from typing import Optional

from pydantic import BaseModel, Extra, Field

# TODO: Update the descriptions import
from genai.schemas.descriptions import TunesAPIDescriptions as tx


class TunesListParams(BaseModel):
    """Class to hold the parameters for listing tunes."""

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.forbid

    limit: Optional[int] = Field(None, description=tx.LIMIT, le=100)
    offset: Optional[int] = Field(None, description=tx.OFFSET)
    status: Optional[str] = Field(None, description=tx.STATUS)
    search: Optional[str] = Field(None, description=tx.SEARCH)


class CreateTuneHyperParams(BaseModel):
    """Class to hold the hyperparameters for creating tunes."""

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.allow

    accumulate_steps: Optional[int] = Field(16, description=tx.ACCUMULATE_STEPS)
    batch_size: Optional[int] = Field(16, description=tx.BATCH_SIZE)
    learning_rate: Optional[float] = Field(0.3, description=tx.LEARNING_RATE)
    max_input_tokens: Optional[int] = Field(256, description=tx.MAX_INPUT_TOKENS)
    max_output_tokens: Optional[int] = Field(128, description=tx.MAX_OUTPUT_TOKENS)
    num_epochs: Optional[int] = Field(20, description=tx.NUM_EPOCHS)
    num_virtual_tokens: Optional[int] = Field(100, description=tx.NUM_VIRTUAL_TOKENS)
    verbalizer: Optional[str] = Field("Input: {{input}} Output:", description=tx.VERBALIZER)
    init_method: Optional[str] = Field(None, description=tx.INIT_METHOD)
    init_text: Optional[str] = Field(None, description=tx.INIT_TEXT)


class CreateTuneParams(BaseModel):
    """Class to hold the parameters for creating tunes."""

    class Config:
        anystr_strip_whitespace = True
        extra = Extra.allow

    name: str = Field(None, description=tx.NAME)
    model_id: str = Field(None, description=tx.MODEL_ID)
    method_id: str = Field(None, description=tx.METHOD_ID)
    task_id: str = Field(None, description=tx.TASK_ID)
    training_file_ids: list[str] = Field(None, description=tx.TRAINING_FILE_IDS)
    validation_file_ids: Optional[list[str]] = Field(None, description=tx.VALIDATION_FILE_IDS)
    parameters: Optional[CreateTuneHyperParams] = Field(None, description=tx.PARAMETERS)


class DownloadAssetsParams(BaseModel):
    """Class to hold the parameters for downloading tune assets."""

    class Config:
        anystr_strip_whitespace = True
        # extra: Extra.forbid

    id: str = Field(None, description=tx.ID)
    content: str = Field(None, description=tx.CONTENT)
