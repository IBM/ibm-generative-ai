import json
from pathlib import Path

import pytest

from genai import Client
from genai.schema import FilePurpose


@pytest.mark.integration
class TestFileService:
    @pytest.mark.vcr
    def test_create_retrieve_delete_file(self, client: Client, tmp_path: Path, subtests):
        file_content = json.dumps({"data": "EXAMPLE TEMPLATE {{variable}}}"})
        file_path = tmp_path / "file.json"
        file_path.write_text(file_content)

        updated_file_content = json.dumps({"data": "UPDATED EXAMPLE TEMPLATE {{variable}}}"})
        updated_file_path = tmp_path / "file_updated.json"
        updated_file_path.write_text(updated_file_content)

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

        with subtests.test("Update file"):
            updated_response = client.file.update(file_id, file_path=updated_file_path)
            assert updated_response.result.file_name == updated_file_path.name
            assert updated_response.result.id == file_id

        with subtests.test("Re-read file"):
            updated_file_content_response = client.file.read(file_id)
            assert updated_file_content_response != file_content
            assert updated_file_content_response == updated_file_content

        with subtests.test("Delete file"):
            client.file.delete(file_id)

        with subtests.test("File was deleted"):
            files = list(client.file.list(search=file_path.name).results)
            assert all(f.id != file_id for f in files)
