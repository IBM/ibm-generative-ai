import contextlib
import datetime
import logging
import threading
import time
import typing
import uuid
from typing import Optional

from fastapi.utils import is_body_allowed_for_status_code
from starlette.responses import Response

from genai._utils.general import cast_list
from genai._utils.responses import BaseErrorResponse, get_api_error_class_by_status_code
from genai.credentials import Credentials
from genai.extensions.localserver.local_base_model import LocalModel
from genai.extensions.localserver.schema import (
    TextGenerationCreateRequest,
    TextTokenizationCreateRequest,
)
from genai.schema import (
    ConcurrencyLimit,
    InternalServerErrorResponse,
    NotFoundResponse,
    TextGenerationCreateResponse,
    TextGenerationLimit,
    TextGenerationLimitRetrieveResponse,
    TextTokenizationCreateResponse,
    UnauthorizedResponse,
)

try:
    import uvicorn
    from fastapi import APIRouter, FastAPI, HTTPException, Request, status
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import (
        BaseHTTPMiddleware,
        DispatchFunction,
        RequestResponseEndpoint,
    )
except ImportError as iex:
    raise ImportError(f"Could not import {iex.name}: Please install ibm-generative-ai[localserver] extension.")  # noqa: B904

logger = logging.getLogger(__name__)


class ApiErrorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, dispatch: typing.Optional[DispatchFunction] = None) -> None:
        super().__init__(app, dispatch)
        app.add_exception_handler(HTTPException, self._handle_exception)

    async def _handle_exception(self, request: Request, exc: Exception):
        detail = str(exc)
        status_code = getattr(exc, "status_code", 500)
        headers = getattr(exc, "headers", None)

        if isinstance(exc, HTTPException):
            detail = exc.detail
            status_code = exc.status_code

        if not is_body_allowed_for_status_code(status_code):
            return Response(status_code=status_code, headers=headers)

        response_body: BaseErrorResponse
        try:
            cls: type[BaseErrorResponse] = get_api_error_class_by_status_code(status_code) or BaseErrorResponse
            response_body = cls.model_validate(
                cls(
                    error=detail,
                    message=detail,
                    status_code=status_code,
                    extensions={},  # type: ignore
                )
                if isinstance(detail, str)
                else cls.model_validate(detail)
            )
        except:  # noqa
            response_body = InternalServerErrorResponse(message=detail, error=detail, extensions={})  # type: ignore

        return JSONResponse(
            status_code=status_code,
            headers=headers,
            content=response_body.model_dump(),
        )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            return await self._handle_exception(request, exc)


class ApiAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, api_key: Optional[str] = None, insecure: bool = False):
        super().__init__(app)
        self.api_key = api_key
        self.insecure = insecure

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers["Authorization"]
        logging.debug(f"Incoming Request: Auth: {auth_header}, Endpoint: {request.url}")
        if self.insecure is False:
            if str(self.api_key) not in auth_header:
                logger.warning(f"A client used an incorrect API Key: {auth_header}")
                response_obj = UnauthorizedResponse(
                    error="Unauthorized",
                    message="API key not found",
                    extensions={},  # type: ignore
                )
                logger.debug(response_obj.model_dump())
                return JSONResponse(
                    content=response_obj.model_dump(),
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
        logging.debug("Calling next in chain")
        response = await call_next(request)
        logging.debug("Returning response")
        return response


class LocalLLMServer:
    def __init__(
        self,
        models: list[type[LocalModel]],
        port: int = 8080,
        interface: str = "0.0.0.0",
        api_key: Optional[str] = None,
        insecure_api: bool = False,
    ):
        self.models = {model.model_id: model() for model in models}
        self.port = port
        self.interface = interface
        self.insecure_api = insecure_api

        # Set the API Key
        self.api_key: str = api_key or "test" if insecure_api else str(uuid.uuid4())

        self.app = FastAPI(
            title="IBM Generative AI Local Model Server",
            debug=False,
            openapi_url=None,
            docs_url=None,
            redoc_url=None,
        )

        self.app.add_middleware(ApiErrorMiddleware)
        self.router = APIRouter()
        self.router.add_api_route("/v2/text/tokenization", self._route_text_tokenization, methods=["POST"])
        self.router.add_api_route("/v2/text/generation", self._route_text_generation, methods=["POST"])
        self.router.add_api_route("/v2/text/generation/limits", self._route_generation_limits, methods=["GET"])
        self.app.include_router(self.router)
        self.app.add_middleware(ApiAuthMiddleware, api_key=self.api_key, insecure=insecure_api)

        self.uvicorn_config = uvicorn.Config(self.app, host=interface, port=port, log_level="error", access_log=False)
        self.uvicorn_server = uvicorn.Server(self.uvicorn_config)
        self.endpoint = f"http://{self.interface}:{self.port}"
        logger.debug(f"{__name__}: API: {self.endpoint}, Insecure: {insecure_api}")

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
        self.uvicorn_server.should_exit = True
        while not self.uvicorn_server.started:
            time.sleep(1e-3)

    def _get_model(self, model_id) -> LocalModel:
        model = self.models.get(model_id)
        if not model:
            raise HTTPException(
                status_code=404,
                detail=NotFoundResponse(
                    message="Model not found",
                    error="Not Found",
                    extensions={"state": {"model_id": model_id}},  # type: ignore
                ).model_dump(),
            )
        return model

    async def _route_text_tokenization(self, body: TextTokenizationCreateRequest) -> TextTokenizationCreateResponse:
        logger.info(f"Tokenize called: {body}")

        model = self._get_model(body.model_id)
        results = [model.tokenize(input_text=input, parameters=body.parameters) for input in cast_list(body.input)]

        return TextTokenizationCreateResponse(
            model_id=body.model_id,
            created_at=datetime.datetime.now().isoformat(),
            results=results,
        )

    async def _route_text_generation(self, body: TextGenerationCreateRequest) -> TextGenerationCreateResponse:
        logger.info(f"Text Generation Called: Model: {body.model_id}, Input: {body.input}")

        model = self._get_model(body.model_id)
        results = [model.generate(input_text=input, parameters=body.parameters) for input in cast_list(body.input)]
        return TextGenerationCreateResponse(
            id=str(uuid.uuid4()),
            model_id=body.model_id,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            results=results,
        )

    async def _route_generation_limits(self):
        logger.info("Generate Limits Called")
        response = TextGenerationLimitRetrieveResponse(
            result=TextGenerationLimit(concurrency=ConcurrencyLimit(limit=100, remaining=100))
        )
        return response
