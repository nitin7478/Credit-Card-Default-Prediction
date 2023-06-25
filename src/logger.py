import logging 
import os
from datetime import datetime
from src.constant import get_current_time_stamp


LOG_FILE = f"log_{get_current_time_stamp()}.log"
LOG_DIR = "logs"

logs_path = os.path.join(os.getcwd(),LOG_DIR)
os.makedirs(logs_path , exist_ok = True)
LOG_FILE_PATH = os.path.join(logs_path , LOG_FILE)
logging.basicConfig(
    filename = LOG_FILE_PATH,
    filemode="w",
    format = '[%(asctime)s] - %(levelname)s - %(lineno)d - %(filename)s - %(funcName)s() - %(message)s',
    level = logging.INFO,
)


# if __name__=="__main__":
#     logging.info("Logging has started")
    
