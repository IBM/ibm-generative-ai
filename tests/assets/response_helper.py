class SimpleResponse:
    @staticmethod
    def generate(**kwargs):
        SimpleResponse._check_for_errors("generate", **kwargs)

        response = {}
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
            for i in range(len(kwargs["inputs"]))
        ]

        return response

    @staticmethod
    def generate_response_array_async(**kwargs):
        arr = []
        for i in range(len(kwargs["inputs"])):
            response = {}
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
                {"input_text": kwargs["inputs"][i], "token_count": len(kwargs["inputs"][i].split(" "))}
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
                return SimpleResponse.error(404, "Not found", "Model not found", {"code": "NOT_FOUND", "state": {}})

            if "inputs" not in kwargs:
                return SimpleResponse.error(
                    400,
                    "Bad Request",
                    " must have required property 'inputs'",
                    {"code": "INVALID_INPUT", "state": [{"instancePath": "", "params": {"missingProperty": "inputs"}}]},
                )
