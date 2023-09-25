# flake8: noqa


class Descriptions:
    # LengthPenalty
    DECAY_FACTOR = "Represents the factor of exponential decay and must be > 1.0. Larger values correspond to more aggressive decay."
    START_INDEX = "A number of generated tokens after which this should take effect."

    # Return
    RETURN = "key-value pairs."
    INPUT_TEXT = "Include input text."
    GENERATED_TOKEN = "Include list of individual generated tokens. 'Extra' token information is included based on the other flags below."
    INPUT_TOKEN = "Include list of input tokens. 'Extra' token information is included based on the other flags here, but only for decoder-only models."
    TOKEN_LOGPROBS = "Include logprob for each returned token. Applicable only if generated_tokens == true and/or input_tokens == true."
    TOKEN_RANKS = (
        "Include rank of each returned token. Applicable only if generated_tokens == true and/or input_tokens == true."
    )
    TOP_N_TOKENS = "Include top n candidate tokens at the position of each returned token. The maximum value permitted is 5, but more may be returned if there is a tie for nth place. Applicable only if generated_tokens == true and/or input_tokens == true."

    # Params.Generate
    DECODING_METHOD = (
        "Decoding method used for generation. Options are greedy or sample. Defaults to sample if not specified."
    )
    LENGTH_PENALTY = "It can be used to exponentially increase the likelihood of the text generation terminating once a specified number of tokens have been generated."
    MAX_NEW_TOKEN = "The maximum number of new tokens to be generated. The range is 1 to 1024, defaults to 20."
    MIN_NEW_TOKEN = "If stop sequences are given, they are ignored until minimum tokens are generated."
    RANDOM_SEED = "Manually passed seed to initialize the randomization for experimental repeatability. The range is 1 to 9999. Valid only with decoding_method=sample."
    STOP_SQUENCES = "Stop sequences are one or more strings which will cause the text generation to stop if/when they are produced as part of the output. Stop sequences encountered prior to the minimum number of tokens being generated will be ignored."
    STREAM = "Enables to stream partial progress as server-sent events. Defaults to false."
    TEMPERATURE = "The value used to module the next token probabilities. The range is 0.05 to 2.00, a value set to 0.05 would make it deterministic. Valid only with decoding_method=sample."
    TIME_LIMIT = "Time limit in milliseconds - if not completed within this time, generation will stop. The text generated so far will be returned along with the TIME_LIMIT stop reason."
    TOP_K = "The number of highest probability vocabulary tokens to keep for top-k-filtering. The range is any value >= 1. Valid only with decoding_method=sample."
    TOP_P = "If set to value < 1, only the most probable tokens with probabilities that add up to top_p or higher are kept for generation. The range is 0.00 to 1.00. Valid only with decoding_method=sample."
    TYPICAL_P = "Local typicality measures how similar the conditional probability of predicting a target token next is to the expected conditional probability of predicting a random token next, given the partial text already generated. If set to float < 1, the smallest set of the most locally typical tokens with probabilities that add up to typical_p or higher are kept for generation."
    REPETITION_PENALTY = "The parameter for repetition penalty. 1.0 means no penalty."
    TRUNCATE_INPUT_TOKENS = "Truncate to this many input tokens. Can be used to avoid requests failing due to input being longer than configured limits. Zero means don't truncate."
    BEAM_WIDTH = "Multiple output sequences of tokens are generated, using your decoding selection, and then the output sequence with the highest overall probability is returned. When beam search is enabled, there will be a performance penalty, and Stop sequences will not be available."  # noqa

    # Params.Token
    RETURN_TOKEN = "Return tokens with the response. Defaults to false."

    # Params.History
    LIMIT = "Specifies the maximum number of items in the collection that should be returned. Defaults to 100. Maximum is 100."
    OFFSET = "Specifies the starting position in the collection. Defaults to 0."
    STATUS = "Filters the items to be returned based on their status. Possible values are SUCCESS and ERROR."
    ORIGIN = "Filters the items to be returned based on their origin. Possible values are API and UI."

    # Params.Moderations
    MODERATIONS = "Leverages various models to detect hate speech in the provided inputs and generated outputs."
    HAP = "Mechanism for detecting hate/abuse/profanity on a sentence level."
    HAP_INPUT = "Enable/Disable HAP detection on the provided input."
    HAP_OUTPUT = "Enable/Disable HAP detection on the generated output."
    HAP_THRESHOLD = "The number from interval <0, 1> that causes the sentence to be flagged (default is 0.75)."


class TunesAPIDescriptions:
    # Params.CreateTune
    NAME = "Name of the tune."
    SEARCH = "Filters the items to be returned based on their name."
    MODEL_ID = "The ID of the model to be used for this request."
    METHOD_ID = "The ID of the tuning method to be used for this request."
    TASK_ID = "Task ID that determines format of the training data. Possible values are generic, classification, or summarization."
    TRAINING_FILE_IDS = "The IDs of uploaded files that contain training data."
    VALIDATION_FILE_IDS = "The IDs of uploaded files that contain validation data."
    PARAMETERS = "key-value pairs"
    ACCUMULATE_STEPS = "Number of training steps to use to combine gradients. This helps overcome the limitation of smaller batch sizes due to GPU memory limitations. The range is 1 to 128, defaults to 16."
    BATCH_SIZE = "The number of samples to work through before updating the internal model parameters. Optimal batch size set points are based on a combination of the number of examples you’ve uploaded as well as other parameters. If you’ve uploaded a smaller training data set, you should set your batch size lower. The range is 1 to 16, defaults to 16."
    LEARNING_RATE = "Learning rate to be used while tuning prompt vectors. The range is 0.01 to 0.5, defaults to 0.3."
    MAX_INPUT_TOKENS = "The maximum number of tokens that are accepted in the input field for each example. If any of the input rows in your training data set exceed this value, the input data will be truncated at the set maximum value. The range is 1 to 256, defaults to 256."
    MAX_OUTPUT_TOKENS = "The maximum number of tokens that are accepted in the output field for each example. If any of the output rows in your training data set exceed this value, the output data will be truncated at the set maximum value. The range is 1 to 128, defaults to 128."
    NUM_EPOCHS = "The number of times to cycle through the training data set. If you have a large training data set, a high number of epochs will take a very long time to finish tuning. The range is 1 to 50, defaults to 20."
    NUM_VIRTUAL_TOKENS = "Number of virtual tokens to be used for training. This is purely experimental. If the default value doesn’t provide good results, you may want to try selecting another value. Possible values are 20, 50, or 100, defaults to 100."
    VERBALIZER = "Verbalizer template to be used for formatting data at train and inference time. This template may use double brackets to indicate where fields from training data should be rendered. The template can contain one or both of {{input}} and {{output}}. Defaults to {{input}}."
    OFFSET = "Specifies the starting position in the collection. Defaults to 0."
    LIMIT = "Specifies the maximum number of items in the collection that should be returned. Defaults to 100. Maximum is 100."
    SEARCH = "Filters the items to be returned based on their name."
    STATUS = "Filters the items to be returned based on their status. Possible values are: INITIALIZING, NOT_STARTED, PENDING, HALTED, RUNNING, QUEUED, COMPLETED, FAILED."
    INIT_METHOD = "Initialization method to be used. Possible values are RANDOM or TEXT. Defaults to RANDOM. Used only if the method_id is 'pt' = Prompt Tuning."
    INIT_TEXT = "Initialization text to be used. This is only applicable if init_method == TEXT. Used only if the method_id is 'pt' = Prompt Tuning."
    ID = "The ID of the tune."
    CONTENT = "The name of the asset. Available options are encoder and logs."


class FilesAPIDescriptions:
    OFFSET = "Specifies the starting position in the collection. Defaults to 0."  # noqa
    LIMIT = "Specifies the maximum number of items in the collection that should be returned. Defaults to 100. Maximum is 100."  # noqa
    SEARCH = "Filters the items to be returned based on their name."
    PURPOSE = "The intended purpose of the uploaded document. Currently only tune or template are supported."  # noqa
    TASK_ID = "Task ID that determins format of the training data. Possible values are generation, classification, or summarization. This field is required if purpose == 'tune'."  # noqa
    FILE = "The file to be uploaded."
