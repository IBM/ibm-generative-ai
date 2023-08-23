from typing import Optional

from genai.exceptions import GenAiException
from genai.schemas import CreateTuneHyperParams, CreateTuneParams
from genai.schemas.responses import TuneInfoResult
from genai.schemas.tunes_params import DownloadAssetsParams
from genai.services import TuneManager
from genai.services.base_service import BaseService


class TuneService(BaseService):
    def create(
        self,
        source_model_id: str,
        name: str,
        method: str,
        task: str,
        hyperparameters: CreateTuneHyperParams = None,
        training_file_ids: Optional[list[str]] = None,
        validation_file_ids: Optional[list[str]] = None,
    ) -> TuneInfoResult:
        """Tune the base-model for given training data.

        Args:
            name (str): Label for this tuned model.
            method (str): The list of one or more prompt strings.
            task (str): Task ID, could be "classification", "summarization", or "generation"
            hyperparameters (CreateTuneHyperParams): Tuning hyperparameters
            training_file_ids (list[str]): IDs for files with training data
            validation_file_ids (list[str]): IDs for files with validation data

        Returns:
            Model: An instance of tuned model
        """
        if training_file_ids is None:
            raise GenAiException(ValueError("Parameter should be specified: training_file_paths or training_file_ids."))

        params = CreateTuneParams(
            name=name,
            model_id=source_model_id,
            method_id=method,
            task_id=task,
            training_file_ids=training_file_ids,
            validation_file_ids=validation_file_ids,
            parameters=hyperparameters or CreateTuneHyperParams(),
        )
        return TuneManager.create_tune(service=self._api_service, params=params)

    def status(self, tune_id: str) -> Optional[str]:
        tune = self.detail(tune_id)
        if tune:
            return tune.status
        return None

    def detail(self, tune_id: str) -> Optional[TuneInfoResult]:
        return TuneManager.get_tune(tune_id=tune_id, service=self._api_service)

    def delete(self, tune_id: str):
        tune = TuneManager.get_tune(service=self._api_service, tune_id=tune_id)
        if tune is None:
            raise GenAiException(ValueError("Tuned model not found. Currently method supports only tuned models."))
        TuneManager.delete_tune(service=self._api_service, tune_id=tune_id)

    def download(self, tune_id: str, output_path="tune_assets"):
        encoder_params = DownloadAssetsParams(id=tune_id, content="encoder")
        logs_params = DownloadAssetsParams(id=tune_id, content="logs")

        encoder_response = TuneManager.download_tune_assets(
            service=self._api_service, params=encoder_params, output_path=output_path
        )
        logs_response = TuneManager.download_tune_assets(
            service=self._api_service, params=logs_params, output_path=output_path
        )

        return {
            "encoder_download_path": encoder_response["dowloaded_file_path"],
            "logs_download_path": logs_response["dowloaded_file_path"],
        }
