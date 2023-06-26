from src.pipeline.pipeline import Pipeline
from src.exception import CustomException
from src.logger import logging
from src.config.configuration import Configuration
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
from src.components.data_validation import DataValidation

def main(): 
    try:
        pipeline = Pipeline()
        pipeline.run_pipeline()
        # a = Configuration().get_data_transformation_config()
        # print(a)
    except Exception as e:
        logging.error(f"{e}")
        print(e)
    
if __name__=="__main__":
    main()