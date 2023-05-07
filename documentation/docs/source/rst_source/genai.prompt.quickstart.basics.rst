Basic Concepts
=================================


Creating a simple prompt from a template
-----------------------------------------
A prompt pattern can be created using the :ref:`prompts-pattern` class. It can be created from a string,
a file, or a url.

From string
^^^^^^^^^^^^^
..  code-block:: python
    :caption: Prompt Pattern from string

    from genai.prompt_pattern import PromptPattern

    _string = """
        The capital of {{country}} is {{capital}}. The capital of Taiwan is
    """

    prompt = PromptPattern.from_str(_string)
    prompt.sub("country", "Spain").sub("capital", "Madrid")

    # The capital of Spain is Madrid. The capital of Taiwan is


From file
^^^^^^^^^^^^^

Assuming a local :ref:`capital-qa.yaml<File : capital-qa.yaml>` file.

..  code-block:: python
    :caption: Prompt Pattern from file

    from genai.prompt_pattern import PromptPattern

    _path_to_file = "my_templates/capital-qa.yaml"

    prompt = PromptPattern.from_file(_path_to_file)
    prompt.sub("country", "Canada")


From a URL
^^^^^^^^^^^^^

Assuming :ref:`capital-qa.yaml<File : capital-qa.yaml>`, a file hosted on Github.

..  code-block:: python
    :caption: Prompt Pattern from URL

    from genai.prompt_pattern import PromptPattern

    _url_to_file = "https://raw.github.com/my_template/capital-qa.yaml"
    _github_token = "my-github-token"

    prompt = PromptPattern.from_file(
        url=_url_to_file,
        token=_github_token
    )
    prompt.sub("country", "Canada")



Template substitutions using data from file
--------------------------------------------
Once your prompt has been created, you might want to populate it from various sources. You can either
directly substitute the **{{var}}** with a passed string (as displayed in the above examples), or you can substitute
the variables using values pulled from a csv file or a json file.

Please refere to :ref:`prompts-pattern` for an indepth look at the offered methods.

.. note::

    There are 3 strategies that can be used to populate a template from a csv or json file:

    - **Sequential** : sequentially substitute the template's variables from a csv or json, starting from a given index.

    - **Sample**     : randomly samples rows from a csv or json and instantiate prompts. Without repetition of the data.

    - **Random**     : for each prompt variable, substitute the value from the corresponding key at random from csv or json.


From csv
^^^^^^^^^

Assuming local :ref:`synth-animal.yaml<File : synth-animal.yaml>` and :ref:`penguins.csv<File : penguins.csv>` and files.

..  code-block:: python
    :caption: Substitute the template variables from a sampled row

    from genai.prompt_pattern import PromptPattern

    _path_to_template_file = "my_templates/synth-animal.yaml"
    _path_to_csv_file = "my_data/penguins.csv"

    prompt = PromptPattern.from_file(_path_to_template_file)
    print("\nGiven template:\n", prompt)

    prompt.sub("animal", "penguins")

    mapping = {
        "species": ["species1", "species2", "species3"],
        "island": ["location1", "location2", "location3"],
        "flipper_length_mm": ["length1", "length2", "length3"],
        "year": ["dob1", "dob2", "dob3"],
    }
    prompt.sub_from_csv(
        csv_path=cvs_path,
        col_to_var=mapping,
        strategy="sample"
    )

    print("-----------------------")
    print("generated prompt")
    print(pt)
    print("-----------------------")


..  code-block:: console
    :caption: Output

    Given template:
    Please generate synthetic data about {{animal}}.
    1,{{species1}},{{location1}},{{length1}},{{dob1}}
    2,{{species2}},{{location2}},{{length2}},{{dob2}}
    3,{{species3}},{{location3}},{{length3}},{{dob3}}
    4,

    -----------------------
    generated prompt
    Please generate synthetic data about penguins.
    1,Gentoo,Biscoe,215,2008
    2,Gentoo,Biscoe,217,2009
    3,Chinstrap,Dream,198,2007
    4,


From json and jsonl
^^^^^^^^^^^^^^^^^^^^

Assuming local :ref:`instruction.yaml<File : instruction.yaml>` and :ref:`tasks.jsonl<File : tasks.jsonl>` and files.

..  code-block:: python
    :caption: Prompt Pattern

    from genai.prompt_pattern import PromptPattern

    _path_to_template_file = "my_templates/instruction.yaml"
    _path_to_json_file = "my_data/tasks.jsonl"

    prompt = PromptPattern.from_file(_path_to_template_file)
    print("\nGiven template:\n", prompt)

    mapping = {
        "instruction": ["instruction1", "instruction2"],
        "input": ["input1", "input2"],
        "output": ["output1", "output2"],
    }

    prompt.sub_from_json(
        json_path=_path_to_json_file,
        key_to_var=mapping,
        strategy="linear"
    )

    print("-----------------------")
    print("generated prompt")
    print(prompt)
    print("-----------------------")

.. code-block:: console
    :caption: Output

    Given template:
    1. Instruction: {{instruction1}}
    1. Input: {{input1}}
    1. Output: {{output1}}

    2. Instruction: {{instruction2}}
    2. Input: {{input2}}
    2. Output: {{output2}}

    3. Instruction:

    -----------------------
    generated prompt
    1. Instruction: Is there anything I can eat for a breakfast that doesn't include eggs, yet includes protein, and has roughly 700-1000 calories?
    1. Input:
    1. Output: Yes, you can have 1 oatmeal banana protein shake and 4 strips of bacon. The oatmeal banana protein shake may contain 1/2 cup oatmeal, 60 grams whey protein powder, 1/2 medium banana, 1tbsp flaxseed oil and 1/2 cup watter, totalling about 550 calories. The 4 strips of bacon contains about 200 calories.

    2. Instruction: What is the relation between the given pairs?
    2. Input: Night : Day :: Right : Left
    2. Output: The relation between the given pairs is that they are opposites.

    3. Instruction:

    -----------------------



Building multiple prompts from a file
---------------------------------------

There is a chance you might want to use a template to generate multiple prompts, based off of a csv file or a json file.

Generating multiple random prompts from csv
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming local :ref:`synth-animal.yaml<File : synth-animal.yaml>` and :ref:`penguins.csv<File : penguins.csv>` and files.

..  code-block:: python
    :caption: Multiple Prompt Pattern using complete file

    from genai.prompt_pattern import PromptPattern

    _path_to_template_file = "my_templates/synth-animal.yaml"
    _path_to_csv_file = "my_data/penguins.csv"

    prompt = PromptPattern.from_file(_path_to_template_file)
    print("\nGiven template:\n", prompt)

    prompt.sub("animal", "penguins")
    mapping = {
        "species": ["species1", "species2", "species3"],
        "island": ["location1", "location2", "location3"],
        "flipper_length_mm": ["length1", "length2", "length3"],
        "year": ["dob1", "dob2", "dob3"],
    }

    list_of_prompts = prompt.sub_all_from_csv(
        csv_path=_path_to_csv_file,
        col_to_var=mapping,
    )

Assuming local :ref:`synth-animal.yaml<File : synth-animal.yaml>` and :ref:`penguins.csv<File : penguins.csv>` and files.

..  code-block:: python
    :caption: 10 Randomly Generate Prompt Patterns

    from genai.prompt_pattern import PromptPattern

    _path_to_template_file = "my_templates/synth-animal.yaml"
    _path_to_csv_file = "my_data/penguins.csv"

    prompt = PromptPattern.from_file(_path_to_template_file)
    print("\nGiven template:\n", prompt)

    prompt.sub("animal", "penguins")
    mapping = {
        "species": ["species1", "species2", "species3"],
        "island": ["location1", "location2", "location3"],
        "flipper_length_mm": ["length1", "length2", "length3"],
        "year": ["dob1", "dob2", "dob3"],
    }

    list_of_prompts = prompt.sub_from_csv(
        csv_path=_path_to_csv_file,
        col_to_var=mapping,
        strategy="random",
        n=10
    )

Generating multiple random prompts from json
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

..  code-block:: python
    :caption: Multiple Prompt Patterns using complete file

    from genai.prompt_pattern import PromptPattern

    _path_to_template_file = "my_templates/instruction.yaml"
    _path_to_json_file = "my_data/tasks.jsonl"

    prompt = PromptPattern.from_file(_path_to_template_file)
    print("\nGiven template:\n", prompt)

    mapping = {
        "instruction": ["instruction1", "instruction2"],
        "input": ["input1", "input2"],
        "output": ["output1", "output2"],
    }

    list_of_prompts = prompt.sub_all_from_json(
        json_path=_path_to_json_file,
        key_to_var=mapping
    )

..  code-block:: python
    :caption: 10 Randomly Generated Prompt Patterns

    from genai.prompt_pattern import PromptPattern

    _path_to_template_file = "my_templates/instruction.yaml"
    _path_to_json_file = "my_data/tasks.jsonl"

    prompt = PromptPattern.from_file(_path_to_template_file)
    print("\nGiven template:\n", prompt)

    mapping = {
        "instruction": ["instruction1", "instruction2"],
        "input": ["input1", "input2"],
        "output": ["output1", "output2"],
    }

    list_of_prompts = prompt.sub_from_json(
        json_path=_path_to_json_file,
        key_to_var=mapping,
        strategy="random",
        n=10
    )
