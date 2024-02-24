import pytest

from genai.client import Client


@pytest.mark.integration
class TestFolderService:
    @pytest.mark.vcr
    def test_create_delete_folder(self, client: Client, subtests):
        with subtests.test("Create folder"):
            create_response = client.folder.create(name="My test folder")
            id = create_response.result.id

        with subtests.test("Get folder"):
            retrieve_response = client.folder.retrieve(id=id)
            assert retrieve_response.result == create_response.result

        with subtests.test("List folders"):
            folder_ids = [folder.id for folder in client.folder.list().results]
            assert id in folder_ids

        with subtests.test("Delete folder"):
            client.folder.delete(id=id)

        with subtests.test("Verify the folder deletion"):
            for folder in client.folder.list().results:
                assert folder.id != id
