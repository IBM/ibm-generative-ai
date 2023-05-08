import os
import pathlib
import random

import requests

import genai.extensions.huggingface  # noqa
from genai.prompt_pattern import PromptPattern

#
# Adult dataset in the following example was obtained from UCI Machine
# Learning repository. The full Bibtex citation is as follows:
#
# @misc{Dua:2019 ,
# author = "Dua, Dheeru and Graff, Casey",
# year = "2017",
# title = "{UCI} Machine Learning Repository",
# url = "http://archive.ics.uci.edu/ml",
# institution = "University of California, Irvine, School of Information and Computer Sciences" }


def get_dataset(datafile):
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"

    if os.path.exists(datafile):
        print("Data already downloaded. Skipping the download.")
        return
    with requests.get(url) as response:
        print("Saving data to {}".format(datafile))
        # Add data
        with open(datafile, "ab") as f:
            f.write(response.content)


datafile = os.path.join(pathlib.Path(__file__).parent.absolute(), "adult.data.csv")
get_dataset(datafile)

# flake8: noqa
template = """
    The age of the individual is {{0}}.
    The workclass of the individual is {{1}}.
    The estimate of the number of individuals in the population with the same demographics as the individual was {{2}}.
    The numeric form of the highest education level they achieved was {{4}}.
    The marital status of the individual was {{5}}.
    The occupation of the individual was {{6}}.
    The relationship status of the individual is {{7}}.
    The race of the individual was {{8}}.
    The sex of the individual is {{9}}.
    The capital gain they had in the previous year was {{10}}.
    The capital loss they had in the previous year was {{11}}.
    The number of hours worked per week was {{12}}.
    The native country of the individual was {{13}}.
"""


prompt = PromptPattern.from_str(template)

list_of_prompts = prompt.sub_all_from_csv(csv_path=datafile, col_to_var="infer", headers=False)

print("-----------------------")
print("Generated prompts: \n total number {}".format(len(list_of_prompts)))
print("Sample prompt: {}".format(list_of_prompts[random.randint(0, len(list_of_prompts) - 1)]))
print("-----------------------")

prompt.huggingface.save_dataset(list_of_prompts, "<path-to-your-folder>")
