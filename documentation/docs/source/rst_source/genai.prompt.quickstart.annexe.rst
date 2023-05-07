
Annexe
=======

File : capital-qa.yaml
------------------------

..  code-block:: yaml

    apiVersion: v0
    name: captial-qa
    content: |
        Country: Germany
        Capital: Berlin
        Country: USA
        Capital: Washington
        Country: {{country}}
        Capital:

File : synth-animal.yaml
-------------------------

.. code-block:: yaml

    apiVersion: v0
    name: synth-animal
    content: |
    Please generate synthetic data about {{animal}}.
    1,{{species1}},{{location1}},{{length1}},{{dob1}}
    2,{{species2}},{{location2}},{{length2}},{{dob2}}
    3,{{species3}},{{location3}},{{length3}},{{dob3}}
    4,

File : penguins.csv
---------------------

..  code-block:: text

    "","species","island","bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g","sex","year"
    "1","Adelie","Torgersen",39.1,18.7,181,3750,"male",2007
    "2","Adelie","Torgersen",39.5,17.4,186,3800,"female",2007
    "3","Adelie","Torgersen",40.3,18,195,3250,"female",2007
    "4","Adelie","Torgersen",NA,NA,NA,NA,NA,2007
    "5","Gentoo","Biscoe",36.7,19.3,193,3450,"female",2007
    "6","Gentoo","Biscoe",39.3,20.6,190,3650,"male",2007
    ...
    "341","Chinstrap","Dream",43.5,18.1,202,3400,"female",2009
    "342","Chinstrap","Dream",49.6,18.2,193,3775,"male",2009
    "343","Chinstrap","Dream",50.8,19,210,4100,"male",2009
    "344","Chinstrap","Dream",50.2,18.7,198,3775,"female",2009


File : instruction.yaml
-------------------------

..  code-block:: yaml

    apiVersion: v0
    name: instruction
    content: |
        1. Instruction: {{instruction1}}
        1. Input: {{input1}}
        1. Output: {{output1}}

        2. Instruction: {{instruction2}}
        2. Input: {{input2}}
        2. Output: {{output2}}

        3. Instruction:


File : tasks.jsonl
-------------------------

..  code-block:: json

    {"id": "seed_task_0", "name": "breakfast_suggestion", "instruction": "Is there anything I can eat for a breakfast that doesn't include eggs, yet includes protein, and has roughly 700-1000 calories?", "instances": [{"input": "", "output": "Yes, you can have 1 oatmeal banana protein shake and 4 strips of bacon. The oatmeal banana protein shake may contain 1/2 cup oatmeal, 60 grams whey protein powder, 1/2 medium banana, 1tbsp flaxseed oil and 1/2 cup watter, totalling about 550 calories. The 4 strips of bacon contains about 200 calories."}], "is_classification": false},
    {"id": "seed_task_1", "name": "antonym_relation", "instruction": "What is the relation between the given pairs?", "instances": [{"input": "Night : Day :: Right : Left", "output": "The relation between the given pairs is that they are opposites."}], "is_classification": false},
    {"id": "seed_task_2", "name": "one_sentence_description", "instruction": "Generate a one-sentence description for each of the following people.", "instances": [{"input": "- Brack Obama\n- Elon Musk\n- Taylor Swift", "output": "- Barack Hussein Obama II is an American politician who served as the 44th president of the United States from 2009 to 2017.\n- Elon Musk is the founder, CEO, and chief engineer of SpaceX; angel investor, CEO and product architect of Tesla, Inc.; founder of The Boring Company; co-founder of Neuralink and OpenAI; president of the Musk Foundation; and owner and CEO of Twitter, Inc.\n- Taylor Alison Swift is an American singer-songwriter."}], "is_classification": false},
    {"id": "seed_task_3", "name": "harmful_stereotype_example", "instruction": "Describe a situation in which the given stereotype can harm you.", "instances": [{"input": "\"All Asians are smart!\"", "output": "Imagine you're a small child of Asian descent. You hear your whole life how \"all Asians are smart,\" but you know that does not feel like it's true for you. You have a hard time in school. Reading is difficult. Math is impossible. Everyone around you seems to pressure you because you are supposed to be \"smart.\" Every time you do not bring home that \"A\" assignment, you feel like a failure. Like you alone missed out on the gene that makes \"all Asians smart.\"\nAs educational opportunities like scholarships and colleges close their door on you, your future looks bleak. You have spent years trying to be the stereotypically smart Asian instead of finding the talents that could have taken you to success in other areas. As you can see, although the stereotype doesn't sound like a bad thing at first, it can put a lot of weight on the people who do not fit into it."}], "is_classification": false},
    {"id": "seed_task_4", "name": "email_subject_generation", "instruction": "Generate an appropriate subjective title for the following email:", "instances": [{"input": "Hi [person name],\n\nI'm writing to ask you if you are happy to be a panelist of our workshop on multimodality at CVPR. The workshop will be held on June 20, 2023. \n\nBest,\n[my name]", "output": "Invitition to be a panelist for CVPR 2023 workshop on Multimodality"}], "is_classification": false},
    {"id": "seed_task_5", "name": "interview_question_answering", "instruction": "How do you answer this question in a job interview?", "instances": [{"input": "What do you think about when you are alone in a car?", "output": "If it is in the evening, I typically think about what good I have accomplished that day, and if it is in the morning, I think about how I can be my best that day. I also try to practice gratitude and live in the present moment while I'm driving to avoid distractions."}], "is_classification": false},
    {"id": "seed_task_6", "name": "new_year's_resolutions", "instruction": "Brainstorm a list of possible New Year's resolutions.", "instances": [{"input": "", "output": "- Lose weight\n- Exercise more\n- Eat healthier\n- Quit smoking\n- Drink less alcohol\n- Spend less money\n- Save more money\n- Get out of debt\n- Take a trip\n- Volunteer more\n- Spend more time with family and friends\n- Read more\n- Start a hobby\n- Get organized\n- Simplify your life\n- Meditate or pray more\n- Get a new job\n- Move to a new city\n- Make new friends\n- Go back to school\n- Learn a new language\n- Start a business"}], "is_classification": false}
