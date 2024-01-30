class ApiEndpoint:
    __slots__ = ()
    path: str
    method: str
    version: str
    class_name: str


class ApiKeyRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/api_key"
    method: str = "GET"
    version: str = "2023-11-22"


class ApiKeyRegenerateCreateEndpoint(ApiEndpoint):
    path: str = "/v2/api_key/regenerate"
    method: str = "POST"
    version: str = "2023-11-22"


class FileRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/files"
    method: str = "GET"
    version: str = "2023-12-15"


class FileCreateEndpoint(ApiEndpoint):
    path: str = "/v2/files"
    method: str = "POST"
    version: str = "2023-12-15"


class FileIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/files/{id}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class FileIdRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/files/{id}"
    method: str = "GET"
    version: str = "2023-12-15"


class FileIdContentRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/files/{id}/content"
    method: str = "GET"
    version: str = "2023-11-22"


class ModelRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/models"
    method: str = "GET"
    version: str = "2023-11-22"


class ModelIdRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/models/{id}"
    method: str = "GET"
    version: str = "2024-01-30"


class PromptRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/prompts"
    method: str = "GET"
    version: str = "2024-01-10"


class PromptCreateEndpoint(ApiEndpoint):
    path: str = "/v2/prompts"
    method: str = "POST"
    version: str = "2024-01-10"


class PromptIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/prompts/{id}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class PromptIdRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/prompts/{id}"
    method: str = "GET"
    version: str = "2024-01-10"


class PromptIdPatchEndpoint(ApiEndpoint):
    path: str = "/v2/prompts/{id}"
    method: str = "PATCH"
    version: str = "2024-01-10"


class PromptIdUpdateEndpoint(ApiEndpoint):
    path: str = "/v2/prompts/{id}"
    method: str = "PUT"
    version: str = "2024-01-10"


class RequestRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/requests"
    method: str = "GET"
    version: str = "2023-11-22"


class RequestChatConversationIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/requests/chat/{conversationId}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class RequestChatConversationIdRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/requests/chat/{conversationId}"
    method: str = "GET"
    version: str = "2023-11-22"


class RequestIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/requests/{id}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class SystemPromptRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/system_prompts"
    method: str = "GET"
    version: str = "2023-11-22"


class SystemPromptCreateEndpoint(ApiEndpoint):
    path: str = "/v2/system_prompts"
    method: str = "POST"
    version: str = "2023-11-22"


class SystemPromptIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/system_prompts/{id}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class SystemPromptIdRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/system_prompts/{id}"
    method: str = "GET"
    version: str = "2023-11-22"


class SystemPromptIdUpdateEndpoint(ApiEndpoint):
    path: str = "/v2/system_prompts/{id}"
    method: str = "PUT"
    version: str = "2023-11-22"


class TaskRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/tasks"
    method: str = "GET"
    version: str = "2023-11-22"


class TextChatCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/chat"
    method: str = "POST"
    version: str = "2024-01-10"


class TextChatOutputCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/chat/output"
    method: str = "POST"
    version: str = "2024-01-10"


class TextChatStreamCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/chat_stream"
    method: str = "POST"
    version: str = "2024-01-10"


class TextEmbeddingCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/embeddings"
    method: str = "POST"
    version: str = "2023-11-22"


class TextEmbeddingLimitRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/text/embeddings/limits"
    method: str = "GET"
    version: str = "2023-11-22"


class TextExtractionLimitRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/text/extraction/limits"
    method: str = "GET"
    version: str = "2023-11-22"


class TextGenerationCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation"
    method: str = "POST"
    version: str = "2024-01-10"


class TextGenerationComparisonCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/comparison"
    method: str = "POST"
    version: str = "2023-11-22"


class TextGenerationLimitRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/limits"
    method: str = "GET"
    version: str = "2023-11-22"


class TextGenerationOutputCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/output"
    method: str = "POST"
    version: str = "2023-11-22"


class TextGenerationIdFeedbackRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/{id}/feedback"
    method: str = "GET"
    version: str = "2023-11-22"


class TextGenerationIdFeedbackCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/{id}/feedback"
    method: str = "POST"
    version: str = "2023-11-22"


class TextGenerationIdFeedbackUpdateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/{id}/feedback"
    method: str = "PUT"
    version: str = "2023-11-22"


class TextGenerationStreamCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation_stream"
    method: str = "POST"
    version: str = "2024-01-10"


class TextModerationCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/moderations"
    method: str = "POST"
    version: str = "2023-11-22"


class TextTokenizationCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/tokenization"
    method: str = "POST"
    version: str = "2024-01-10"


class TuneRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/tunes"
    method: str = "GET"
    version: str = "2023-11-22"


class TuneCreateEndpoint(ApiEndpoint):
    path: str = "/v2/tunes"
    method: str = "POST"
    version: str = "2023-11-22"


class TuneImportCreateEndpoint(ApiEndpoint):
    path: str = "/v2/tunes/import"
    method: str = "POST"
    version: str = "2023-11-22"


class TuneIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/tunes/{id}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class TuneIdRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/tunes/{id}"
    method: str = "GET"
    version: str = "2023-11-22"


class TuneIdPatchEndpoint(ApiEndpoint):
    path: str = "/v2/tunes/{id}"
    method: str = "PATCH"
    version: str = "2023-11-22"


class TuneIdContentTypeRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/tunes/{id}/content/{type}"
    method: str = "GET"
    version: str = "2023-12-15"


class TuningTypeRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/tuning_types"
    method: str = "GET"
    version: str = "2024-01-30"


class UserDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/user"
    method: str = "DELETE"
    version: str = "2023-11-22"


class UserRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/user"
    method: str = "GET"
    version: str = "2023-11-22"


class UserPatchEndpoint(ApiEndpoint):
    path: str = "/v2/user"
    method: str = "PATCH"
    version: str = "2023-11-22"


class UserCreateEndpoint(ApiEndpoint):
    path: str = "/v2/user"
    method: str = "POST"
    version: str = "2023-11-22"
