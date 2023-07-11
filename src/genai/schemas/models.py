import warnings
from enum import Enum

warnings.simplefilter("always", DeprecationWarning)
warnings.warn(
    """\x1b[33;20m
The class ModelType is being deprecated.
Please replace any reference to ModelType by its model id string equivalent.
Example :
  ModelType.FLAN_T5 becomes "google/flan-t5-xxl"\x1b[0m
""",
    DeprecationWarning,
    stacklevel=2,
)


class ModelType(str, Enum):
    CODEGEN_MONO_16B = "salesforce/codegen-16b-mono"
    DIAL_FLAN_T5 = "prakharz/dial-flant5-xl"
    DIAL_FLAN_T5_3B = "prakharz/dial-flant5-xl"
    FLAN_T5 = "google/flan-t5-xxl"
    FLAN_T5_11B = "google/flan-t5-xxl"
    FLAN_T5_3B = "google/flan-t5-xl"
    FLAN_UL2 = "google/flan-ul2"
    FLAN_UL2_20B = "google/flan-ul2"
    GPT_JT_6B_V1 = "togethercomputer/gpt-jt-6b-v1"
    GPT_NEOX_20B = "eleutherai/gpt-neox-20b"
    MT0 = "bigscience/mt0-xxl"
    MT0_13B = "bigscience/mt0-xxl"
    UL2 = "google/ul2"
    UL2_20B = "google/ul2"
