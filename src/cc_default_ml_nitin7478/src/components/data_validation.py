from src.logger import logging
from src.exception import CustomException
from src.entity.config_entity import DataValidationConfig
from src.entity.artifact_entity import DataIngestionArtifact , DataValidationArtifact
import os, sys , json
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset, DataQualityPreset
from src.util import read_yaml_file
from src.constant import *
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings
warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)

import pandas as pd


class DataValidation:
    def __init__(self , data_validation_config:DataValidationConfig,
                 data_ingestion_artifact: DataIngestionArtifact):
        try:
            logging.info(f" {'='* 20} Data Validation log started. {'='*20} ")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise CustomException(e, sys) from e
    
    def get_train_test_dataframe(self):
        try:
            logging.info(f"converting train and test file into dataframe")
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            logging.info(f"conversion to dataframe successful")
            return train_df , test_df
        except Exception as e:
            raise CustomException(e,sys) from e
        
    def is_old_new_raw_dataset_datadrift_found(self , number_of_n_runs_old:int)->bool:
        try:
            is_data_drift_found = False
            ## Scenario wew are running program for every n days , user specify n number or folders back
            if number_of_n_runs_old is not None or number_of_n_runs_old >=1:
                new_raw_file_path = self.data_ingestion_artifact.raw_file_path
        
                number_of_n_runs_old = - (abs(number_of_n_runs_old)+1)
    
                new_raw_file_path = new_raw_file_path.replace('\\', '/')
                # remains = ("/").join(new_raw_file_path.split("/")[-2:])
                
                # paths = ("\\").join(new_raw_file_path.split("/")[:-3])
                
                path_components = new_raw_file_path.split("/")
                paths = os.path.normpath("/".join(path_components[:-3]))
                remains = os.path.normpath("/".join(path_components[-2:]))
                
                
                old_file_path = None
                
                if len(list(os.listdir(paths))) >= abs(number_of_n_runs_old):
                    old_date = str(os.listdir(paths)[number_of_n_runs_old])
                    old_file_path = os.path.join(paths,old_date, remains)
                
                    logging.info(f"Reading new excel file and convert to dataframe: [{new_raw_file_path}]")
                    new_df = pd.read_excel(new_raw_file_path , skiprows=1)
        
                    logging.info(f"Reading old raw excel file: [{old_file_path} of date :{old_date} \
                    which is {abs(number_of_n_runs_old)-1} folders back]")
                    if os.path.exists(old_file_path):
                        old_df = pd.read_excel(old_file_path , skiprows=1)
                        logging.info(f"Old raw excel file read and convert successfull")
                        drift_report = Report(metrics=[DataDriftPreset(), TargetDriftPreset()])
                        drift_report.run(reference_data=old_df, current_data=new_df)
                        report = json.loads(drift_report.json())
                        
                        is_data_drift_found = report['metrics'][0]['result']['dataset_drift']
                        if is_data_drift_found==False:
                            logging.info(f"Old and new dataset Data drift check successfull. No data drift found")
                        else:
                            raise Exception(f"Old and new dataset Data drift found")
                        return is_data_drift_found
                        # raise Exception("Old period raw file is missing,kindly disable old new dataset data drift check function")
                    else:
                        logging.info("Old period raw files for data drift not found, kindly check old files or update key data_drift_check_old_period in config.yaml file for temporary basis")
                        print("Old period raw files for data drift not found, kindly check old files or update key data_drift_check_old_period in config.yaml file for temporary basis")
                    return is_data_drift_found
            else:
                logging.info("Old period for Data drift check is None or Zero")
                print("Old period for Data drift check is None or Zero")
                return is_data_drift_found
        except Exception as e :
            raise CustomException(e, sys) from e
        
    
     
    def is_train_test_file_exists(self)->bool:
        try:
            logging.info("Checking if train and test file exists")
            is_train_file_exists = False
            is_test_file_exists = False
            
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path
            
            is_train_file_exists = os.path.exists(train_file_path)
            is_test_file_exists = os.path.exists(test_file_path)
            
            is_available = is_train_file_exists and is_test_file_exists
            logging.info(f"is train and test file exists? -> {is_available}")
            
            if not is_available:
                training_file = self.data_ingestion_artifact.train_file_path
                test_file = self.data_ingestion_artifact.test_file_path
                message = f"Traning file : {training_file} or testing file : {test_file} is not present"
                logging.error(message)
                return is_available
            else:
                return is_available
        except Exception as e:
            raise CustomException(e,sys) from e
    
    def validate_dataset_schema(self)->bool:
        try:
            logging.info(f"starting schema data validation")
            is_schema_validation_successful = False
            train_df, test_df = self.get_train_test_dataframe()
            if os.path.exists(self.data_validation_config.schema_file_path):
                schema_config = read_yaml_file(self.data_validation_config.schema_file_path)
            else:
                raise Exception("No schema file found")
            
            train_data_columns_list = list(map(lambda x: str(x).replace("dtype('" , "").replace("')", "").replace("\n", ""),train_df.dtypes.values))
            train_schema_dataframe = dict(zip(train_df.columns , train_data_columns_list))
            test_data_columns_list = list(map(lambda x: str(x).replace("dtype('" , "").replace("')", "").replace("\n", ""),test_df.dtypes.values))
            test_schema_dataframe = dict(zip(test_df.columns , test_data_columns_list))
            is_schema_validation_successful = schema_config[SCHEMA_VALIDATION_COLUMNS_KEY] == train_schema_dataframe \
                and schema_config[SCHEMA_VALIDATION_COLUMNS_KEY] == test_schema_dataframe
            if is_schema_validation_successful==True:
                logging.info(f"is schema validated successful : {is_schema_validation_successful}")
                return is_schema_validation_successful
            else:
                logging.error(f"Schema validation not successful")
                return is_schema_validation_successful
        except Exception as e:
            raise CustomException(e,sys) from e
        
    def is_data_drift_found(self)->bool:
        try:
            is_data_drift_found = False
            logging.info(f"Starting data drift check ")
            report = self.save_data_drift_report()
            self.save_data_drift_report_page()
            is_data_drift_found = report['metrics'][0]['result']['dataset_drift']
            if is_data_drift_found==False:
                logging.info(f"Data drift check successfull.No data drift found")
            else:
                is_data_drift_found = True
                logging.info(f"Data drift found in train and test dataset")
            return is_data_drift_found
        except Exception as e:
            raise CustomException(e,sys) from e
    
    def save_data_drift_report(self):
        try:
            logging.info("Checking data drift for train and test set and genrating json report")
            train_df,test_df =  self.get_train_test_dataframe()
            drift_report = Report(metrics=[DataDriftPreset(), TargetDriftPreset()])
            drift_report.run(reference_data=train_df, current_data=test_df)
            report = json.loads(drift_report.json())
            report_file_path = os.path.join(self.data_validation_config.report_file_path)
            report_dir = os.path.dirname(report_file_path)
            os.makedirs(report_dir , exist_ok= True)
            with open(report_file_path , 'w') as report_file:
                json.dump(report, report_file , indent=6)
            logging.info("Successful : Checking data drift train and test set and genrating json reports")
            return report
        except Exception as e:
            raise CustomException(e,sys) from e
    
    def save_data_drift_report_old_data_check(self):
        try:
            logging.info("Checking data drift for old dataset and new dataset and genrating json report")
            train_df,test_df =  self.get_train_test_dataframe()
            drift_report = Report(metrics=[DataDriftPreset(), TargetDriftPreset()])
            drift_report.run(reference_data=train_df, current_data=test_df)
            report = json.loads(drift_report.json())
            report_file_path = os.path.join(self.data_validation_config.report_file_path)
            report_dir = os.path.dirname(report_file_path)
            os.makedirs(report_dir , exist_ok= True)
            with open(report_file_path , 'w') as report_file:
                json.dump(report, report_file , indent=6)
            logging.info("Successful : Checking data drift train and test set and genrating json reports")
            return report
        except Exception as e:
            raise CustomException(e,sys) from e  
        
    def save_data_drift_report_page(self):
        try:
            logging.info("Checking data drift and genrating html report")
            train_df,test_df =  self.get_train_test_dataframe()
            drift_report = Report(metrics=[DataDriftPreset(), TargetDriftPreset()])
            drift_report.run(reference_data=train_df, current_data=test_df)
            drift_report.save_html(self.data_validation_config.report_page_file_path)
            logging.info("Successful : Checking data drift and genrating html reports")
        except Exception as e:
            raise CustomException(e,sys) from e
        
    def initiate_data_validation(self)-> DataValidationArtifact:
        try:
            
            is_train_test_file_exists = self.is_train_test_file_exists()
            is_data_drift_found = self.is_data_drift_found() 
            is_old_new_raw_dataset_datadrift_found = self.is_old_new_raw_dataset_datadrift_found(self.data_validation_config.data_drift_check_old_period)
            is_validated = self.validate_dataset_schema()
            if is_train_test_file_exists==True and is_data_drift_found==False:
                if is_old_new_raw_dataset_datadrift_found== False and is_validated==True:
                    is_validated = True
                    logging.info(f"All data validations successful")
            else:
                is_validated = False
                logging.info(f"error in data validation")
                raise Exception("error in data validation")
            data_validation_artifact = DataValidationArtifact(
                schema_file_path=self.data_validation_config.schema_file_path,
                report_file_path=self.data_validation_config.report_file_path,
                report_page_file_path=self.data_validation_config.report_page_file_path,
                is_validated=is_validated,
                message="Data Validation performed successfully"
                )
            logging.info(f"Data Validation artifact : {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise CustomException(e,sys) from e
    
    def __del__(self):
        logging.info(f"{'>>'*20} Data Validation log completed.{'<<'*20} \n\n")