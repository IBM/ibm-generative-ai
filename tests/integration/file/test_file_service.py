import json
from pathlib import Path

import pytest

from genai import Client
from genai.file import FilePurpose


@pytest.mark.integration
class TestFileService:
    @pytest.mark.vcr
    def test_create_retrieve_delete_file(self, client: Client, tmp_path: Path, subtests):
        file_content = json.dumps({"data": "EXAMPLE TEMPLATE {{variable}}}"})
        file_path = tmp_path / "file.json"
        file_path.write_text(file_content)

        with subtests.test("Create file"):
            create_response = client.file.create(file_path, purpose=FilePurpose.TEMPLATE)
            assert create_response.result.file_name == file_path.name
            file_id = create_response.result.id

        with subtests.test("List files"):
            files = list(client.file.list(search=file_path.name).results)
            assert any(f.id == file_id for f in files)

        with subtests.test("Retrieve file"):
            assert client.file.retrieve(file_id).result == create_response.result

        with subtests.test("Read file"):
            assert client.file.read(file_id) == file_content

        with subtests.test("Delete file"):
            client.file.delete(file_id)

        with subtests.test("File was deleted"):
            files = list(client.file.list(search=file_path.name).results)
            assert all(f.id != file_id for f in files)
