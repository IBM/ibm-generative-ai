Changelog
=========


v3.0.0 (2024-05-27)
-------------------

🌟 Highlights
^^^^^^^^^^^^^^^^^^^^^^^^^
- Add llama 3 model 🦙🦙🦙
- Add fine tuning with deployments
- Add lm-evaluation-harness extension
See `📚 Examples <https://ibm.github.io/ibm-generative-ai/latest/rst_source/examples.html>`_ for more information.



🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^
- feat: new llama model `#(356) <https://github.com/IBM/ibm-generative-ai/pull/356>`_ [`@David-Kristek <https://github.com/David-Kristek>`_]
- feat: add lm_eval extension `#(345) <https://github.com/IBM/ibm-generative-ai/pull/345>`_ [`@jezekra1 <https://github.com/jezekra1>`_, `@yoavkatz <https://github.com/yoavkatz>`_]
- feat: add fine-tuning with deployments `#(357) <https://github.com/IBM/ibm-generative-ai/pull/357>`_ [`@David-Kristek <https://github.com/David-Kristek>`_]

🐛 Bug Fixes
^^^^^^^^^^^
- fix(huggingface): fix not working default tool `#(355) <https://github.com/IBM/ibm-generative-ai/pull/355>`_ [`@David-Kristek <https://github.com/David-Kristek>`_]
- fix(llama-index): avoid batching in embeddings `#(353) <https://github.com/IBM/ibm-generative-ai/pull/353>`_ [`@David-Kristek <https://github.com/David-Kristek>`_]

📖 Docs
^^^^^^
- docs: update migration guide [`@jezekra1 <https://github.com/jezekra1>`_]
- docs(example): typo in text moderation [`@lmandel <https://github.com/lmandel>`_]
- docs(moderation): update description [`@Tomas2D <https://github.com/Tomas2D>`_]

⚙️ Other
^^^^^^^^
- chore: remove deprecated code `#(358) <https://github.com/IBM/ibm-generative-ai/pull/358>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- ci: deploy documentation after new version gets published [`@Tomas2D <https://github.com/Tomas2D>`_]
- chore: update dependencies [`@Tomas2D <https://github.com/Tomas2D>`_]

**Full Changelog**: `v2.3.0...v3.0.0 <https://github.com/IBM/ibm-generative-ai/compare/v2.3.0...v3.0.0>`_

.. admonition:: Warning
    :class: warning

    We have removed deprecations introduced after v2 release. See the `V3 Migration Guide <v3_migration_guide>`_ for detailed information.


🔗 API Endpoint Versions
^^^^^^^^^^^^^^^^^^^^^^^^

.. collapse:: API Endpoint Versions

    ========  ==========================================  ======================
    Method    Path                                        Version (YYYY-MM-DD)
    ========  ==========================================  ======================
    GET       /v2/api_key                                 2023-11-22
    POST      /v2/api_key/regenerate                      2023-11-22
    GET       /v2/beta/evaluations                        2023-11-22
    POST      /v2/beta/evaluations                        2023-11-22
    GET       /v2/beta/evaluations/experiments            2023-11-22
    POST      /v2/beta/evaluations/experiments            2023-11-22
    DELETE    /v2/beta/evaluations/experiments/{id}       2023-11-22
    GET       /v2/beta/evaluations/experiments/{id}       2023-11-22
    GET       /v2/beta/evaluations/limits                 2023-11-22
    POST      /v2/beta/evaluations/preview                2023-11-22
    GET       /v2/beta/evaluations/templates              2023-11-22
    GET       /v2/beta/evaluations/templates/{id}         2023-11-22
    DELETE    /v2/beta/evaluations/{id}                   2023-11-22
    GET       /v2/beta/evaluations/{id}                   2023-11-22
    GET       /v2/beta/evaluations/{id}/instance_results  2023-11-22
    POST      /v2/beta/text/classification                2023-11-22
    POST      /v2/beta/text/rerank                        2023-11-22
    POST      /v2/beta/text/sentence-similarity           2023-11-22
    POST      /v2/beta/time_series/forecasting            2023-11-22
    GET       /v2/beta/time_series/limits                 2023-11-22
    GET       /v2/deployments                             2023-11-22
    POST      /v2/deployments                             2023-11-22
    DELETE    /v2/deployments/{id}                        2023-11-22
    GET       /v2/deployments/{id}                        2023-11-22
    GET       /v2/files                                   2024-05-13
    POST      /v2/files                                   2024-05-13
    DELETE    /v2/files/{id}                              2023-11-22
    GET       /v2/files/{id}                              2024-05-13
    PATCH     /v2/files/{id}                              2023-11-22
    GET       /v2/files/{id}/content                      2023-11-22
    GET       /v2/folders                                 2023-11-22
    POST      /v2/folders                                 2023-11-22
    DELETE    /v2/folders/{id}                            2023-11-22
    GET       /v2/folders/{id}                            2023-11-22
    PATCH     /v2/folders/{id}                            2024-01-10
    PUT       /v2/folders/{id}                            2023-11-22
    GET       /v2/models                                  2023-11-22
    GET       /v2/models/{id}                             2024-01-30
    GET       /v2/prompts                                 2024-03-19
    POST      /v2/prompts                                 2024-03-19
    DELETE    /v2/prompts/{id}                            2023-11-22
    GET       /v2/prompts/{id}                            2024-03-19
    PATCH     /v2/prompts/{id}                            2024-03-19
    PUT       /v2/prompts/{id}                            2024-03-19
    GET       /v2/requests                                2023-11-22
    DELETE    /v2/requests/chat/{conversation_id}         2023-11-22
    GET       /v2/requests/chat/{conversation_id}         2024-03-19
    DELETE    /v2/requests/{id}                           2023-11-22
    GET       /v2/requests/{id}/feedback                  2023-11-22
    POST      /v2/requests/{id}/feedback                  2023-11-22
    PUT       /v2/requests/{id}/feedback                  2023-11-22
    GET       /v2/system_prompts                          2023-11-22
    POST      /v2/system_prompts                          2023-11-22
    DELETE    /v2/system_prompts/{id}                     2023-11-22
    GET       /v2/system_prompts/{id}                     2023-11-22
    PUT       /v2/system_prompts/{id}                     2023-11-22
    GET       /v2/tags                                    2023-11-22
    GET       /v2/tasks                                   2023-11-22
    POST      /v2/text/chat                               2024-03-19
    POST      /v2/text/chat/output                        2024-03-19
    POST      /v2/text/chat_stream                        2024-03-19
    POST      /v2/text/embeddings                         2024-04-15
    GET       /v2/text/embeddings/limits                  2023-11-22
    GET       /v2/text/extraction/limits                  2023-11-22
    POST      /v2/text/generation                         2024-03-19
    POST      /v2/text/generation/comparison              2024-03-19
    GET       /v2/text/generation/limits                  2023-11-22
    POST      /v2/text/generation/output                  2024-03-19
    GET       /v2/text/generation/{id}/feedback           2023-11-22
    POST      /v2/text/generation/{id}/feedback           2024-02-20
    PUT       /v2/text/generation/{id}/feedback           2024-02-20
    POST      /v2/text/generation_stream                  2024-03-19
    POST      /v2/text/moderations                        2024-03-19
    POST      /v2/text/tokenization                       2024-01-10
    GET       /v2/tunes                                   2023-11-22
    POST      /v2/tunes                                   2023-11-22
    POST      /v2/tunes/import                            2023-11-22
    POST      /v2/tunes/preflight                         2023-11-22
    DELETE    /v2/tunes/{id}                              2023-11-22
    GET       /v2/tunes/{id}                              2023-11-22
    PATCH     /v2/tunes/{id}                              2023-11-22
    GET       /v2/tunes/{id}/content                      2023-11-22
    GET       /v2/tunes/{id}/content/{type}               2023-12-15
    GET       /v2/tuning_types                            2024-01-30
    DELETE    /v2/user                                    2023-11-22
    GET       /v2/user                                    2023-11-22
    PATCH     /v2/user                                    2023-11-22
    POST      /v2/user                                    2023-11-22
    ========  ==========================================  ======================

v2.3.0 (2024-03-22)
-------------------

- Add Text Experimental module (see `client.text.experimental`)
    - Sentence Similarity (`client.text.sentence_similarity`).
    - Rerank (`client.text.experimental.rerank`).
    - Classification (`client.text.experimental.classification`).
- Add Folder module (`client.folder`).
- Add Tags module (`client.tag`).
- Add Tasks module (`client.task`).
- Add Request Feedback Service (`client.request.feedback`).
- Update Moderations.
    - Add Social Bias model.
    - Remove Implicit Hate and Stigma model.
- Add tune creation from an existing file (client.tune.create_from_file).
- Allow to upload arbitrary files (remove old constraints for json files only).
- Add support to update the file content (see client.file.update method).
- Add support for the latest `LangChain` / `LLamaIndex` (migrate to 0.10.x) / `Transformers` versions.
- Unify schemas between various services.

.. admonition:: Deprecation Warnings
    :class: warning

    - Stigma (`ModerationStigma` class) has been deprecated, use Social Bias instead (`ModerationSocialBias` class).
    - Implicit Hate (`ModerationImplicitHate` class) has been deprecated, use Social Bias instead (`ModerationSocialBias` class).

    .. code-block:: python

            from genai.schema import ModerationHAP, ModerationHAPInput

             # ❌ Old Way
            ModerationHAP(input=True, output=True, threshold=0.8)

             # ✅ New Way
            ModerationHAP(
                input=ModerationHAPInput(enabled=True, threshold=0.8),
                output=ModerationHAPOutput(enabled=True, threshold=0.8)
            )

    - Deprecate `TuningType` enum; use values from `client.tune.types()` method.
    - Following schemas or their properties were renamed.
        - `UserPromptResult` -> `PromptResult`
        - `PromptsResponseResult` -> `PromptResult`
        - `UserResponseResult` -> `UserResult`
        - `UserCreateResultApiKey` -> `UserApiKey`
        - `PromptRetrieveRequestParamsSource` -> `PromptListSource`
        - `TextChatStreamCreateResponse.moderation` -> `TextChatStreamCreateResponse.moderations`
        - `TextGenerationStreamCreateResponse.moderation` -> `TextGenerationStreamCreateResponse.moderations`
        - `TextGenerationResult.moderation` -> `TextGenerationResult.moderations`
        - `BaseMessage.file_ids` -> `BaseMessage.files`

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^
- feat(text): update schemas [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(request): update schemas [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(user): update schemas [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(model): update schemas [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(prompt): update schemas [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(task): init task module [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(text): init text experimental module (sentence similarity, rerank, classification) [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(tags): init tags module [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(folder): init folder module [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(llama-index): migrate to v0.10.x `#(331) <https://github.com/IBM/ibm-generative-ai/pull/331>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat: add request feedback module and deprecate text generation feedback [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat: improve schema generation [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat: infer openapi schema type [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat: add fallback for deprecated/removed schemas [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat: add support for custom auth `#(335) <https://github.com/IBM/ibm-generative-ai/pull/335>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- feat(text): add input property to text generation to align with API [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(tune): replace static tuning type enum by dynamic retrieval [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(extension): add comments to the local server example [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(prompt): update folder_id parameter [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(user): update schemas (email property added) [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(file): add update method, add 'origin_id' parameter and schema [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(request): update request chat conversation response body [`@Tomas2D <https://github.com/Tomas2D>`_]

🐛 Bug Fixes
^^^^^^^^^^^
- fix(tune): unexpected access to non-enum property [`@Tomas2D <https://github.com/Tomas2D>`_]

📖 Docs
^^^^^^
- docs(readme): update watsonx SDK URL `#(339) <https://github.com/IBM/ibm-generative-ai/pull/339>`_ [`@JanPokorny <https://github.com/JanPokorny>`_]
- docs: update furo template [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: update authors [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: update examples descriptions [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: switch to sphinx-multiversion fork `#(326) <https://github.com/IBM/ibm-generative-ai/pull/326>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs(folder): update example [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs(folder): update folder example [`@Tomas2D <https://github.com/Tomas2D>`_]

⚙️ Other
^^^^^^^^
- test(langchain): use 'invoke' method instead '__call__' [`@Tomas2D <https://github.com/Tomas2D>`_]
- test: add tests for schema deprecation [`@Tomas2D <https://github.com/Tomas2D>`_]
- test: add tests for endpoint aliases [`@Tomas2D <https://github.com/Tomas2D>`_]
- test: remove non existing models [`@Tomas2D <https://github.com/Tomas2D>`_]

**Full Changelog**: `v2.2.0...v2.3.0 <https://github.com/IBM/ibm-generative-ai/compare/v2.2.0...v2.3.0>`_


🔗 API Endpoint Versions
^^^^^^^^^^^^^^^^^^^^^^^^

.. collapse:: API Endpoint Versions

    ========  ===================================  ======================
    Method    Path                                 Version (YYYY-MM-DD)
    ========  ===================================  ======================
    GET       /v2/api_key                          2023-11-22
    POST      /v2/api_key/regenerate               2023-11-22
    POST      /v2/beta/text/classification         2023-11-22
    POST      /v2/beta/text/rerank                 2023-11-22
    POST      /v2/beta/text/sentence-similarity    2023-11-22
    POST      /v2/beta/time_series/forecasting     2023-11-22
    GET       /v2/beta/time_series/limits          2023-11-22
    GET       /v2/files                            2023-12-15
    POST      /v2/files                            2023-12-15
    DELETE    /v2/files/{id}                       2023-11-22
    GET       /v2/files/{id}                       2023-12-15
    PATCH     /v2/files/{id}                       2023-11-22
    GET       /v2/files/{id}/content               2023-11-22
    GET       /v2/folders                          2023-11-22
    POST      /v2/folders                          2023-11-22
    DELETE    /v2/folders/{id}                     2023-11-22
    GET       /v2/folders/{id}                     2023-11-22
    PATCH     /v2/folders/{id}                     2024-01-10
    PUT       /v2/folders/{id}                     2023-11-22
    GET       /v2/models                           2023-11-22
    GET       /v2/models/{id}                      2024-01-30
    GET       /v2/prompts                          2024-03-19
    POST      /v2/prompts                          2024-03-19
    DELETE    /v2/prompts/{id}                     2023-11-22
    GET       /v2/prompts/{id}                     2024-03-19
    PATCH     /v2/prompts/{id}                     2024-03-19
    PUT       /v2/prompts/{id}                     2024-03-19
    GET       /v2/requests                         2023-11-22
    DELETE    /v2/requests/chat/{conversation_id}  2023-11-22
    GET       /v2/requests/chat/{conversation_id}  2024-03-19
    DELETE    /v2/requests/{id}                    2023-11-22
    GET       /v2/requests/{id}/feedback           2023-11-22
    POST      /v2/requests/{id}/feedback           2023-11-22
    PUT       /v2/requests/{id}/feedback           2023-11-22
    GET       /v2/system_prompts                   2023-11-22
    POST      /v2/system_prompts                   2023-11-22
    DELETE    /v2/system_prompts/{id}              2023-11-22
    GET       /v2/system_prompts/{id}              2023-11-22
    PUT       /v2/system_prompts/{id}              2023-11-22
    GET       /v2/tags                             2023-11-22
    GET       /v2/tasks                            2023-11-22
    POST      /v2/text/chat                        2024-03-19
    POST      /v2/text/chat/output                 2024-03-19
    POST      /v2/text/chat_stream                 2024-03-19
    POST      /v2/text/embeddings                  2023-11-22
    GET       /v2/text/embeddings/limits           2023-11-22
    GET       /v2/text/extraction/limits           2023-11-22
    POST      /v2/text/generation                  2024-03-19
    POST      /v2/text/generation/comparison       2024-03-19
    GET       /v2/text/generation/limits           2023-11-22
    POST      /v2/text/generation/output           2024-03-19
    GET       /v2/text/generation/{id}/feedback    2023-11-22
    POST      /v2/text/generation/{id}/feedback    2024-02-20
    PUT       /v2/text/generation/{id}/feedback    2024-02-20
    POST      /v2/text/generation_stream           2024-03-19
    POST      /v2/text/moderations                 2024-03-19
    POST      /v2/text/tokenization                2024-01-10
    GET       /v2/tunes                            2023-11-22
    POST      /v2/tunes                            2023-11-22
    POST      /v2/tunes/import                     2023-11-22
    DELETE    /v2/tunes/{id}                       2023-11-22
    GET       /v2/tunes/{id}                       2023-11-22
    PATCH     /v2/tunes/{id}                       2023-11-22
    GET       /v2/tunes/{id}/content/{type}        2023-12-15
    GET       /v2/tuning_types                     2024-01-30
    DELETE    /v2/user                             2023-11-22
    GET       /v2/user                             2023-11-22
    PATCH     /v2/user                             2023-11-22
    POST      /v2/user                             2023-11-22
    ========  ===================================  ======================

v2.2.0 (2024-02-20)
-------------------

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^
- feat(llama-index): add embeddings `#(316) <https://github.com/IBM/ibm-generative-ai/pull/316>`_ [`@David-Kristek <https://github.com/David-Kristek>`_]


🐛 Bug Fixes
^^^^^^^^^^^
- fix: improve http error handling `#(320) <https://github.com/IBM/ibm-generative-ai/pull/320>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- fix: allow the remaining limit to have a negative value `#(317) <https://github.com/IBM/ibm-generative-ai/pull/317>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- fix: correct typo in url `#(310) <https://github.com/IBM/ibm-generative-ai/pull/310>`_ [SOTAkkkk]

📖 Docs
^^^^^^
- docs: add simple text generation example `#(323) <https://github.com/IBM/ibm-generative-ai/pull/323>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]

⚙️ Other
^^^^^^^^
- chore: fixes and updates `#(318) <https://github.com/IBM/ibm-generative-ai/pull/318>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- typo: fix bam api url in documentation `#(319) <https://github.com/IBM/ibm-generative-ai/pull/319>`_ [Aditya Gupta]
- docs(langchain): add langchain sql agent example `#(314) <https://github.com/IBM/ibm-generative-ai/pull/314>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- chore: less strict typings `#(315) <https://github.com/IBM/ibm-generative-ai/pull/315>`_ [`@David-Kristek <https://github.com/David-Kristek>`_]
- chore: improve types generation `#(312) <https://github.com/IBM/ibm-generative-ai/pull/312>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]

**Full Changelog**: `v2.1.1...v2.2.0 <https://github.com/IBM/ibm-generative-ai/compare/v2.1.1...v2.2.0>`_


🔗 API Endpoint Versions
^^^^^^^^^^^^^^^^^^^^^^^^

.. collapse:: API Endpoint Versions

    ========  ==================================  ======================
    Method    Path                                Version (YYYY-MM-DD)
    ========  ==================================  ======================
    GET       /v2/api_key                         2023-11-22
    POST      /v2/api_key/regenerate              2023-11-22
    GET       /v2/files                           2023-12-15
    POST      /v2/files                           2023-12-15
    DELETE    /v2/files/{id}                      2023-11-22
    GET       /v2/files/{id}                      2023-12-15
    GET       /v2/files/{id}/content              2023-11-22
    GET       /v2/models                          2023-11-22
    GET       /v2/models/{id}                     2024-01-30
    GET       /v2/prompts                         2024-01-10
    POST      /v2/prompts                         2024-01-10
    DELETE    /v2/prompts/{id}                    2023-11-22
    GET       /v2/prompts/{id}                    2024-01-10
    PATCH     /v2/prompts/{id}                    2024-01-10
    PUT       /v2/prompts/{id}                    2024-01-10
    GET       /v2/requests                        2023-11-22
    DELETE    /v2/requests/chat/{conversationId}  2023-11-22
    GET       /v2/requests/chat/{conversationId}  2023-11-22
    DELETE    /v2/requests/{id}                   2023-11-22
    GET       /v2/system_prompts                  2023-11-22
    POST      /v2/system_prompts                  2023-11-22
    DELETE    /v2/system_prompts/{id}             2023-11-22
    GET       /v2/system_prompts/{id}             2023-11-22
    PUT       /v2/system_prompts/{id}             2023-11-22
    GET       /v2/tasks                           2023-11-22
    POST      /v2/text/chat                       2024-01-10
    POST      /v2/text/chat/output                2024-01-10
    POST      /v2/text/chat_stream                2024-01-10
    POST      /v2/text/embeddings                 2023-11-22
    GET       /v2/text/embeddings/limits          2023-11-22
    GET       /v2/text/extraction/limits          2023-11-22
    POST      /v2/text/generation                 2024-01-10
    POST      /v2/text/generation/comparison      2023-11-22
    GET       /v2/text/generation/limits          2023-11-22
    POST      /v2/text/generation/output          2023-11-22
    GET       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation/{id}/feedback   2023-11-22
    PUT       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation_stream          2024-01-10
    POST      /v2/text/moderations                2023-11-22
    POST      /v2/text/tokenization               2024-01-10
    GET       /v2/tunes                           2023-11-22
    POST      /v2/tunes                           2023-11-22
    POST      /v2/tunes/import                    2023-11-22
    DELETE    /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}                      2023-11-22
    PATCH     /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}/content/{type}       2023-12-15
    GET       /v2/tuning_types                    2024-01-30
    DELETE    /v2/user                            2023-11-22
    GET       /v2/user                            2023-11-22
    PATCH     /v2/user                            2023-11-22
    POST      /v2/user                            2023-11-22
    ========  ==================================  ======================

v2.1.1 (2024-02-02)
-------------------

🐛 Bug Fixes
^^^^^^^^^^^
- fix: make SharedResource threadsafe `#(307) <https://github.com/IBM/ibm-generative-ai/pull/307>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- fix: point readme documentation links to latest version `#(306) <https://github.com/IBM/ibm-generative-ai/pull/306>`_ [`@jezekra1 <https://github.com/jezekra1>`_]

⚙️ Other
^^^^^^^^
- feat(langchain): validate peer dependency `#(308) <https://github.com/IBM/ibm-generative-ai/pull/308>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- fix(docs): update pre-build hook [`@Tomas2D <https://github.com/Tomas2D>`_]

**Full Changelog**: `v2.1.0...v2.1.1 <https://github.com/IBM/ibm-generative-ai/compare/v2.1.0...v2.1.1>`_


v2.1.0 (2024-01-30)
-------------------

.. admonition:: Schema Import (deprecation warning)
    :class: warning

    Schemas are now exported from genai.schema (the old way of importing remains to work, but you will receive a warning)


🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^
- feat: refactor schemas for better user experience `#(294) <https://github.com/IBM/ibm-generative-ai/pull/294>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- feat: add truncate_input_tokens parameter for embeddings `#(280) <https://github.com/IBM/ibm-generative-ai/pull/280>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- feat: migrate to langchain_core `#(261) <https://github.com/IBM/ibm-generative-ai/pull/261>`_ [`@David-Kristek <https://github.com/David-Kristek>`_]
- feat: adjust tests and pipeline to ensure 3.12 compatibility `#(259) <https://github.com/IBM/ibm-generative-ai/pull/259>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- feat: retrieve service actions metadata `#(260) <https://github.com/IBM/ibm-generative-ai/pull/260>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(example): add chromadb embedding function `#(270) <https://github.com/IBM/ibm-generative-ai/pull/270>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(langchain): correctly handles prompt_id and model_id `#(293) <https://github.com/IBM/ibm-generative-ai/pull/293>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(system-prompts): init module `#(292) <https://github.com/IBM/ibm-generative-ai/pull/292>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(langchain): add embeddings support `#(289) <https://github.com/IBM/ibm-generative-ai/pull/289>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- feat(examples): add example of langchain agent with tools `#(268) <https://github.com/IBM/ibm-generative-ai/pull/268>`_ [`@David-Kristek <https://github.com/David-Kristek>`_]
- feat(langchain): update core and related dependencies `#(282) <https://github.com/IBM/ibm-generative-ai/pull/282>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]

🐛 Bug Fixes
^^^^^^^^^^^^^
- fix: rewrite test casettes due to vcrpy update `#(290) <https://github.com/IBM/ibm-generative-ai/pull/290>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- fix: update vcrpy to released version `#(284) <https://github.com/IBM/ibm-generative-ai/pull/284>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- fix: external limiter implementation `#(274) <https://github.com/IBM/ibm-generative-ai/pull/274>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- fix: include overhead in payload size calculation when batching `#(266) <https://github.com/IBM/ibm-generative-ai/pull/266>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- fix: reduce maximum payload size [`@jezekra1 <https://github.com/jezekra1>`_]
- fix: schema action metadata inheritance `#(262) <https://github.com/IBM/ibm-generative-ai/pull/262>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- fix(docs): redirects `#(298) <https://github.com/IBM/ibm-generative-ai/pull/298>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- fix(langchain): templates and models `#(293) <https://github.com/IBM/ibm-generative-ai/pull/293>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]

📖 Docs
^^^^^^^
- docs: update links in README [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: update link to the migration guide [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: init documentation versioning `#(296) <https://github.com/IBM/ibm-generative-ai/pull/296>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: add installation note for extensions `#(291) <https://github.com/IBM/ibm-generative-ai/pull/291>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: update prompt usage example `#(275) <https://github.com/IBM/ibm-generative-ai/pull/275>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: update migration guide, examples, deploy `#(271) <https://github.com/IBM/ibm-generative-ai/pull/271>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: update migration guide `#(269) <https://github.com/IBM/ibm-generative-ai/pull/269>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- docs: update README [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: update faq / credentials / migration guide `#(263) <https://github.com/IBM/ibm-generative-ai/pull/263>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- docs: add changelog `#(257) <https://github.com/IBM/ibm-generative-ai/pull/257>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- docs: improve examples `#(258) <https://github.com/IBM/ibm-generative-ai/pull/258>`_ [`@jezekra1 <https://github.com/jezekra1>`_]

⚙️ Other
^^^^^^^^
- build: add langchain to dev dependencies [`@Tomas2D <https://github.com/Tomas2D>`_]
- refactor: remove list comprehensions to preserve type-hints `#(301) <https://github.com/IBM/ibm-generative-ai/pull/301>`_ [`@jezekra1 <https://github.com/jezekra1>`_]
- ci: update git checkout for documentation build [`@Tomas2D <https://github.com/Tomas2D>`_]
- ci: update docs build script [`@Tomas2D <https://github.com/Tomas2D>`_]
- ci: set CODEOWNERS `#(267) <https://github.com/IBM/ibm-generative-ai/pull/267>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- build: remove unused dependencies and update versions `#(264) <https://github.com/IBM/ibm-generative-ai/pull/264>`_ [`@Tomas2D <https://github.com/Tomas2D>`_]
- ci: check if all tests have markers `#(265) <https://github.com/IBM/ibm-generative-ai/pull/265>`_ [`@jezekra1 <https://github.com/jezekra1>`_]

**Full Changelog**: `v2.0.0...v2.1.0 <https://github.com/IBM/ibm-generative-ai/compare/v2.0.0...v2.1.0>`_


🔗 API Endpoint Versions
^^^^^^^^^^^^^^^^^^^^^^^^

.. collapse:: API Endpoint Versions

    ========  ==================================  ======================
    Method    Path                                Version (YYYY-MM-DD)
    ========  ==================================  ======================
    GET       /v2/api_key                         2023-11-22
    POST      /v2/api_key/regenerate              2023-11-22
    GET       /v2/files                           2023-12-15
    POST      /v2/files                           2023-12-15
    DELETE    /v2/files/{id}                      2023-11-22
    GET       /v2/files/{id}                      2023-12-15
    GET       /v2/files/{id}/content              2023-11-22
    GET       /v2/models                          2023-11-22
    GET       /v2/models/{id}                     2024-01-30
    GET       /v2/prompts                         2024-01-10
    POST      /v2/prompts                         2024-01-10
    DELETE    /v2/prompts/{id}                    2023-11-22
    GET       /v2/prompts/{id}                    2024-01-10
    PATCH     /v2/prompts/{id}                    2024-01-10
    PUT       /v2/prompts/{id}                    2024-01-10
    GET       /v2/requests                        2023-11-22
    DELETE    /v2/requests/chat/{conversationId}  2023-11-22
    GET       /v2/requests/chat/{conversationId}  2023-11-22
    DELETE    /v2/requests/{id}                   2023-11-22
    GET       /v2/system_prompts                  2023-11-22
    POST      /v2/system_prompts                  2023-11-22
    DELETE    /v2/system_prompts/{id}             2023-11-22
    GET       /v2/system_prompts/{id}             2023-11-22
    PUT       /v2/system_prompts/{id}             2023-11-22
    GET       /v2/tasks                           2023-11-22
    POST      /v2/text/chat                       2024-01-10
    POST      /v2/text/chat/output                2024-01-10
    POST      /v2/text/chat_stream                2024-01-10
    POST      /v2/text/embeddings                 2023-11-22
    GET       /v2/text/embeddings/limits          2023-11-22
    GET       /v2/text/extraction/limits          2023-11-22
    POST      /v2/text/generation                 2024-01-10
    POST      /v2/text/generation/comparison      2023-11-22
    GET       /v2/text/generation/limits          2023-11-22
    POST      /v2/text/generation/output          2023-11-22
    GET       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation/{id}/feedback   2023-11-22
    PUT       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation_stream          2024-01-10
    POST      /v2/text/moderations                2023-11-22
    POST      /v2/text/tokenization               2024-01-10
    GET       /v2/tunes                           2023-11-22
    POST      /v2/tunes                           2023-11-22
    POST      /v2/tunes/import                    2023-11-22
    DELETE    /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}                      2023-11-22
    PATCH     /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}/content/{type}       2023-12-15
    GET       /v2/tuning_types                    2024-01-30
    DELETE    /v2/user                            2023-11-22
    GET       /v2/user                            2023-11-22
    PATCH     /v2/user                            2023-11-22
    POST      /v2/user                            2023-11-22
    ========  ==================================  ======================

v2.0.0 (2024-01-15)
-------------------

On November 22nd, 2023, the API (v2) was announced. We reflected this change on the Python SDK by rewriting its core to be faster, more reliable and mainly in sync with the API. The new SDK brings the concept of the central client, which gives you access to the API very straightforward. This concept was recently integrated into OpenAI SDK / Cohere SDK, and more are joining.

To seamlessly migrate from V0.X versions to 2.0, we have prepared the Migration Guide. The reborn documentation with a lot of examples will help you get started.

Here is a little sneak peek.


* Very Performant.
* Generated Typings directly from the API.
* Smart Requests Concurrency Handling.
* Retry Mechanism in case of network or API failure.
* Batching Large Requests automatically.
* Easy to extend.

**Full Changelog**: `v0.6.1...v2.0.0 <https://github.com/IBM/ibm-generative-ai/compare/v0.6.1...v2.0.0>`_

🔗 API Endpoint Versions
^^^^^^^^^^^^^^^^^^^^^^^^

.. collapse:: API Endpoint Versions

    ========  ==================================  ======================
    Method    Path                                Version (YYYY-MM-DD)
    ========  ==================================  ======================
    GET       /v2/api_key                         2023-11-22
    POST      /v2/api_key/regenerate              2023-11-22
    GET       /v2/files                           2023-12-15
    POST      /v2/files                           2023-12-15
    DELETE    /v2/files/{id}                      2023-11-22
    GET       /v2/files/{id}                      2023-12-15
    GET       /v2/files/{id}/content              2023-11-22
    GET       /v2/models                          2023-11-22
    GET       /v2/models/{id}                     2024-01-10
    GET       /v2/prompts                         2024-01-10
    POST      /v2/prompts                         2024-01-10
    DELETE    /v2/prompts/{id}                    2023-11-22
    GET       /v2/prompts/{id}                    2024-01-10
    PATCH     /v2/prompts/{id}                    2024-01-10
    PUT       /v2/prompts/{id}                    2024-01-10
    GET       /v2/requests                        2023-11-22
    DELETE    /v2/requests/chat/{conversationId}  2023-11-22
    GET       /v2/requests/chat/{conversationId}  2023-11-22
    DELETE    /v2/requests/{id}                   2023-11-22
    GET       /v2/tasks                           2023-11-22
    POST      /v2/text/chat                       2024-01-10
    POST      /v2/text/chat/output                2024-01-10
    POST      /v2/text/chat_stream                2024-01-10
    POST      /v2/text/embeddings                 2023-11-22
    GET       /v2/text/embeddings/limits          2023-11-22
    GET       /v2/text/extraction/limits          2023-11-22
    POST      /v2/text/generation                 2024-01-10
    POST      /v2/text/generation/comparison      2023-11-22
    GET       /v2/text/generation/limits          2023-11-22
    POST      /v2/text/generation/output          2023-11-22
    GET       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation/{id}/feedback   2023-11-22
    PUT       /v2/text/generation/{id}/feedback   2023-11-22
    POST      /v2/text/generation_stream          2024-01-10
    POST      /v2/text/moderations                2023-11-22
    POST      /v2/text/tokenization               2024-01-10
    GET       /v2/tunes                           2023-11-22
    POST      /v2/tunes                           2023-11-22
    POST      /v2/tunes/import                    2023-11-22
    DELETE    /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}                      2023-11-22
    PATCH     /v2/tunes/{id}                      2023-11-22
    GET       /v2/tunes/{id}/content/{type}       2023-12-15
    GET       /v2/tuning_types                    2023-11-22
    DELETE    /v2/user                            2023-11-22
    GET       /v2/user                            2023-11-22
    PATCH     /v2/user                            2023-11-22
    POST      /v2/user                            2023-11-22
    ========  ==================================  ======================

v0.6.1 (2023-12-20)
-------------------


* fix: correct llama-index import for new version by `@David-Kristek <https://github.com/David-Kristek>`_ in `#(243) <https://github.com/IBM/ibm-generative-ai/pull/243>`_
* fix(examples): correct Hugging Face example prompt by `@David-Kristek <https://github.com/David-Kristek>`_ in `#(244) <https://github.com/IBM/ibm-generative-ai/pull/244>`_
* fix: prevent duplicating template with same name by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(245) <https://github.com/IBM/ibm-generative-ai/pull/245>`_

**Full Changelog**: `v0.6.0...v0.6.1 <https://github.com/IBM/ibm-generative-ai/compare/v0.6.0...v0.6.1>`_


v0.6.0 (2023-12-08)
-------------------


* feat(extensions): add support for llamaindex by `@David-Kristek <https://github.com/David-Kristek>`_ in `#(238) <https://github.com/IBM/ibm-generative-ai/pull/238>`_
* fix: update aiohttp to support python 3.12 by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(239) <https://github.com/IBM/ibm-generative-ai/pull/239>`_
* fix: add missing **init**.py in package to fix broken import by `@jezekra1 <https://github.com/jezekra1>`_ in `#(241) <https://github.com/IBM/ibm-generative-ai/pull/241>`_
* fix: update maximal local concurrency limit based on API response by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(242) <https://github.com/IBM/ibm-generative-ai/pull/242>`_

New Contributors
^^^^^^^^^^^^^^^^


* `@jezekra1 <https://github.com/jezekra1>`_ made their first contribution in `#(241) <https://github.com/IBM/ibm-generative-ai/pull/241>`_

**Full Changelog**: `v0.5.1...v0.5.2 <https://github.com/IBM/ibm-generative-ai/compare/v0.5.1...v0.5.2>`_


v0.5.1 (2023-11-17)
-------------------

🐛 Bug fixes
^^^^^^^^^^^^


* Add missing rate-limit check for tokenize methods
* Unify error messages between sync and async methods

**Full Changelog**: `v0.5.0...v0.5.1 <https://github.com/IBM/ibm-generative-ai/compare/v0.5.0...v0.5.1>`_


v0.5.0 (2023-11-13)
-------------------

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Added integration for LangChain Chat Models; see an example of `generation <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/langchain_chat_generate.py>`_ and `streaming <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/langchain_chat_stream.py>`_.
* Added support for LangChain Model Serialization (saving and loading models); `see an example <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/langchain_serialization.py>`_.
* Added support for the Chat endpoint in ``Model`` class; see an `example <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/chat.py>`_.
* Added support for new moderation models (HAP, STIGMA, Implicit Hate) - not released on API yet but will be available soon.
* Added type validation for input_tokens property in generate response.
* Extend LangChain generation information / LLM Output (token_usage structure, generated tokens, stop_reason, conversation_id, created_at, ...).
* Add optional ``raw_response=True/False`` parameter to ``generate_stream`` / ``generate_as_complete`` and ``generate`` methods to receive a raw response instead of unwrapped results.

🐛 Bug fixes
^^^^^^^^^^^^^^^


* LangChain extension now correctly tokenizes the inputs (previously, the GPT2 tokenizer had been used).
* Improve general error handling.

**Full Changelog**: `v0.4.1...v0.5.0 <https://github.com/IBM/ibm-generative-ai/compare/v0.4.1...v0.5.0>`_


v0.4.1 (2023-10-27)
-------------------

🐛 Bug fixes
^^^^^^^^^^^^^^^


* Correctly handle file responses
* Use ``tqdm.auto`` instead of ``tqdm.tqdm`` to improve display in Jupyter Notebooks

**Full Changelog**: `v0.4.0...v0.4.1 <https://github.com/IBM/ibm-generative-ai/compare/v0.4.0...v0.4.1>`_


v0.4.0 (2023-10-24)
-------------------

⚠️ Switch to Pydantic V2
^^^^^^^^^^^^^^^^^^^^^^^^


* In case your application is dependent on Pydantic V1, refer to the `migration guide <https://docs.pydantic.dev/2.0/migration/>`_.
* If you cannot upgrade, stick to the previous version 0.3.2.

**Full Changelog**: `v0.3.2...v0.4.0 <https://github.com/IBM/ibm-generative-ai/compare/v0.3.2...v0.4.0>`_


v0.3.2 (2023-10-23)
-------------------

🐛 Bug fixes
^^^^^^^^^^^^^^^


* Correctly handle async errors and process abortion

🔧 Configuration Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Increase async generate/tokenize retry limits from 3 to 5

**Full Changelog**: `v0.3.1...v0.3.2 <https://github.com/IBM/ibm-generative-ai/compare/v0.3.1...v0.3.2>`_


v0.3.1 (2023-10-20)
-------------------

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Handle concurrency limits for ``generate`` and ``generate_as_completed`` methods.
* Add automatic handling of rate limits for the tokenize endpoint (tokenize_async method).
* Added ``stop_sequence`` parameter for generated output (non-empty token which caused the generation to stop) + added - ``include_stop_sequence`` parameter for the ``GenerateParams`` (it indicates whether the stop sequence (which caused the generation to stop) is part of the generated text. The default value depends on the model in use).
* Removed hidden ``stop_sequences`` removal inside the ``LangChainInterface``\ , which can now be controlled via the ``include_stop_sequence`` parameter.
* Improve general error handling + method signatures (improve Python typings).

🐛 Bug fixes
^^^^^^^^^^^^^^^


* Fix stacked progress bar (\ ``generate_async`` method)
* Handle cases when the package is used inside the ``asyncio`` environment
* Hide warning when an unknown field is retrieved in the generated response

**Full Changelog**: `v0.3.0...v0.3.1 <https://github.com/IBM/ibm-generative-ai/compare/v0.3.0...v0.3.1>`_


v0.3.0 (2023-10-12)
-------------------

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Added Hugging Face Agent support; see an `example <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/huggingface_agent.py>`_.
* Drastically improve the speed of ``generate_async`` method - the concurrency limit is now automatically inferred from the API. (custom setting of ``ConnectionManager.MAX_CONCURRENT_GENERATE`` will be ignored). In case you want to slow down the speed of generating, just pass the following parameter to the method: ``max_concurrency_limit=1``  or any other value.
* Increase the default tokenize processing limits from 5 requests per second to 10 requests per second (this will be increased in the future).

🐛 Bug fixes
^^^^^^^^^^^^^^^


* Throws on unhandled exceptions during the ``generate_async`` calls.
  Correctly cleanups the async HTTP clients when the task/calculation is being cancelled (for instance, you call generate_async in Jupyter - Notebook and then click the stop button). This should prevent receiving the ``Can't have two active async_generate_clients`` error.
* Fix async support for newer LangChain versions (\ ``>=0.0.300``\ )
* Fix LangChain PromptTemplate import warning in newer versions of LangChain
* Correctly handle server errors when streaming
* Fix ``tune_methods`` method


v0.2.8 (2023-09-25)
-------------------

🚀 Features / Enhancements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Added moderation support; now you can retrieve HAP for generated requests (\ `example <https://github.com/IBM/ibm-generative-ai/blob/main/examples/user/generate_with_moderation.py>`_\ )
* Internally improve streaming processing (poor or unstable internet connection)
* Internally improve server response parsing and error handling
* Add a user-agent header to distinguish Python SDK on the API

🐛 Bug fixes
^^^^^^^^^^^^^^^


* LangChain - correct handling of stop_sequences
* Correctly set versions of used dependencies (httpx / pyyaml)
* Prevents unexpected modifications to user's GenerateParams passed to the Model class
* Prevents unexpected errors when GenerateParams contains stream=True and generate (non-stream) version is called

🔧 Configuration changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Remove API version from the API endpoint string

**Full Changelog**: `v0.2.7...v0.2.8 <https://github.com/IBM/ibm-generative-ai/compare/v0.2.7...v0.2.8>`_


v0.2.7 (2023-09-15)
-------------------


* feat(langchain) - generate method by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(157) <https://github.com/IBM/ibm-generative-ai/pull/157>`_
* fix(params): do not strip special characters by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(153) <https://github.com/IBM/ibm-generative-ai/pull/153>`_
* fix: correct httpx dependency version by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(158) <https://github.com/IBM/ibm-generative-ai/pull/158>`_

**Full Changelog**: `v0.2.6...v0.2.7 <https://github.com/IBM/ibm-generative-ai/compare/v0.2.6...v0.2.7>`_


v0.2.6 (2023-09-11)
-------------------


* feat(langchain): add streaming support by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(144) <https://github.com/IBM/ibm-generative-ai/pull/144>`_
* feat(http): allow override httpx options by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(149) <https://github.com/IBM/ibm-generative-ai/pull/149>`_
* feat: add typical_p parameter by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(135) <https://github.com/IBM/ibm-generative-ai/pull/135>`_
* chore: update examples by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(136) <https://github.com/IBM/ibm-generative-ai/pull/136>`_
* docs: mention CLI in README by `@Tomas2D <https://github.com/Tomas2D>`_ in `#(143) <https://github.com/IBM/ibm-generative-ai/pull/143>`_
* chore: adding escapting of backslashes for re.sub value by `@assaftibm <https://github.com/assaftibm>`_ in `#(84) <https://github.com/IBM/ibm-generative-ai/pull/84>`_
* chore: correct README.md typo by `@ind1go <https://github.com/ind1go>`_ in `#(148) <https://github.com/IBM/ibm-generative-ai/pull/148>`_
* update schema for stop_sequences generate param by `@mirianfsilva <https://github.com/mirianfsilva>`_ in `#(142) <https://github.com/IBM/ibm-generative-ai/pull/142>`_

New Contributors
^^^^^^^^^^^^^^^^


* `@assaftibm <https://github.com/assaftibm>`_ made their first contribution in `#(84) <https://github.com/IBM/ibm-generative-ai/pull/84>`_
* `@ind1go <https://github.com/ind1go>`_ made their first contribution in `#(148) <https://github.com/IBM/ibm-generative-ai/pull/148>`_

**Full Changelog**: `v0.2.5...v0.2.6 <https://github.com/IBM/ibm-generative-ai/compare/v0.2.5...v0.2.6>`_


v0.2.5 (2023-08-21)
-------------------


* TOUs handling
* Update Pydantic version
* Update examples

**Full Changelog**: `v0.2.4...v0.2.5 <https://github.com/IBM/ibm-generative-ai/compare/v0.2.4...v0.2.5>`_


v0.2.4 (2023-08-01)
-------------------

Updated the documentation (imports of credentials)
Updated schemas for config
Added params in GeneratedParams
Updated examples
Updated tests


v0.2.3 (2023-07-24)
-------------------


* Remove ModelType enum
* Add utils for Model class: listing, info, available, etc.
* Pydantic model allows extra params
* Tests


v0.2.2 (2023-07-11)
-------------------

Documentation Updates.


v0.2.1 (2023-07-10)
-------------------

Documentation update
Example update


v0.2.0 (2023-07-10)
-------------------

Model Tuning
File manager
Tuning Manager
ModelType deprecation warning
Open Source documentation update


v0.1.19 (2023-06-30)
--------------------

Fixed pydantic version issue


v0.1.18 (2023-06-30)
--------------------

Watsonx Templating support
Documentation and examples' update
Parameters updated for upstream compatibility with sampling method
Retry mechanism update


v0.1.17 (2023-06-23)
--------------------


* Modifications to examples/tests to avoid sampling-related parameters with greedy decoding
* Updates to build process
* Modifications to error messages


v0.1.16 (2023-06-21)
--------------------


* Documentation update
* Local server example
* Open source contributions information
* Example endpoints updated


v0.1.15 (2023-06-08)
--------------------


* 🔨 GitHub Workflows
* ✨ Progress bar in async_generate function
* 🐛 Updating Terms of Use to use PATCH
* 🎨 Adding accessors attribute to model class
* ✨Search Space example and utils
* ✨ Localserver Extension
