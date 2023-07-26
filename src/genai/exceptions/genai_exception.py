import logging
from typing import Union

from httpx import Response
from pydantic import ValidationError

from genai.schemas.responses import ErrorResponse

logger = logging.getLogger(__name__)


class GenAiException(Exception):
    def __init__(self, error: Union[Exception, Response]) -> None:
        if isinstance(error, Response):
            try:
                self.error = ErrorResponse(**error.json())
                self.error_message = self.error.message
            except ValidationError:
                self.error = error
                self.error_message = str(error.content)
        else:
            self.error = error
            self.error_message = str(error)
        logger.error(self.error_message)
        super().__init__(self.error_message)
