from enum import Enum


class ModelType(str, Enum):
    FLAN_T5_11B = "google/flan-t5-xxl" 
    FLAN_UL2 = "google/flan-ul2" 
    FLAN_UL2_20B = "google/flan-ul2" 
    GPT_NEOX_20B = "eleutherai/gpt-neox-20b" 
    MT0_13B = "bigscience/mt0-xxl" 
