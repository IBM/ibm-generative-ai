from typing import Callable, TypeVar

from pydantic import BaseModel, ConfigDict, field_serializer

from genai.schema._endpoints import ApiEndpoint

__all__ = ["set_service_action_metadata", "get_service_action_metadata", "inherit_metadata"]


class ServiceActionMetadata(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
    )

    endpoint: type[ApiEndpoint]

    @field_serializer("endpoint")
    def serialize_endpoint(self, dt: type[ApiEndpoint], _info):
        return {k: v for k, v in vars(dt).items() if not k.startswith("__")}


_METADATA_KEY = "_metadata"

T = TypeVar("T", bound=Callable)


def inherit_metadata(*, source: Callable, target: Callable) -> None:
    source_meta = getattr(source, _METADATA_KEY, None)
    target_meta = getattr(target, _METADATA_KEY, None)

    if source_meta is not None and target_meta is None:
        setattr(target, _METADATA_KEY, source_meta)


def set_service_action_metadata(*, endpoint: type[ApiEndpoint]):
    def decorator(fn: T) -> T:
        setattr(fn, _METADATA_KEY, ServiceActionMetadata(endpoint=endpoint))
        return fn

    return decorator


def get_service_action_metadata(service_method: Callable) -> ServiceActionMetadata:
    """
    Retrieve metadata for arbitrary service's method.
    For instance which endpoint is being used.

    Example::

        from genai import Credentials, Client
        from genai.utils import get_service_action_metadata

        credentials = Credentials.from_env()
        client = Client(credentials=credentials)

        metadata = get_service_action_metadata(client.text.tokenization.create)
    """

    metadata = getattr(service_method, _METADATA_KEY, None)
    if not isinstance(metadata, ServiceActionMetadata):
        raise ValueError("Provided callable does not have any metadata.")

    return metadata
