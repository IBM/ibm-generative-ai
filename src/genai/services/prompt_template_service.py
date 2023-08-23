from typing import Optional

from genai.services import PromptTemplateManager
from genai.services.base_service import BaseService


class PromptTemplateService(BaseService):
    def create(self, name: str, template: str):
        return PromptTemplateManager.save_template(template=template, name=name, credentials=self._credentials)

    def update(self, id: str, name: str, template: str):
        return PromptTemplateManager.update_template(id=id, template=template, name=name, credentials=self._credentials)

    def render(self, inputs: list = None, data: Optional[dict] = None):
        return PromptTemplateManager.render_watsonx_prompts(credentials=self._credentials, inputs=inputs, data=data)

    def load(self, id: Optional[str] = None, name: Optional[str] = None):
        return PromptTemplateManager.load_template(credentials=self._credentials, id=id, name=name)

    def list(self):
        return PromptTemplateManager.load_all_templates(credentials=self._credentials)

    def delete_by_id(self, id: str):
        PromptTemplateManager.delete_template_by_id(credentials=self._credentials, id=id)

    def delete_by_name(self, name: str):
        PromptTemplateManager.delete_template_by_name(credentials=self._credentials, name=name)
