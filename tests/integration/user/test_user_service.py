import pytest

from genai import Client


@pytest.mark.integration
class TestUserService:
    @pytest.mark.vcr
    def test_update_user(self, client: Client, subtests) -> None:
        """Embedding works correctly."""

        with subtests.test("Set terms of use to false"):
            client.user.update(tou_accepted=False)

        with subtests.test("Retrieve user"):
            user = client.user.retrieve()
            assert user.result.first_name and user.result.last_name
            # TODO: checking only tou_accepted, because data_usage_content is impossible to turn off now
            assert user.result.tou_accepted is False

        with subtests.test("Set consents to true."):
            client.user.update(tou_accepted=True)

        with subtests.test("Check updates"):
            user = client.user.retrieve()
            assert user.result.tou_accepted is True
