class SimpleResponse:
    @staticmethod
    def generate(**kwargs):
        SimpleResponse._check_for_errors("generate", **kwargs)

        response = {}
        response["id"] = "1cf9f510-5549-4ea5-a909-2cf9219c1bb5"
        response["model_id"] = kwargs["model"]
        response["created_at"] = "2023-03-15T18:28:12.007Z"
        response["results"] = [
            {
                "input_text": input,
                "generated_text": input,
                "generated_token_count": len(input.split(" ")),
                "input_token_count": len(input.split(" ")),
                "stop_reason": "MAX_TOKENS",
            }
            for input in kwargs["inputs"]
        ]

        return response

    @staticmethod
    def generate_stream(**kwargs):
        SimpleResponse._check_for_errors("generate", **kwargs)

        responses = []
        for idx, token in enumerate("This is the output text.".split(" ")):
            response = {
                "id": "1cf9f510-5549-4ea5-a909-2cf9219c1bb5",
                "model_id": kwargs["model"],
                "created_at": "2023-03-15T18:28:12.007Z",
                "results": [
                    {
                        "generated_text": token,
                        "generated_token_count": idx + 1,
                        "stop_reason": "MAX_TOKENS",
                    }
                ],
            }
            responses.append(response)

        return responses

    @staticmethod
    def generate_response_array_async(**kwargs):
        arr = []
        for i in range(len(kwargs["inputs"])):
            response = {}
            response["id"] = "1cf9f510-5549-4ea5-a909-2cf9219c1bb5"
            response["model_id"] = kwargs["model"]
            response["created_at"] = "2023-03-15T18:28:12.007Z"
            response["results"] = [
                {
                    "input_text": kwargs["inputs"][i],
                    "generated_text": " are stronger.",
                    "generated_token_count": 3,
                    "input_token_count": len(kwargs["inputs"][i].split(" ")),
                    "stop_reason": "MAX_TOKENS",
                }
            ]
            arr.append(response)
        return arr

    @staticmethod
    def tokenize(**kwargs):
        response = {}
        response["model_id"] = kwargs["model"]
        response["created_at"] = "2023-03-15T18:28:12.007Z"

        if "params" in kwargs and kwargs["params"].return_tokens is True:
            response["results"] = [
                {
                    "input_text": kwargs["inputs"][i],
                    "token_count": len(kwargs["inputs"][i].split(" ")),
                    "tokens": kwargs["inputs"][i].split(" "),
                }
                for i in range(len(kwargs["inputs"]))
            ]
        else:
            response["results"] = [
                {
                    "input_text": kwargs["inputs"][i],
                    "token_count": len(kwargs["inputs"][i].split(" ")),
                }
                for i in range(len(kwargs["inputs"]))
            ]

        return response

    @staticmethod
    def tokenize_response_array_async(**kwargs):
        arr = []
        num_inputs, batch_size = len(kwargs["inputs"]), 5
        num_batches = num_inputs // batch_size + (num_inputs % batch_size > 0)
        for i in range(num_batches):
            response = {}
            response["model_id"] = kwargs["model"]
            response["created_at"] = "2023-03-15T18:28:12.007Z"

            if "params" in kwargs and kwargs["params"].return_tokens is True:
                response["results"] = [
                    {
                        "input_text": kwargs["inputs"][i],
                        "token_count": len(kwargs["inputs"][i].split(" ")),
                        "tokens": kwargs["inputs"][i].split(" "),
                    }
                    for i in range(i * batch_size, min((i + 1) * batch_size, num_inputs))
                ]
            else:
                response["results"] = [
                    {
                        "input_text": kwargs["inputs"][i],
                        "token_count": len(kwargs["inputs"][i].split(" ")),
                    }
                    for i in range(i * batch_size, min((i + 1) * batch_size, num_inputs))
                ]
            arr.append(response)
        return arr

    @staticmethod
    def history(**kwargs):
        response = {
            "results": [
                {
                    "id": "some-id",
                    "duration": 431,
                    "request": {
                        "inputs": ["Write a tagline for an alumni association: Together we"],
                        "model_id": "google/ul2",
                        "parameters": {},
                    },
                    "status": "SUCCESS",
                    "created_at": "2022-12-19T22:53:22.000Z",
                    "response": SimpleResponse.generate(model="google/ul2", inputs=["some input"]),
                }
            ],
            "totalCount": 62,
        }
        return response

    @staticmethod
    def terms_of_use(**kwargs):
        response = {
            "results": {
                "tou_accepted": True,
                "tou_accepted_at": "2022-12-12T18:51:53.000Z",
                "firstName": "Thomas",
                "lastName": "Watson",
                "data_usage_consent": True,
                "generate_default": None,
            }
        }
        return response

    @staticmethod
    def error(status_code, error, message, extensions=None):
        err = {"status_code": status_code, "error": error, "message": message}

        if extensions is not None:
            err["extensions"] = extensions

        return err

    @staticmethod
    def _check_for_errors(func, **kwargs):
        if func == "generate":
            if "model" not in kwargs:
                return SimpleResponse.error(
                    404,
                    "Not found",
                    "Model not found",
                    {"code": "NOT_FOUND", "state": {}},
                )

            if "inputs" not in kwargs:
                return SimpleResponse.error(
                    400,
                    "Bad Request",
                    " must have required property 'inputs'",
                    {
                        "code": "INVALID_INPUT",
                        "state": [
                            {
                                "instancePath": "",
                                "params": {"missingProperty": "inputs"},
                            }
                        ],
                    },
                )

    @staticmethod
    def prompt_template(template, name):
        response = {
            "results": {
                "id": "5XU9Zv6mrG6KIACN",
                "name": name,
                "value": template,
                "created_at": "2023-05-08T11:51:18.000Z",
            }
        }
        return response

    @staticmethod
    def files(**kwargs):
        response = {}
        results = {
            "id": "dumb-id",
            "bytes": "931652",
            "file_name": "file_to_tune.json",
            "purpose": "tune",
            "storage_provider_location": "us-east",
            "created_at": "2023-05-17T14:55:06.000Z",
            "file_formats": [
                {
                    "id": "1",
                    "name": "generation",
                },
            ],
        }

        if "multipart_form_data" in kwargs:
            response = {"results": results}
        elif "file_id" in kwargs:
            response = {"results": results}
        elif "params" in kwargs:
            response = {
                "results": [results, results],
                "totalCount": 2,
            }
        else:
            response = {
                "results": [results],
                "totalCount": 1,
            }
        return response

    @staticmethod
    def tunes(**kwargs):
        from genai.schemas.tunes_params import CreateTuneParams

        response = {}
        results = {
            "id": "google/flan-t5-xxl-mpt-Bok9gSo3-2023-04-11-18-00-57",
            "name": "Tune #2 google/flan-t5-xxl (3B)",
            "model_id": "google/google/flan-t5-xxl",
            "model_name": "google/flan-t5-xxl (3B)",
            "status": "COMPLETED",
            "task_id": "generation",
            "parameters": {"batch_size": 4, "num_epochs": 12},
            "created_at": "2023-04-11T18:00:57.000Z",
        }

        if "tune_id" in kwargs:
            response["results"] = results
        elif "params" in kwargs and type(kwargs["params"]) == CreateTuneParams:
            response["results"] = results
        else:
            response = {
                "results": [results],
                "totalCount": 1,
            }
        return response

    @staticmethod
    def get_tune(**kwargs):
        response = {
            "results": {
                "id": "google/flan-t5-xl-mpt-oP8G21Dj-2023-04-11-18-11-54",
                "name": "Tune #1 google/flan-t5-xl (3B)",
                "model_id": "google/google/flan-t5-xl",
                "method_id": "mpt",
                "model_name": "google/flan-t5-xl (3B)",
                "status_message": "",
                "task_id": "generation",
                "status": "COMPLETED",
                "parameters": {"batch_size": 4, "num_epochs": 12},
                "created_at": "2023-04-11T18:11:54.000Z",
                "validation_files": [],
                "training_files": [
                    {
                        "id": "60d54ad5-b9d7-4acb-99d6-870ff31c9222",
                        "file_name": "file.json",
                        "created_at": "2023-04-24 10:26:02+02",
                    }
                ],
                "evaluation_files": [],
                "datapoints": {
                    "loss": [
                        {
                            "data": {"epoch": 0, "value": 1.9922},
                            "timestamp": "2023-05-07T09:05:56.000Z",
                        }
                    ]
                },
            }
        }

        return response

    @staticmethod
    def models(**kwargs):
        return {
            "results": [
                {
                    "id": "google/flan-t5-xl",
                    "name": "flan-t5-xl (3B)",
                    "size": "3B",
                    "source_model_id": None,
                    "token_limit": 4096,
                },
                {
                    "id": "flan-t5-xl-mpt-XmHNkJWk-2023-07-18-17-00-34",
                    "name": "flan-t5-xxl (11B)",
                    "size": "11B",
                    "source_model_id": "google/flan-t5-xl",
                    "token_limit": 4096,
                },
            ]
        }

    @staticmethod
    def create_tune(**kwargs):
        model_id = kwargs["model_id"] if "model_id" in kwargs else "google/flan-t5-xxl"
        name = kwargs["name"] if "name" in kwargs else "Tune #2 google/flan-t5-xxl (3B)"
        response = {
            "results": {
                "id": "google/flan-t5-xxl-mpt-Bok9gSo3-2023-04-11-18-00-57",
                "name": name,
                "model_id": model_id,
                "model_name": "google/flan-t5-xxl (3B)",
                "status": "COMPLETED",
                "task_id": "generation",
                "parameters": {"batch_size": 4, "num_epochs": 12},
                "created_at": "2023-04-11T18:00:57.000Z",
            }
        }
        return response

    @staticmethod
    def get_tune_methods():
        response = {
            "results": [
                {"id": "pt", "name": "Prompt tuning"},
                {"id": "mpt", "name": "Multitask prompt tuning"},
            ]
        }
        return response
