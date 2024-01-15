from typing import Annotated, Callable, Optional, TypeVar

from pydantic import Field

__all__ = ["CommonExecutionOptions"]


T = TypeVar("T")


class CommonExecutionOptions:
    __slots__ = ()

    throw_on_error = Annotated[
        bool,
        Field(
            description="Flag indicating whether to throw an error if any error occurs during execution (if disabled, "
            "'None' may be returned in case of error).",
        ),
    ]
    ordered = Annotated[
        bool,
        Field(
            description="Items will be yielded in the order they were passed in, although "
            "they may be processed on the server in different order.",
        ),
    ]
    concurrency_limit = Annotated[
        Optional[int],
        Field(
            description="Upper bound for concurrent executions (in case the passed value is higher than "
            "the API allows, the API's limit will be used).",
            ge=1,
        ),
    ]
    batch_size = Annotated[
        Optional[int],
        Field(
            description="Upper limit for size of single batch of prompts "
            "(the size can be actually lower in case the payload is large enough).",
        ),
    ]
    rate_limit_options = Annotated[
        Optional[dict],
        Field(
            description="HTTPX Transport Options to limit number of requests per second.",
        ),
    ]
    callback = Annotated[
        Optional[Callable[[T], None]],
        Field(description="Callback which is called everytime the response comes."),
    ]
