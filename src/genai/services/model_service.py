from typing import Optional

from genai.schemas.responses import ModelCard, ModelList
from genai.services.base_service import BaseService


class ModelService(BaseService):
    def available(self, model_id: str) -> bool:
        """Check if the model is available. Note that for tuned models
        the model could still be in the process of tuning.

        Returns:
            bool: Boolean indicating model availability
        """
        model = self.detail(model_id=model_id)
        return model is not None

    def detail(self, model_id: str) -> Optional[ModelCard]:
        api_response = self._api_service.model(model_id=model_id)
        if api_response.status_code == 200:
            response_json = api_response.json()
            return ModelCard(**response_json)
        return None

    def list(self) -> list[ModelCard]:
        """Get a list of models

        Args:
            credentials (Credentials): Credentials
            service (ServiceInterface): Service Interface

        Returns:
            list[ModelCard]: A list of available models
        """
        response = self._api_service.models()
        cards = ModelList(**response.json()).results
        return cards
