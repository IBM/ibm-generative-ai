from genai.exceptions import GenAiException

__all__ = ["to_genai_error"]


def to_genai_error(e: Exception) -> GenAiException:
    if isinstance(e, GenAiException):
        return e

    return GenAiException(e)
