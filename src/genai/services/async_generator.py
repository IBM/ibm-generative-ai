import asyncio
import heapq
import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from genai.exceptions import GenAiException
from genai.schemas.responses import GenerateResponse, TokenizeResponse
from genai.services.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

__all__ = ["AsyncResponseGenerator"]


class AsyncResponseGenerator:
    def __init__(self, model_id, prompts, params, service, fn="generate", ordered=False, callback=None):
        """Instantiates the ConcurrentWrapper Interface.

        Args:
            model_id (ModelType): The type of model to use
            prompts (list): List of prompts
            params (GenerateParams): Parameters to use during generate requests
            service (ServiceInterface): The service interface
            fn (Literal["generate", "tokenize"]): Function to call from service
            callback (Callable[[GenerateResult], Any]): callback to execute once a prompt is successfully received.
        """
        self.model_id = model_id
        self.prompts = prompts
        self.params = params
        self.service = service
        self.callback = callback
        self.fn = fn
        self.ordered = ordered

    def __enter__(self):
        self.accumulator = []
        self._initialize_fn_specific_params()
        self.queue_ = Queue()
        self.loop_ = asyncio.new_event_loop()
        return self

    def _shutdown(self):
        pending = asyncio.all_tasks(self.loop_)
        for t in pending:
            t.cancel()
        if self.loop_.is_running():
            self.loop_.stop()
        while not self.queue_.empty():
            _ = self.queue_.get()
            self.queue_.task_done()
        self.queue_.join()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._shutdown()
        except Exception as e:
            logger.error(str(e))
            raise GenAiException(e)

    def _initialize_fn_specific_params(self):
        if self.fn == "generate":
            self.batch_size_ = 1
            self.num_batches_ = len(self.prompts)
            self.message_type_ = GenerateResponse
            self.service_fn_ = self.service.async_generate
            ConnectionManager.make_generate_client()
            self.client_close_fn_ = ConnectionManager.delete_generate_client
        elif self.fn == "tokenize":
            self.batch_size_ = 5
            a, b = divmod(len(self.prompts), self.batch_size_)
            self.num_batches_ = a + (b > 0)
            self.message_type_ = TokenizeResponse
            self.service_fn_ = self.service.async_tokenize
            ConnectionManager.make_tokenize_client()
            self.client_close_fn_ = ConnectionManager.delete_tokenize_client

    def _generate_batch(self):
        for i in range(0, len(self.prompts), self.batch_size_):
            yield self.prompts[i : min(i + self.batch_size_, len(self.prompts))]

    def _process_response(self, response, batch_size):
        if response is None:
            for _ in range(batch_size):
                yield None
        else:
            for result in response.results:
                yield result

    async def _get_response_json(self, model, inputs, params):
        try:
            response_raw = await self.service_fn_(model, inputs, params)
            response = response_raw.json()
        except Exception as ex:
            logger.error("Error in _get_response_json {}: {}".format(type(ex), str(ex)))
            response = None
        return response

    async def _task(self, inputs, batch_num):
        response = None
        try:
            response = await self._get_response_json(self.model_id, inputs, self.params)
            logger.debug("Received response = {}".format(response))
            for i in range(len(response["results"])):
                response["results"][i]["input_text"] = inputs[i]
            response = self.message_type_(**response)
            logger.debug("Cast to Response = {}".format(response))
        except Exception as e:
            logger.error(
                "Exception raised async_generate and casting : {}, response = {}, inputs = {}".format(
                    str(e), response, inputs
                )
            )
            self.queue_.put_nowait((batch_num, len(inputs), None))
            return
        try:
            self.queue_.put_nowait((batch_num, len(inputs), response))
            if self.callback is not None:
                for result in response.results:
                    self.callback(result)
        except Exception as e:
            logger.error(
                "Exception raised in callback : {}, response = {}, inputs = {}".format(str(e), response, inputs)
            )

    async def _schedule_requests(self):
        tasks = []
        batch_num = 0
        for batch in self._generate_batch():
            task = asyncio.create_task(self._task(batch, batch_num))
            tasks.append(task)
            batch_num += 1
        await asyncio.gather(*tasks)

    def _request_launcher(self):
        asyncio.set_event_loop(self.loop_)
        self.loop_.run_until_complete(self._schedule_requests())
        self.loop_.run_until_complete(self.client_close_fn_())

    def generate_response(self):  # -> Generator[Union[GenerateResult, TokenizeResult, None]]:
        """Method to spawn a launcher thread to launch requests for generate endpoint
        and yield responses as they get received.

        Yields:
            Generator[Union[GenerateResult, TokenizeResult, None]]: A generator of results
        """
        if len(self.prompts) == 0:
            return
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self._request_launcher)
            counter = 0
            minheap, batch_tracker = [], 0
            while counter < self.num_batches_:
                try:
                    batch_num, batch_size, response = self.queue_.get()
                    self.queue_.task_done()
                except Exception as ex:
                    logger.error("Exception while reading from queue: {}".format(str(ex)))
                    raise ex
                else:
                    counter += 1
                    # FUTURE: Add metadata here as follows if necessary:
                    # if response is not None:
                    #   for i in len(response.results):
                    #     response.results[i].metadata = self.metadata[batch_num * BATCH_SIZE + i]
                    if not self.ordered:
                        for result in self._process_response(response, batch_size):
                            yield result
                        continue
                try:
                    # If we are here then self.ordered is True.
                    heapq.heappush(minheap, (batch_num, batch_size, response))
                    for i in range(len(minheap)):
                        bnum, bsize, resp = heapq.heappop(minheap)
                        if bnum == batch_tracker:
                            for result in self._process_response(resp, bsize):
                                yield result
                            batch_tracker += 1
                        else:
                            heapq.heappush(minheap, (bnum, bsize, resp))
                            break
                except Exception as ex:
                    logger.error("Error in heap processing: {}".format(str(ex)))
                    raise ex
