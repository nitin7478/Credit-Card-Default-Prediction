from src.exception import CustomException
from src.logger import logging
import sys , yaml,os
from collections import namedtuple
import numpy as np
from sklearn.metrics import f1_score , accuracy_score
from typing import List
import importlib ,csv


GRID_SEARCH_KEY = 'grid_search'
MODULE_KEY = 'module'
CLASS_KEY = 'class'
PARAM_KEY = 'params'
MODEL_SELECTION_KEY = 'model_selection'
SEARCH_PARAM_GRID_KEY = "search_param_grid"

InitializedModelDetail = namedtuple("InitializedModelDetail",
                                    ["model_serial_number", "model", "param_grid_search", "model_name"])

GridSearchedBestModel = namedtuple("GridSearchedBestModel", ["model_serial_number",
                                                             "model",
                                                             "best_model",
                                                             "best_parameters",
                                                             "best_score",
                                                             ])
BestModel = namedtuple("BestModel", ["model_serial_number",
                                     "model",
                                     "best_model",
                                     "best_parameters",
                                     "best_score", ])

MetricInfoArtifact = namedtuple("MetricInfoArtifact",
                                ["model_name", "model_object", "train_f1_score", "test_f1_score", "train_accuracy",
                                 "test_accuracy", "model_accuracy", "index_number"])




def evaluate_classification_model(model_list: list, X_train, y_train:np.ndarray, X_test, y_test:np.ndarray, base_accuracy:float) -> MetricInfoArtifact:
    """
    Description:
    This function compare multiple classification model return best model

    Params:
    model_list: List of model
    X_train: Training dataset input feature
    y_train: Training dataset target feature
    X_test: Testing dataset input feature
    y_test: Testing dataset input feature

    return
    It return a named tuple
    
    MetricInfoArtifact = namedtuple("MetricInfo",
                                ["model_name", "model_object", "train_f1_score", "test_f1_score", "train_accuracy",
                                 "test_accuracy", "model_accuracy", "index_number"])
    """
    try:
        METRIC_INFO_FILE_PATH = os.path.join(os.getcwd(), 'Current_Model_Metric_Info')
        os.makedirs(METRIC_INFO_FILE_PATH , exist_ok=True)
        index_number = 0
        metric_info_artifact = None

        for model in model_list:
            model_name = str(model)  #getting model name based on model object
            logging.info(f"{'>>'*30}Started evaluating model: [{type(model).__name__}] {'<<'*30}")
            
            # Getting prediction for training and testing dataset
        
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            #Calculating r squared score on training and testing dataset
            train_acc = accuracy_score(y_train, y_train_pred)
            test_acc = accuracy_score(y_test, y_test_pred)
            
            #Calculating mean squared error on training and testing dataset
            train_f1_score = f1_score(y_train, y_train_pred , average='macro')
            test_f1_score = f1_score(y_test, y_test_pred, average='macro')

            # Calculating harmonic mean of train_accuracy and test_accuracy
            model_accuracy = (2 * (train_acc * test_acc)) / (train_acc + test_acc)
            diff_test_train_acc = abs(test_acc - train_acc)
            
            #logging all important metric
            logging.info(f"{'>>'*30} Score {'<<'*30}")
            logging.info(f"Train Score\t\t Test Score\t\t Average Score")
            logging.info(f"{train_acc}\t\t {test_acc}\t\t{model_accuracy}")

            logging.info(f"{'>>'*30} Loss {'<<'*30}")
            logging.info(f"Diff test train accuracy: [{diff_test_train_acc}].") 
            logging.info(f"Train f1_score : [{train_f1_score}].")
            logging.info(f"Test f1_score : [{test_f1_score}].")


            #if model accuracy is greater than base accuracy and train and test score is within certain thershold
            #we will accept that model as accepted model
            if model_accuracy >= base_accuracy and diff_test_train_acc < 0.05:
                #if base accuracy will update to model accuracy , any model comes below this accuracy , we wont accept
                base_accuracy = model_accuracy
                metric_info_artifact = MetricInfoArtifact(model_name=model_name,
                                                        model_object=model,
                                                        train_f1_score=train_f1_score,
                                                        test_f1_score=test_f1_score,
                                                        train_accuracy=train_acc,
                                                        test_accuracy=test_acc,
                                                        model_accuracy=model_accuracy,
                                                        index_number=index_number)
                with open(f"{METRIC_INFO_FILE_PATH}/Current_Model_Metric_Info.csv" , 'w') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(metric_info_artifact)

                logging.info(f"Acceptable model found {metric_info_artifact}. ")
            #if index_number 1 is returned and we can consider that, new model updated previous one
            index_number += 1
        if metric_info_artifact is None:
            logging.info(f"No model found with higher accuracy than base accuracy")
        return metric_info_artifact
    except Exception as e:
        raise CustomException(e, sys) from e


class ModelFactory:
    def __init__(self, model_config_path: str = None,):
        try:
            # Read model.yaml file inside config folder
            self.config: dict = ModelFactory.read_params(model_config_path)
            #module to import for GridSearchCV
            self.grid_search_cv_module: str = self.config[GRID_SEARCH_KEY][MODULE_KEY]
            #class name GridSearchCV
            self.grid_search_class_name: str = self.config[GRID_SEARCH_KEY][CLASS_KEY]
            #Read params for GridSearchCV
            self.grid_search_property_data: dict = dict(self.config[GRID_SEARCH_KEY][PARAM_KEY])
            #Read different type of models in model_selection key and save in list
            self.models_initialization_config: dict = dict(self.config[MODEL_SELECTION_KEY])

            self.initialized_model_list = None
            self.grid_searched_best_model_list = None

        except Exception as e:
            raise CustomException(e, sys) from e

    @staticmethod
    def update_property_of_class(instance_ref:object, property_data: dict):
        try:
            #instance_ref is default attributes list , property_data is list from model.yaml
            if not isinstance(property_data, dict):
                raise Exception("property_data parameter required to dictionary")
            print(property_data)
            for key, value in property_data.items():
                logging.info(f"Executing:$ {str(instance_ref)}.{key}={value}")
                setattr(instance_ref, key, value)
            return instance_ref
        except Exception as e:
            raise CustomException(e, sys) from e

    @staticmethod
    def read_params(config_path: str) -> dict:
        try:
            with open(config_path) as yaml_file:
                config:dict = yaml.safe_load(yaml_file)
            return config
        except Exception as e:
            raise CustomException(e, sys) from e

    @staticmethod
    def class_for_name(module_name:str, class_name:str):
        try:
            # load the module, will raise ImportError if module cannot be loaded
            #import the module and class
            module = importlib.import_module(module_name)
            # get the class, will raise AttributeError if class cannot be found
            logging.info(f"Executing command: from {module} import {class_name}")
            #get all the default attributes
            class_ref = getattr(module, class_name)
            return class_ref
        except Exception as e:
            raise CustomException(e, sys) from e

    def execute_grid_search_operation(self, initialized_model: InitializedModelDetail, input_feature,
                                      output_feature) -> GridSearchedBestModel:
        """
        excute_grid_search_operation(): function will perform paramter search operation and
        it will return you the best optimistic  model with best paramter:
        estimator: Model object
        param_grid: dictionary of paramter to perform search operation
        input_feature: your all input features
        output_feature: Target/Dependent features
        ================================================================================
        return: Function will return GridSearchOperation object
        """
        try:
            # instantiating GridSearchCV class
            
           #import gridserach cv module
            grid_search_cv_ref = ModelFactory.class_for_name(module_name=self.grid_search_cv_module,
                                                             class_name=self.grid_search_class_name
                                                             )
            #update gridsearchcv parameters such cv , estimator , and params_grid
            grid_search_cv = grid_search_cv_ref(estimator=initialized_model.model,
                                                param_grid=initialized_model.param_grid_search)
            #updated properties for gridsearch
            grid_search_cv = ModelFactory.update_property_of_class(grid_search_cv,
                                                                   self.grid_search_property_data)

            
            message = f'{">>"* 30} f"Training {type(initialized_model.model).__name__} Started." {"<<"*30}'
            logging.info(message)
            #Perfoerm gridsearch cv operation for particular estimator
            grid_search_cv.fit(input_feature, output_feature)
            message = f'{">>"* 30} f"Training {type(initialized_model.model).__name__}" completed {"<<"*30}'
            grid_searched_best_model = GridSearchedBestModel(model_serial_number=initialized_model.model_serial_number,
                                                             model=initialized_model.model,
                                                             best_model=grid_search_cv.best_estimator_,
                                                             best_parameters=grid_search_cv.best_params_,
                                                             best_score=grid_search_cv.best_score_
                                                             )
            
            #Return lists of all the models with scores and best_params_ , this is only performed on train dataset
            return grid_searched_best_model
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_initialized_model_list(self) -> List[InitializedModelDetail]:
        """
        This function will return a list of model details.
        return List[ModelDetail]
        """
        try:
            initialized_model_list = []
            for model_serial_number in self.models_initialization_config.keys():

                model_initialization_config = self.models_initialization_config[model_serial_number]
                #import modele and class 
                model_obj_ref = ModelFactory.class_for_name(module_name=model_initialization_config[MODULE_KEY],
                                                            class_name=model_initialization_config[CLASS_KEY]
                                                            )
                model = model_obj_ref()
                #update parameter values from params key
                if PARAM_KEY in model_initialization_config:
                    model_obj_property_data = dict(model_initialization_config[PARAM_KEY])
                    model = ModelFactory.update_property_of_class(instance_ref=model,
                                                                  property_data=model_obj_property_data)
                #Read gridsearchparameters for module__
                param_grid_search = model_initialization_config[SEARCH_PARAM_GRID_KEY]
                #store model_name as e.g sklearn.linear_model.LogisticRegression
                model_name = f"{model_initialization_config[MODULE_KEY]}.{model_initialization_config[CLASS_KEY]}"

                model_initialization_config = InitializedModelDetail(model_serial_number=model_serial_number,
                                                                     model=model,
                                                                     param_grid_search=param_grid_search,
                                                                     model_name=model_name
                                                                     )

                initialized_model_list.append(model_initialization_config)

            self.initialized_model_list = initialized_model_list
            
            return self.initialized_model_list
        except Exception as e:
            raise CustomException(e, sys) from e

    def initiate_best_parameter_search_for_initialized_model(self, initialized_model: InitializedModelDetail,
                                                             input_feature,
                                                             output_feature) -> GridSearchedBestModel:
        """
        initiate_best_model_parameter_search(): function will perform paramter search operation and
        it will return you the best optimistic  model with best paramter:
        estimator: Model object
        param_grid: dictionary of paramter to perform search operation
        input_feature: your all input features
        output_feature: Target/Dependent features
        ================================================================================
        return: Function will return a GridSearchOperation
        """
        try:
            return self.execute_grid_search_operation(initialized_model=initialized_model,
                                                      input_feature=input_feature,
                                                      output_feature=output_feature)
        except Exception as e:
            raise CustomException(e, sys) from e

    def initiate_best_parameter_search_for_initialized_models(self,
                                                              initialized_model_list: List[InitializedModelDetail],
                                                              input_feature,
                                                              output_feature) -> List[GridSearchedBestModel]:

        try:
            #Start grid search operations using initialized_model_list one by one using above function
            self.grid_searched_best_model_list = []
            for initialized_model_list in initialized_model_list:
                grid_searched_best_model = self.initiate_best_parameter_search_for_initialized_model(
                    initialized_model=initialized_model_list,
                    input_feature=input_feature,
                    output_feature=output_feature
                )
                self.grid_searched_best_model_list.append(grid_searched_best_model)
            return self.grid_searched_best_model_list
        except Exception as e:
            raise CustomException(e, sys) from e

    @staticmethod
    def get_model_detail(model_details: List[InitializedModelDetail],
                         model_serial_number: str) -> InitializedModelDetail:
        """
        This function return ModelDetail
        """
        try:
            for model_data in model_details:
                if model_data.model_serial_number == model_serial_number:
                    return model_data
        except Exception as e:
            raise CustomException(e, sys) from e

    @staticmethod
    def get_best_model_from_grid_searched_best_model_list(grid_searched_best_model_list: List[GridSearchedBestModel],
                                                          base_accuracy=0.6
                                                          ) -> BestModel:
        try:
            best_model = None
            for grid_searched_best_model in grid_searched_best_model_list:
                if base_accuracy < grid_searched_best_model.best_score:
                    logging.info(f"Acceptable model found:{grid_searched_best_model}")
                    base_accuracy = grid_searched_best_model.best_score

                    best_model = grid_searched_best_model
            if not best_model:
                raise Exception(f"None of Model has base accuracy: {base_accuracy}")
            logging.info(f"Best model: {best_model}")
            return best_model
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_best_model(self, X, y,base_accuracy=0.6) -> BestModel:
        try:
            logging.info("Started Initializing model from config file")
            #get list of all the models from dict and store in list
            initialized_model_list = self.get_initialized_model_list()
            logging.info(f"Initialized model: {initialized_model_list}")
            grid_searched_best_model_list = self.initiate_best_parameter_search_for_initialized_models(
                initialized_model_list=initialized_model_list,
                input_feature=X,
                output_feature=y
            )
            return ModelFactory.get_best_model_from_grid_searched_best_model_list(grid_searched_best_model_list,
                                                                                  base_accuracy=base_accuracy)
        except Exception as e:
            raise CustomException(e, sys)