import os 
from datetime import datetime
ROOT_DIR = os.getcwd()

def get_current_time_stamp():
    return f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"

CONFIG_DIR = 'config'
CONFIG_FILE_PATH = 'config.yaml'
CONFIG_FILE_PATH = os.path.join(ROOT_DIR, CONFIG_DIR, CONFIG_FILE_PATH)

CURRENT_TIME_STAMP = get_current_time_stamp()

# keys are from config.yaml file , we well access values by these keys by using constant variable
# training pipeline related variables
#these key and values are same as config.yaml file 
TRAINING_PIPELINE_CONFIG_KEY = "training_pipeline_config"
TRAINING_PIPELINE_ARTIFACT_DIR_KEY = "artifact_dir"
TRAINING_PIPELINE_NAME_KEY = "pipeline_name"

# DataIngestion related vairbales 
DATA_INGESTION_CONFIG_KEY = "data_ingestion_config"
DATA_INGESTION_ARTIFACT_DIR = "data_ingestion"
DATA_INGESTION_DOWNLOAD_URL_KEY = "dataset_download_url"
DATA_INGESTION_RAW_DATA_DIR_KEY = "raw_data_dir"
DATA_INGESTION_TGZ_DOWNLOAD_DIR_KEY = "tgz_download_dir"
DATA_INGESTION_INGESTED_DIR_NAME_KEY = "ingested_dir"
DATA_INGESTION_TRAIN_DIR_KEY = "ingested_train_dir"
DATA_INGESTION_TEST_DIR_KEY = "ingested_test_dir"

#Data validation related variable
DATA_VALIDATION_CONFIG_KEY = 'data_validation_config'
DATA_VALIDATION_SCHEMA_FILE_NAME_KEY = "schema_file_name"
DATA_VALIDATION_SCHEMA_DIR_KEY = "schema_dir"
DATA_VALIDATION_ARTIFACT_DIR_NAME = "data_validation"
DATA_VALIDATION_REPORT_FILE_NAME = "report_file_name"
DATA_VALIDATION_REPORT_PAGE_NAME_KEY = "report_page_file_name"
DATA_VALIDATION_DATA_DRIFT_CHECK_OLD_PERIOD =  "data_drift_check_old_period"

#Schema validation related variables
SCHEMA_VALIDATION_COLUMNS_KEY = 'columns'
SCHEMA_VALIDATION_TARGET_COLUMN_KEY = 'target_column'
