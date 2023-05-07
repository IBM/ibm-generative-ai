import os
import pathlib
import random

from genai.prompt_pattern import PromptPattern

PATH = pathlib.Path(__file__).parent.resolve()

pt = PromptPattern.from_str(
    """
    Instruction: {{instruction}}
    Input: {{input}}
    Output: {{output}}
"""
)
print("\nGiven template:\n", pt)

json_path = str(PATH) + os.sep + "assets" + os.sep + "seed_tasks.json"

list_of_prompts = pt.sub_all_from_json(json_path=json_path, key_to_var="infer")

print("-----------------------")
print("Generated prompts: \n total number {}".format(len(list_of_prompts)))
print("Sample prompt: {}".format(list_of_prompts[random.randint(0, len(list_of_prompts) - 1)]))
print("-----------------------")
