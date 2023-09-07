import httpx

__all__ = ["HttpProvider"]


class HttpProvider:
    default_http_client_options: dict = {}
    default_http_transport_options: dict = {}

    @classmethod
    def get_client(cls, **kwargs):
        options = {**cls.default_http_client_options, **kwargs}
        return httpx.Client(**options)

    @classmethod
    def get_async_client(cls, **kwargs):
        options = {**cls.default_http_client_options, **kwargs}
        return httpx.AsyncClient(**options)

    @classmethod
    def get_async_transport(cls, **kwargs):
        options = {**cls.default_http_transport_options, **kwargs}
        return httpx.AsyncHTTPTransport(**options)
