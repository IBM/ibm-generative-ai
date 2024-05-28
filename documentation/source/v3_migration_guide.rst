V3 Migration Guide
==================

.. contents::
   :local:
   :class: this-will-duplicate-information-and-it-is-still-useful-here

.. admonition:: V1 to V2 migration
   :class: tip

   If you are still on V1 please see the `V2 Migration Guide <v2_migration_guide>` first.

What has changed?
-----------------

- We have simplified and improved moderations.
- All Schemas were moved to a single place and should now be imported from ``genai.schema`` module.
- Some schemas were renamed for better readability.

Moderations
-----------
- Stigma (``ModerationStigma`` class) has been replaced by Social Bias (``ModerationSocialBias`` class).
- Implicit Hate (``ModerationImplicitHate`` class) has been replaced by Social Bias (``ModerationSocialBias`` class).
- You can now set a different threshold for input and output moderations.
- Text generation response ``moderation`` was renamed to ``moderations``:

  ``TextChatStreamCreateResponse.moderation`` -> ``TextChatStreamCreateResponse.moderations``
  ``TextGenerationStreamCreateResponse.moderation`` -> ``TextGenerationStreamCreateResponse.moderations``
  ``TextGenerationResult.moderation`` -> ``TextGenerationResult.moderations``

❌ Old Way

.. code:: python

    from genai.schema import ModerationHAP, ModerationStigma, ModerationImplicitHate, ModerationParameters

    for response in client.text.generation.create(
        model_id="google/flan-t5-xl",
        inputs=["What is a molecule?", "What is NLP?"],
        moderations=ModerationParameters(
            hap=ModerationHAP(input=True, output=True, threshold=0.8),
            stigma=ModerationStigma(input=True, output=True, threshold=0.8),
            implicit_hate=ModerationImplicitHate(input=True, output=True, threshold=0.8),
        )
    ):
        for result in response.results:
            moderation = result.moderation


✅ New Way

.. code:: python

    from genai.schema import (
        ModerationHAP,
        ModerationHAPInput,
        ModerationHAPOutput,
        ModerationParameters,
        ModerationSocialBias,
        ModerationSocialBiasInput,
        ModerationSocialBiasOutput,
    )

    for response in client.text.generation.create(
        model_id="google/flan-t5-xl",
        inputs=["what is a molecule?", "what is nlp?"],
        moderations=moderationparameters(
            hap=moderationhap(
                input=moderationhapinput(enabled=true, threshold=0.8),
                output=moderationhapoutput(enabled=true, threshold=0.8),
            ),
            social_bias=moderationsocialbias(
                input=moderationsocialbiasinput(enabled=true, threshold=0.8),
                output=moderationsocialbiasoutput(enabled=true, threshold=0.8),
            ),
        )
    ):
        for result in response.results:
            moderation = result.moderations



Imports
-------

- It is no longer to import schemas from submodules, use ``from genai.schema import ...``

❌ Old Way

.. code:: python

    from genai.text.generation import DecodingMethod


✅ New Way

.. code:: python

    from genai.schema import DecodingMethod

📝 Other changes
----------------

- Deprecate ``TuningType`` enum; use values from ``client.tune.types()`` method.

- Following schemas or their properties were renamed:
    - `UserPromptResult` -> `PromptResult`
    - `PromptsResponseResult` -> `PromptResult`
    - `UserResponseResult` -> `UserResult`
    - `UserCreateResultApiKey` -> `UserApiKey`
    - `PromptRetrieveRequestParamsSource` -> `PromptListSource`
    - `BaseMessage.file_ids` -> `BaseMessage.files`
