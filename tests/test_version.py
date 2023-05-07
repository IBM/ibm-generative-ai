import pytest

import genai
from genai._version import __version__


@pytest.mark.unit
class TestVersion:
    def test_get_version(self):
        assert genai.__version__ == __version__
