import contextlib
import datetime
import logging
import threading
import time
import uuid

try:
    import uvicorn
    from fastapi import APIRouter, FastAPI, Request, status
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import BaseHTTPMiddleware
except ImportError as iex:
    raise ImportError(f"Could not import {iex.name}: Please install ibm-generative-ai[localserver] extension.")


from genai import Credentials
from genai.extensions.localserver.custom_model_interface import CustomModel
from genai.extensions.localserver.schemas import (
    GenerateRequestBody,
    TokenizeRequestBody,
)
from genai.schemas.responses import ErrorResponse, GenerateResponse, TokenizeResponse

logger = logging.getLogger(__name__)


class ApiAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str = None, insecure: bool = False):
        super().__init__(app)
        self.api_key = api_key
        self.insecure = insecure

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers["Authorization"]
        logging.debug(f"Incoming Request: Auth: {auth_header}, Endpoint: {request.url}")
        if self.insecure is False:
            if str(self.api_key) not in auth_header:
                logger.warning(f"A client used an incorrect API Key: {auth_header}")
                response_obj = ErrorResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    error="Unauthorized",
                    message="API key not found",
                )
                logger.debug(response_obj.dict())
                return JSONResponse(content=response_obj.dict(), status_code=status.HTTP_401_UNAUTHORIZED)
        logging.debug("Calling next in chain")
        response = await call_next(request)
        logging.debug("Returning response")
        return response


class LocalLLMServer:
    def __init__(
        self,
        models: list[CustomModel],
        port: int = 8080,
        interface: str = "0.0.0.0",
        api_key: str = None,
        insecure_api: bool = False,
    ):
        self.models = {model.model_id: model() for model in models}
        self.port = port
        self.interface = interface
        self.insecure_api = insecure_api

        # Set the API Key
        if api_key is None and insecure_api is False:
            self.api_key = uuid.uuid4()
        elif api_key is None and insecure_api is True:
            self.api_key = "test"

        self.app = FastAPI(
            title="IBM Generative AI Local Model Server",
            debug=False,
            openapi_url=False,
            docs_url=False,
            redoc_url=None,
        )
        self.router = APIRouter()
        self.router.add_api_route("/v1/tokenize", self._route_tokenize, methods=["POST"])
        self.router.add_api_route("/v1/generate", self._route_generate, methods=["POST"])
        self.app.include_router(self.router)
        self.app.add_middleware(ApiAuthMiddleware, api_key=self.api_key, insecure=insecure_api)

        self.uvicorn_config = uvicorn.Config(self.app, host=interface, port=port, log_level="error", access_log=False)
        self.uvicorn_server = uvicorn.Server(self.uvicorn_config)
        self.endpoint = f"http://{self.interface}:{self.port}/v1"
        logger.debug(f"{__name__}: Models: {list(self.models.keys())}, API: {self.endpoint}, Insecure: {insecure_api}")

    @contextlib.contextmanager
    def run_locally(self):
        thread = threading.Thread(target=self.start_server)
        thread.start()
        try:
            while not self.uvicorn_server.started:
                time.sleep(1e-3)
            yield
        finally:
            self.uvicorn_server.should_exit = True
            thread.join()

    def get_credentials(self):
        return Credentials(api_key=self.api_key, api_endpoint=self.endpoint)

    def start_server(self):
        logger.debug("Starting server background process")

        logger.info(f"Credentials: Endpoint: {self.endpoint} API Key: {self.api_key}")
        logger.info(
            f"In Python Script: credentials = Credentials(api_key={self.api_key}, api_endpoint={self.endpoint})"
        )
        self.uvicorn_server.run()

    def stop_server(self):
        logger.debug("Stopping server background process")
        self.uvicorn_server.shutdown()

    async def _route_tokenize(self, tokenize_request: TokenizeRequestBody):
        logger.info(f"Tokenize called: {tokenize_request}")

        results = [
            self.models[tokenize_request.model_id].tokenize(input_text=input, params=tokenize_request.parameters)
            for input in tokenize_request.inputs
        ]

        created_at = datetime.datetime.now().isoformat()
        response = TokenizeResponse(model_id=tokenize_request.model_id, created_at=created_at, results=results)

        return response

    async def _route_generate(self, generate_request: GenerateRequestBody):
        logger.info(f"Generate Called: Model: {generate_request.model_id}: {generate_request.inputs}")
        results = [
            self.models[generate_request.model_id].generate(input_text=input, params=generate_request.parameters)
            for input in generate_request.inputs
        ]
        created_at = datetime.datetime.now().isoformat()
        response = GenerateResponse(model_id=generate_request.model_id, created_at=created_at, results=results)
        return response
