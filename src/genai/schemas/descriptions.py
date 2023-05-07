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
    RANDOM_SEED = (
        "Manually passed seed to initialize the randomization for experimental repeatability. The range is 1 to 9999."
    )
    STOP_SQUENCES = "Stop sequences are one or more strings which will cause the text generation to stop if/when they are produced as part of the output. Stop sequences encountered prior to the minimum number of tokens being generated will be ignored."
    STREAM = "Enables to stream partial progress as server-sent events. Defaults to false."
    TEMPERATURE = "The value used to module the next token probabilities. The range is 0.00 to 2.00, a value set to 0.00 would make it deterministic."
    TIME_LIMIT = "Time limit in milliseconds - if not completed within this time, generation will stop. The text generated so far will be returned along with the TIME_LIMIT stop reason."
    TOP_K = (
        "The number of highest probability vocabulary tokens to keep for top-k-filtering. The range is any value >= 1."
    )
    TOP_P = "If set to value < 1, only the most probable tokens with probabilities that add up to top_p or higher are kept for generation. The range is 0.00 to 1.00."
    REPETITION_PENALTY = "The parameter for repetition penalty. 1.0 means no penalty."
    TRUNCATE_INPUT_TOKENS = "Truncate to this many input tokens. Can be used to avoid requests failing due to input being longer than configured limits. Zero means don't truncate."

    # Params.Token
    RETURN_TOKEN = "Return tokens with the response. Defaults to false."

    # Params.History
    LIMIT = "Specifies the maximum number of items in the collection that should be returned. Defaults to 100. Maximum is 100."
    OFFSET = "Specifies the starting position in the collection. Defaults to 0."
    STATUS = "Filters the items to be returned based on their status. Possible values are SUCCESS and ERROR."
    ORIGIN = "Filters the items to be returned based on their origin. Possible values are API and UI."
