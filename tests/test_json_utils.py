# from unittest.mock import MagicMock, patch

import pytest

from genai.utils.json_utils import json_extract, json_get_all_keys


@pytest.mark.unit
class TestJsonUtils:
    @pytest.fixture
    def json_obj(self):
        return {"key1": "val1", "key2": {"key21": "val21"}, "key3": [{"key31": "val31"}, {"key31": "val32"}]}

    def test_json_extract(self, json_obj):
        a = json_extract(obj=json_obj, key="key1", join=True)
        assert a == "val1"

        a = json_extract(obj=json_obj, key="key31", join=False)
        assert a.sort() == ["val31", "val32"].sort()

        a = json_extract(obj=json_obj, key="key31", join=True)
        assert a == "val31val32"

        a = json_extract(obj=json_obj, key="key4")
        assert a == []

    def test_json_get_all_keys(self, json_obj):
        keys = json_get_all_keys(json_obj)
        assert keys.sort() == ["key1", "key21", "key2", "key3", "key31"].sort()

        keys = json_get_all_keys(json_obj, join=True)
        assert isinstance(keys, str)
        assert keys == "key1key21key31key31"
