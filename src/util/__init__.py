import yaml 
from src.exception import CustomException
from src.logger import logging
import os,sys

def read_yaml_file(file_path:str) -> dict:
    """
    Reads a YAML file and returns the contents as a dictionary 
    args - file_path:str
    """
    try:
        with open(file_path , "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise CustomException(e, sys) from e
        