Quick Start
=================================

What is a prompt?
---------------------------

Generally, models take "prompts" as input. With genai, PromptPattern provides a flexible approach to creating prompts from general
templates.


Common use case
-----------------------------------------

Say you have a json or csv file which contains data you want to use to generate an array of prompts to feed your model.
Using the :ref:`prompts-pattern` class, you can easily substitute your template's variables with data from a file, generating
one or multiple prompts.

Sequential substitution
^^^^^^^^^^^^^^^^^^^^^^^^^^

Here, we want to **sequentially substitute** the synth-animal.yaml template's variables with the data comming from penguins.csv, and generate **as
many prompts as possible** using the data.

A crucial step is to provide the mapping between the template's variables and the csv's column names.


Assuming local :ref:`synth-animal.yaml<File : synth-animal.yaml>` and :ref:`penguins.csv<File : penguins.csv>` and files.

..  code-block:: python
    :caption: Multiple Prompt Patterns using complete file

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

    print("-----------------------")
    print("generated prompt")
    print(list_of_prompts)
    print(len(list_of_prompts))
    print("-----------------------")

    responses = bloomz.generate_as_completed(list_of_prompts)
    for response in responses:
        # do something with response.generated_text


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
    [Please generate synthetic data about penguins.
    1,Adelie,Torgersen,181,2007
    2,Adelie,Torgersen,186,2007
    3,Adelie,Torgersen,195,2007
    4,
    , Please generate synthetic data about penguins.
    1,Adelie,Torgersen,NA,2007
    2,Adelie,Torgersen,193,2007
    3,Adelie,Torgersen,190,2007
    4,
    ...
    , Please generate synthetic data about penguins.
    1,Chinstrap,Dream,207,2009
    2,Chinstrap,Dream,202,2009
    3,Chinstrap,Dream,193,2009
    4,
    ]
    114
    -----------------------


Sampling substitution
^^^^^^^^^^^^^^^^^^^^^^^^^^

Here, we want to **sample random data** from tasks.jsonl to substiture the instruction.yaml template's variables. We want to get a list of **5 prompts**.

Again, a crucial step is to provide the mapping between the template's variables and the json's keys.

Assuming local :ref:`instruction.yaml<File : instruction.yaml>` and :ref:`tasks.jsonl<File : tasks.jsonl>` and files.

..  code-block:: python
    :caption: 5 Prompt Patterns using complete file

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
        strategy="sample",
        n=5
    )

    print("-----------------------")
    print("generated prompt")
    print(list_of_prompts)
    print(len(list_of_prompts))
    print("-----------------------")


    responses = bloomz.generate_as_completed(list_of_prompts)
    for response in responses:
        # do something with response.generated_text


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
    [1. Instruction: Find out the largest one from a set of numbers. Output the number directly.
    1. Input: {1001, 22, 500, -3999, 1e6, 85, -2e6}
    1. Output: 1e6

    2. Instruction: What is the relation between the given pairs?
    2. Input: Night : Day :: Right : Left
    2. Output: The relation between the given pairs is that they are opposites.

    3. Instruction:

    ...

    1. Instruction: Rank these countries by their population.
    1. Input: Brazil, China, US, Japan, Canada, Australia
    1. Output: China, US, Brazil, Japan, Canada, Australia

    2. Instruction: Find the four smallest perfect numbers.
    2. Input:
    2. Output: 6, 28, 496, and 8128

    3. Instruction:
    ]
    5
    -----------------------



Random substitution for synthetic data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here, we want to **randomly substitute** the synth-animal.yaml template's variables with values from penguins.csv, and generate **10 000 prompts**. Since the each created prompts are a synthesis of multiple
different rows from the csv, we can create as prompts as we want.

Again, a crucial step is to provide the mapping between the template's variables and the csv's column names, as well as the number of prompts we want to get.


Assuming local :ref:`synth-animal.yaml<File : synth-animal.yaml>` and :ref:`penguins.csv<File : penguins.csv>` and files.

..  code-block:: python
    :caption: Multiple Prompt Template using complete file

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
        n=10000
    )

    print("-----------------------")
    print("generated prompt")
    print(list_of_prompts)
    print(len(list_of_prompts))
    print("-----------------------")

    responses = bloomz.generate_as_completed(list_of_prompts)
    for response in responses:
        # do something with response.generated_text


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
    [Please generate synthetic data about penguins.
    1,Adelie,Dream,210,2007
    2,Gentoo,Torgersen,210,2007
    3,Gentoo,Biscoe,215,2007
    4,
    , Please generate synthetic data about penguins.
    1,Adelie,Dream,191,2007
    2,Gentoo,Biscoe,211,2009
    3,Chinstrap,Dream,201,2008
    4,
    ...
    , Please generate synthetic data about penguins.
    1,Gentoo,Torgersen,215,2007
    2,Chinstrap,Dream,210,2009
    3,Adelie,Biscoe,217,2008
    4,
    ]
    10000
    -----------------------
