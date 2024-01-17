from genai._generated.endpoints import ApiEndpoint
from genai._utils.service.metadata import (
    get_service_action_metadata,
    set_service_action_metadata,
)


class DummyEndpoint(ApiEndpoint):
    pass


def test_metadata_retrieval():
    @set_service_action_metadata(endpoint=DummyEndpoint)
    def create():
        return None

    metadata = get_service_action_metadata(create)
    assert metadata.endpoint == DummyEndpoint


def test_parameters_not_influenced():
    @set_service_action_metadata(endpoint=DummyEndpoint)
    def create(a: int, b: int, c: int):
        return a, b, c

    assert create(1, 2, 3) == (1, 2, 3)
