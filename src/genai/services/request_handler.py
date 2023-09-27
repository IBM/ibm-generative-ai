import asyncio
import logging
from typing import Optional

import httpx
from httpx import Response
from httpx_sse import SSEError, connect_sse

from genai._version import version
from genai.exceptions import GenAiException
from genai.options import Options
from genai.services.connection_manager import ConnectionManager
from genai.utils.http_provider import HttpProvider

logger = logging.getLogger(__name__)

__all__ = ["RequestHandler"]


class RequestHandler:
    @staticmethod
    def _metadata(
        method: str,
        key: str,
        model_id: str = None,
        inputs: list = None,
        parameters: dict = None,
        options: Options = None,
        files: dict = None,
    ):
        """General function to build header and/or json_data for /post and /get requests.

        Args:
            method (str): Request type. Currently accepts GET or POST
            key (str): API key for authorization.
            model_id (str, optional): The id of the language model to be queried. Defaults to None.
            inputs (list, optional): List of inputs to be queried. Defaults to None.
            parameters (dict, optional): Key-value pairs for model parameters. Defaults to None.
            options (Options, optional): Additional parameters to pass in the query payload. Defaults to None.
            files (dict, optional): Pre-built files. Defaults to None.

        Returns:
            tuple: Headers, json_data for request, files
        """

        headers = {
            "Authorization": f"Bearer {key}",
            "x-request-origin": f"python-sdk/{version}",
            "user-agent": f"python-sdk/{version}",
        }

        # NOTE: discuss with team if we want to keep like this or try another approach
        if method == "POST" and files is not None:
            return headers, None, files

        json_data = {}

        if method == "POST" or method == "PUT":
            headers["Content-Type"] = "application/json"

            if model_id is not None:
                json_data["model_id"] = model_id

            if inputs is not None:
                json_data["inputs"] = inputs

            if parameters is not None:
                json_data["parameters"] = parameters

            if options is not None:
                for key in options.keys():
                    json_data[key] = options[key]

        if method == "PATCH":
            headers["Content-Type"] = "application/json"

        return headers, json_data, files

    @staticmethod
    async def async_post(
        endpoint: str,
        key: str,
        model_id: str = None,
        inputs: list = None,
        parameters: dict = None,
        options: Options = None,
        files: dict = None,
    ):
        """Low level API for async /post request to REST API.

        Args:
            endpoint (str): Remote endpoint to be queried.
            key (str): API key for authorization.
            model_id (str, optional): The id of the language model to be queried. Defaults to None.
            inputs (list, optional): List of inputs to be queried. Defaults to None.
            parameters (dict, optional): Key-value pairs for model parameters. Defaults to None.

        Returns:
            httpx.Response: Response from the REST API.
        """
        headers, json_data, files = RequestHandler._metadata(
            method="POST",
            key=key,
            model_id=model_id,
            inputs=inputs,
            parameters=parameters,
            options=options,
            files=files,
        )
        async with HttpProvider.get_async_client() as client:
            return await client.post(endpoint, headers=headers, json=json_data, files=files)

    @staticmethod
    async def async_patch(endpoint: str, key: str, json_data: dict) -> Response:
        """Low level API for /patch request to REST API.

        Currently only used for TOU endpoint.

        Args:
            endpoint (str):
            key (str)
            json_data: (dict)

        Returns:
            httpx.Response: Response from the REST API.
        """
        headers, _, _ = RequestHandler._metadata(method="PATCH", key=key)
        async with HttpProvider.get_async_client(timeout=ConnectionManager.TIMEOUT) as client:
            return await client.patch(endpoint, headers=headers, json=json_data)

    @staticmethod
    async def async_generate(
        endpoint: str,
        key: str,
        model_id: str = None,
        inputs: list = None,
        parameters: dict = None,
        options: Options = None,
    ):
        """Low level API for async /generate request to REST API.

        Args:
            endpoint (str): Remote endpoint to be queried.
            key (str): API key for authorization.
            model_id (str, optional): The id of the language model to be queried. Defaults to None.
            inputs (list, optional): List of inputs to be queried. Defaults to None.
            parameters (dict, optional): Key-value pairs for model parameters. Defaults to None.

        Returns:
            httpx.Response: Response from the REST API.
        """
        headers, json_data, _ = RequestHandler._metadata(
            method="POST",
            key=key,
            model_id=model_id,
            inputs=inputs,
            parameters=parameters,
            options=options,
        )
        response = None
        for attempt in range(0, ConnectionManager.MAX_RETRIES_GENERATE):
            response = await ConnectionManager.async_generate_client.post(endpoint, headers=headers, json=json_data)
            if response.status_code in [
                httpx.codes.SERVICE_UNAVAILABLE,
                httpx.codes.TOO_MANY_REQUESTS,
            ]:
                await asyncio.sleep(2 ** (attempt + 1))
            else:
                break
        return response

    @staticmethod
    async def async_tokenize(
        endpoint: str,
        key: str,
        model_id: str = None,
        inputs: list = None,
        parameters: dict = None,
        options: Options = None,
    ):
        """Low level API for async /tokenize request to REST API.

        Args:
            endpoint (str): Remote endpoint to be queried.
            key (str): API key for authorization.
            model_id (str, optional): The id of the language model to be queried. Defaults to None.
            inputs (list, optional): List of inputs to be queried. Defaults to None.
            parameters (dict, optional): Key-value pairs for model parameters. Defaults to None.

        Returns:
            httpx.Response: Response from the REST API.
        """
        headers, json_data, _ = RequestHandler._metadata(
            method="POST",
            key=key,
            model_id=model_id,
            inputs=inputs,
            parameters=parameters,
            options=options,
        )
        response = None
        for attempt in range(0, ConnectionManager.MAX_RETRIES_TOKENIZE):
            # NOTE: We don't retry-fail with httpx since that'd not
            # not respect the ratelimiting below (5 requests per second).
            # Instead, we do the ratelimiting here with the help of limiter.
            async with ConnectionManager.async_tokenize_limiter:
                response = await ConnectionManager.async_tokenize_client.post(endpoint, headers=headers, json=json_data)
                if response.status_code in [
                    httpx.codes.SERVICE_UNAVAILABLE,
                    httpx.codes.TOO_MANY_REQUESTS,
                ]:
                    await asyncio.sleep(2 ** (attempt + 1))
                else:
                    break
        return response

    @staticmethod
    async def async_get(endpoint: str, key: str, parameters: dict = None):
        """Low level API for async /get request to REST API.

        Args:
            endpoint (str): Remote endpoint to be queried.
            key (str): API key for authorization.
            parameters (dict, optional): Key-value pairs for model parameters. Defaults to None.

        Returns:
            httpx.Response: Response from the REST API.
        """
        headers, _, _ = RequestHandler._metadata(method="GET", key=key)

        async with HttpProvider.get_async_client(timeout=ConnectionManager.TIMEOUT) as client:
            response = await client.get(url=endpoint, headers=headers, params=parameters)
        return response

    @staticmethod
    def post(
        endpoint: str,
        key: str,
        model_id: str = None,
        inputs: list = None,
        parameters: dict = None,
        streaming: bool = False,
        options: Options = None,
        files: dict = None,
    ):
        """Low level API for /post request to REST API.

        Args:
            endpoint (str): Remote endpoint to be queried.
            key (str): API key for authorization.
            model_id (str, optional): The id of the language model to be queried. Defaults to None.
            inputs (list, optional): List of inputs to be queried. Defaults to None.
            parameters (dict, optional): Key-value pairs for model parameters. Defaults to None.
            options (Options, optional): Additional parameters to pass in the query payload. Defaults to None.
            files (dict, optional): Files to be sent to the server. Defaults to None.

        Returns:
            httpx.Response: Response from the REST API.
            or
            Generator of streamed response payloads from the REST API.
        """
        headers, json_data, files = RequestHandler._metadata(
            method="POST",
            key=key,
            model_id=model_id,
            inputs=inputs,
            parameters=parameters,
            options=options,
            files=files,
        )

        if streaming:
            return RequestHandler.post_stream(endpoint=endpoint, headers=headers, json_data=json_data, files=files)
        else:
            with HttpProvider.get_client(timeout=ConnectionManager.TIMEOUT) as s:
                response = s.post(url=endpoint, headers=headers, json=json_data, files=files)
                return response

    @staticmethod
    def patch(endpoint: str, key: str, json_data: dict) -> Response:
        """Low level API for /patch request to REST API.

        Currently only used for TOU endpoint.

        Args:
            endpoint (str):
            key (str)
            json_data: (dict)

        Returns:
            httpx.Response: Response from the REST API.
        """
        headers, _, _ = RequestHandler._metadata(method="PATCH", key=key)

        with HttpProvider.get_client(timeout=ConnectionManager.TIMEOUT) as s:
            response = s.patch(url=endpoint, headers=headers, json=json_data)
            return response

    @staticmethod
    def post_stream(endpoint, headers, json_data, files):
        with HttpProvider.get_client(timeout=ConnectionManager.TIMEOUT) as client:
            with connect_sse(
                client,
                method="POST",
                url=endpoint,
                headers=headers,
                json=json_data,
                files=files,
            ) as event_source:
                try:
                    for sse in event_source.iter_sse():
                        yield sse.data
                except SSEError as e:
                    response: Response = event_source.response
                    if "application/json" in response.headers["content-type"]:
                        response.read()
                        raise GenAiException(response)
                    raise e

    @staticmethod
    def get(endpoint: str, key: str, parameters: Optional[dict] = None) -> Response:
        """Low level API for /get request to REST API.

        Args:
            endpoint (str): Remote endpoint to be queried.
            key (str): API key for authorization.
            parameters (dict, optional): Key-value pairs for model parameters. Defaults to None.

        Returns:
            httpx.Response: Response from the REST API.
        """
        headers, _, _ = RequestHandler._metadata(method="GET", key=key)
        with HttpProvider.get_client(timeout=ConnectionManager.TIMEOUT) as s:
            response = s.get(url=endpoint, headers=headers, params=parameters)
            return response

    @staticmethod
    def put(endpoint: str, key: str, options: Optional[Options] = None) -> Response:
        """Low level API for /get request to REST API.

        Args:
            endpoint (str): Remote endpoint to be queried.
            key (str): API key for authorization.
            options (Options, optional): Additional parameters to pass in the query payload. Defaults to None.

        Returns:
            requests.models.Response: Response from the REST API.
        """
        headers, json_data, _ = RequestHandler._metadata(method="PUT", key=key, options=options)
        with HttpProvider.get_client(timeout=ConnectionManager.TIMEOUT) as s:
            response = s.put(url=endpoint, headers=headers, json=json_data)
            return response

    @staticmethod
    def delete(endpoint: str, key: str, parameters: Optional[dict] = None) -> Response:
        """Low level API for /get request to REST API.

        Args:
            endpoint (str): Remote endpoint to be queried.
            key (str): API key for authorization.
            parameters (dict, optional): Key-value pairs for model parameters. Defaults to None.

        Returns:
            requests.models.Response: Response from the REST API.
        """
        headers, _, _ = RequestHandler._metadata(method="DELETE", key=key)
        with HttpProvider.get_client(timeout=ConnectionManager.TIMEOUT) as s:
            response = s.delete(url=endpoint, headers=headers, params=parameters)
            return response
