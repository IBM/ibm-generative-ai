import csv
import os
import pathlib
import random

import requests

# Either import genai.extensions.langchain or import specific
# class from langchain extension for PromptInterface to register
import genai.extensions.langchain
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


def get_dataset(datafile, headers=None):
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"

    if os.path.exists(datafile):
        print("Data already downloaded. Skipping the download.")
        return
    with requests.get(url) as response:
        print("Saving data to {}".format(datafile))
        # Add header
        if headers is not None:
            with open(datafile, "w", newline="") as f:
                csv.writer(f).writerow(headers)
        # Add data
        with open(datafile, "ab") as f:
            f.write(response.content)


headers = [
    "age",
    "workclass",
    "demographic",
    "education_str",
    "education",
    "marital_status",
    "occupation",
    "relationship_status",
    "race",
    "sex",
    "capital_gain",
    "capital_loss",
    "work_hours_per_week",
    "native_country",
    "salary",
]
datafile = os.path.join(pathlib.Path(__file__).parent.absolute(), "adult.header.data.csv")
get_dataset(datafile, headers=headers)

# flake8: noqa
pattern = """
    The age of the individual is {{age}}.
    The workclass of the individual is {{workclass}}.
    The estimate of the number of individuals in the population with the same demographics as the individual was {{demographic}}.
    The numeric form of the highest education level they achieved was {{education}}.
    The string form of the highest education level they achieved was {{education_str}}.
    The marital status of the individual was {{marital_status}}.
    The occupation of the individual was {{occupation}}.
    The relationship status of the individual is {{relationship_status}}.
    The race of the individual was {{race}}.
    The sex of the individual is {{sex}}.
    The capital gain they had in the previous year was {{capital_gain}}.
    The capital loss they had in the previous year was {{capital_loss}}.
    The number of hours worked per week was {{work_hours_per_week}}.
    The native country of the individual was {{native_country}}.
    The salary of this individual was {{salary}}.
"""


prompt_pattern = PromptPattern.from_str(pattern)

print("\nGiven pattern:\n", prompt_pattern)

prompts = prompt_pattern.sub_all_from_csv(csv_path=datafile, col_to_var="infer")

print("-----------------------")
print("Generated prompts: \n total number {}".format(len(prompts)))
print("Sample prompt: {}".format(prompts[random.randint(0, len(prompts) - 1)]))
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# Langchain raw string templates are created as
# PromptTemplate(input_vars=[variable list], template=raw_string).
# In the following example, this template gets created automatically
# from genai PromptPattern using langchain extension.
# Langchain PromptTemplates are substituted with variable values as
# template.format(variable1=val1, variable2=val2, ....)
# In the following example, when we read csv using DictReader, each
# line gets read as a dictionary {column1: val, column2: val, ...}.
# We use ** operator in python to feed this dictionary to format
# the langchain template as template.format(**line)

print("Translating prompt pattern to langchain template")
template = prompt_pattern.langchain.as_template()
print("Generated langchain template = ", template)
prompts = []
with open(datafile, "r") as fin:
    reader = csv.DictReader(fin)
    for line in reader:
        if len(line) < len(headers):
            continue
        prompts.append(template.format(**line))  # **operator converts dict into key-val args

print("-----------------------")
print("Generated prompts: \n total number {}".format(len(prompts)))
print("Sample prompt: {}".format(prompts[random.randint(0, len(prompts) - 1)]))
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

# In the following snippet, we create a genai PromptPattern from
# a langchain PromptTemplate using langchain extension of genai.
print("Translating langchain template back to prompt pattern")
prompt_pattern = PromptPattern.langchain.from_template(template)
prompts = prompt_pattern.sub_all_from_csv(csv_path=datafile, col_to_var="infer")
print("-----------------------")
print("Generated prompts: \n total number {}".format(len(prompts)))
print("Sample prompt: {}".format(prompts[random.randint(0, len(prompts) - 1)]))
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
