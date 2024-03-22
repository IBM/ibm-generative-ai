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


class TextClassificationCreateEndpoint(ApiEndpoint):
    path: str = "/v2/beta/text/classification"
    method: str = "POST"
    version: str = "2023-11-22"


class TextRerankCreateEndpoint(ApiEndpoint):
    path: str = "/v2/beta/text/rerank"
    method: str = "POST"
    version: str = "2023-11-22"


class TextSentenceSimilarityCreateEndpoint(ApiEndpoint):
    path: str = "/v2/beta/text/sentence-similarity"
    method: str = "POST"
    version: str = "2023-11-22"


class BetaTimeSerieForecastingCreateEndpoint(ApiEndpoint):
    path: str = "/v2/beta/time_series/forecasting"
    method: str = "POST"
    version: str = "2023-11-22"


class BetaTimeSerieLimitRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/beta/time_series/limits"
    method: str = "GET"
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


class FileIdPatchEndpoint(ApiEndpoint):
    path: str = "/v2/files/{id}"
    method: str = "PATCH"
    version: str = "2023-11-22"


class FileIdContentRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/files/{id}/content"
    method: str = "GET"
    version: str = "2023-11-22"


class FolderRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/folders"
    method: str = "GET"
    version: str = "2023-11-22"


class FolderCreateEndpoint(ApiEndpoint):
    path: str = "/v2/folders"
    method: str = "POST"
    version: str = "2023-11-22"


class FolderIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/folders/{id}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class FolderIdRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/folders/{id}"
    method: str = "GET"
    version: str = "2023-11-22"


class FolderIdPatchEndpoint(ApiEndpoint):
    path: str = "/v2/folders/{id}"
    method: str = "PATCH"
    version: str = "2024-01-10"


class FolderIdUpdateEndpoint(ApiEndpoint):
    path: str = "/v2/folders/{id}"
    method: str = "PUT"
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
    version: str = "2024-03-19"


class PromptCreateEndpoint(ApiEndpoint):
    path: str = "/v2/prompts"
    method: str = "POST"
    version: str = "2024-03-19"


class PromptIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/prompts/{id}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class PromptIdRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/prompts/{id}"
    method: str = "GET"
    version: str = "2024-03-19"


class PromptIdPatchEndpoint(ApiEndpoint):
    path: str = "/v2/prompts/{id}"
    method: str = "PATCH"
    version: str = "2024-03-19"


class PromptIdUpdateEndpoint(ApiEndpoint):
    path: str = "/v2/prompts/{id}"
    method: str = "PUT"
    version: str = "2024-03-19"


class RequestRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/requests"
    method: str = "GET"
    version: str = "2023-11-22"


class RequestChatConversationIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/requests/chat/{conversation_id}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class RequestChatConversationIdRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/requests/chat/{conversation_id}"
    method: str = "GET"
    version: str = "2024-03-19"


class RequestIdDeleteEndpoint(ApiEndpoint):
    path: str = "/v2/requests/{id}"
    method: str = "DELETE"
    version: str = "2023-11-22"


class RequestIdFeedbackRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/requests/{id}/feedback"
    method: str = "GET"
    version: str = "2023-11-22"


class RequestIdFeedbackCreateEndpoint(ApiEndpoint):
    path: str = "/v2/requests/{id}/feedback"
    method: str = "POST"
    version: str = "2023-11-22"


class RequestIdFeedbackUpdateEndpoint(ApiEndpoint):
    path: str = "/v2/requests/{id}/feedback"
    method: str = "PUT"
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


class TagRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/tags"
    method: str = "GET"
    version: str = "2023-11-22"


class TaskRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/tasks"
    method: str = "GET"
    version: str = "2023-11-22"


class TextChatCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/chat"
    method: str = "POST"
    version: str = "2024-03-19"


class TextChatOutputCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/chat/output"
    method: str = "POST"
    version: str = "2024-03-19"


class TextChatStreamCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/chat_stream"
    method: str = "POST"
    version: str = "2024-03-19"


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
    version: str = "2024-03-19"


class TextGenerationComparisonCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/comparison"
    method: str = "POST"
    version: str = "2024-03-19"


class TextGenerationLimitRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/limits"
    method: str = "GET"
    version: str = "2023-11-22"


class TextGenerationOutputCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/output"
    method: str = "POST"
    version: str = "2024-03-19"


class TextGenerationIdFeedbackRetrieveEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/{id}/feedback"
    method: str = "GET"
    version: str = "2023-11-22"


class TextGenerationIdFeedbackCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/{id}/feedback"
    method: str = "POST"
    version: str = "2024-02-20"


class TextGenerationIdFeedbackUpdateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation/{id}/feedback"
    method: str = "PUT"
    version: str = "2024-02-20"


class TextGenerationStreamCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/generation_stream"
    method: str = "POST"
    version: str = "2024-03-19"


class TextModerationCreateEndpoint(ApiEndpoint):
    path: str = "/v2/text/moderations"
    method: str = "POST"
    version: str = "2024-03-19"


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


class TuneFromFileCreateEndpoint(ApiEndpoint):
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
