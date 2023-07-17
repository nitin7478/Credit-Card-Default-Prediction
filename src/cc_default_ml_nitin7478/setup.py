from setuptools import setup,find_packages
from typing import List
#Declaring variables for setup functions
PROJECT_NAME="Credit Card Default Prediction"
VERSION="0.0.6"
AUTHOR="Nitin Udmale"
DESRCIPTION="This is my first Modular Coding Project"

REQUIREMENT_FILE_NAME="requirements.txt"

HYPHEN_E_DOT = "-e ."



# def get_requirements_list(file_path:str) -> List[str]:
#     """
#     Description: This function is going to return list of requirement
#     mention in requirements.txt file, list of libraries.
#     """
#     with open(file_path, 'rb') as file:
#         raw_data = file.read()
#         encoding = chardet.detect(raw_data)['encoding']
#         print(encoding)
#     with open(file_path, 'r', encoding=encoding) as file:
#         requirements = file.read().splitlines()
#         if HYPHEN_E_DOT in requirements:
#             requirements.remove(HYPHEN_E_DOT)
#     return requirements

def get_requirements_list(file_path:str) -> List[str]:
    """
    Description: This function is going to return list of requirement
    mention in requirements.txt file, list of libraries.
    """
    with open(file_path ,'r', encoding = 'utf-16') as requirement_file:
        requirement_list = requirement_file.readlines()
        requirement_list = [requirement_name.replace("\n", "") for requirement_name in requirement_list]
        if HYPHEN_E_DOT in requirement_list:
            requirement_list.remove(HYPHEN_E_DOT)
        return requirement_list


# def read_requirements_file(file_path):
#     with open(file_path, 'rb') as file:
#         raw_data = file.read()
#         encoding = chardet.detect(raw_data)['encoding']
    
#     with open(file_path, 'r', encoding=encoding) as file:
#         requirements = file.read().splitlines()
#     return requirements



setup(
name=PROJECT_NAME,
version=VERSION,
author=AUTHOR,
description=DESRCIPTION,
packages=find_packages(), 
install_requires=get_requirements_list(REQUIREMENT_FILE_NAME)
)
