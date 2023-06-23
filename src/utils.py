
from src.exception import CustomException
from src.logger import logging
import sys,os


# if __name__=="__main__":
#     try :
#         a = 1/0
#         logging.info("zero division succesfull")
#     except Exception as e:
#         logging.error("zero division error")
#         raise CustomException(e , sys) from e