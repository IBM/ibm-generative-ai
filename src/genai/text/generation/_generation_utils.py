import json
import logging
from typing import Generator, Optional, Type, TypeVar

from pydantic import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


def generation_stream_handler(
    generator: Generator[Optional[str], None, None], *, logger: logging.Logger, ResponseModel: Type[TModel]
) -> Generator[TModel, None, None]:
    for response in generator:
        if not response:
            continue

        try:
            parsed_response: dict = json.loads(response)
            yield ResponseModel(**parsed_response)
        except Exception as err:
            logger.error("Could not parse {} as json".format(response))
            raise err
