import json
import logging
import time
from typing import Any, Generator, List, Optional, Type, TypeVar, Union

import httpx
from pydantic import BaseModel

from genai.exceptions import GenAiException
from genai.options import Options
from genai.schemas import GenerateParams, TokenParams
from genai.schemas.chat import BaseMessage
from genai.schemas.generate_params import ChatOptions
from genai.services import ServiceInterface
from genai.services.connection_manager import ConnectionManager
from genai.utils.errors import to_genai_error
from genai.utils.general import to_model_instance

Params = Union[GenerateParams, TokenParams, Any]


T = TypeVar("T", bound=BaseModel)


def generation_stream_handler(
    generator: Generator[Optional[str], None, None], *, logger: logging.Logger, ResponseModel: Type[T]
) -> Generator[T, None, None]:
    for response in generator:
        if not response:
            continue

        try:
            parsed_response: dict = json.loads(response)
            yield ResponseModel(**parsed_response)
        except Exception as err:
            logger.error("Could not parse {} as json".format(response))
            raise to_genai_error(err)


def create_chat_handler(service: ServiceInterface, *, model_id: str, params: Optional[Params] = None):
    def chat_handler(
        messages: List[BaseMessage],
        *,
        options: Optional[ChatOptions],
        streaming: bool = False,
        **kwargs,
    ):
        options = to_model_instance(options, ChatOptions)
        if not options.use_conversation_parameters:
            options.use_conversation_parameters = None

        request_options = Options(
            **options.model_dump(exclude_none=True),
            **kwargs,
        )

        request_params = to_model_instance(params, GenerateParams)
        request_params.stream = streaming

        def execute(attempt=0):
            response = service.chat(
                model=model_id,
                messages=messages,
                params=request_params if not options.use_conversation_parameters else None,
                options=request_options,
                streaming=streaming,
            )
            if streaming or response.is_success:
                return response
            elif response.status_code == httpx.codes.TOO_MANY_REQUESTS and attempt < ConnectionManager.MAX_RETRIES_CHAT:
                time.sleep(2 ** (attempt + 1))
                return execute(attempt + 1)
            else:
                raise GenAiException(response)

        return execute()

    return chat_handler
