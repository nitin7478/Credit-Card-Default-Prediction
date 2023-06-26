import yaml 
from src.exception import CustomException
from src.logger import logging
import os,sys
from src.constant import *
import pandas as pd
import numpy as np
import dill


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


def load_data(file_path : str, schema_file_path: str) -> pd.DataFrame:
    """
    loads file data and returns dataframe
    file_path : location of file 
    schema_file_path : location of schema file path 
    """
    try:
        logging.info("Starting load data and return df for file path {file_path} from data_transformation")
        dataset_schema = read_yaml_file(schema_file_path)
        schema = dataset_schema[SCHEMA_VALIDATION_COLUMNS_KEY]
        dataframe = pd.read_csv(file_path)
        
        for column in dataframe.columns:
            if column in list(schema.keys()):
                dataframe[column].astype(schema[column])
            else:
                raise Exception(f"{column} not in schema")
        logging.info("Successful load data for file path and return df {file_path} from data_transformation")
        return dataframe
    except Exception as e:
        raise CustomException(e, sys) from e

def save_numpy_array_data(file_path: str , array:np.array):
    """
    Save numpy array data to file 
    file_path : str location of file to save 
    array: np.array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path , exist_ok= True)
        with open(file_path,'wb') as file_obj:
            np.save(file_obj , array)
        logging.info(f"transformed np. array data saved to file path {file_path}")
    except Exception as e:
        raise CustomException(e,sys) from e

def load_numpy_array_data(file_path:str)->np.array:
    """
    load numpy array data from file 
    file_path: str location of file to load
    return: np.array data loaded
    """
    try:
        with open(file_path, 'rb') as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise CustomException(e, sys) from e


def save_object(file_path:str,obj):
    """
    file_path: str
    obj: Any sort of object
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
    except Exception as e:
        raise CustomException(e,sys) from e

def load_object(file_path:str):
    """
    file_path:str
    """
    try:
        with open(file_path, 'rb') as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise CustomException(e,sys) from e