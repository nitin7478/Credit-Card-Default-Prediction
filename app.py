from flask import Flask, render_template, request
from src.entity.predictor import Predictor
import os
import pandas as pd
from datetime import datetime
import csv


SAVED_MODELS_DIR_NAME = "saved_models"
ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, SAVED_MODELS_DIR_NAME)

METRIC_INFO_FILE_PATH = os.path.join(ROOT_DIR, 'Current_Model_Metric_Info', 'metric_info.csv' )
if os.path.exists(METRIC_INFO_FILE_PATH):
    line = list()
    with open(METRIC_INFO_FILE_PATH, mode ='r') as file:
        csv_file = csv.reader(file)
        for lines in csv_file:
            line.append(lines)
else:
    print("No Model Trained , kindly run pipeline")
current_accuracy = round(float(line[0][-2]),2)

app = Flask(__name__)


@app.route('/')
def home():
    latest_model_folder_name = Predictor.get_latest_model_path(model_dir=MODEL_DIR)
    date_string = os.path.dirname(latest_model_folder_name).split("\\")[-1]
    last_trained_model_date = datetime.strptime(date_string, "%Y%m%d%H%M%S")
    return render_template('index.html' ,last_trained_model_date=last_trained_model_date , current_accuracy=current_accuracy)



@app.route('/predict', methods=['POST'])
def predict():
    features = ['ID','LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE', 'PAY_0',
                'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6', 'BILL_AMT1',
                'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
                'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']

    input_data = pd.DataFrame(columns=features)
    input_row = {}
    for feature in features:
        input_row[feature] = [int(request.form.get(feature))]
    input_data = pd.DataFrame.from_dict(input_row)
    
    # Perform prediction using the loaded model
    predictor = Predictor(model_dir=MODEL_DIR)
    prediction = predictor.predict(input_data)
    
    
    if prediction == 0:
        result = 'Not Default'
    else:
        result = 'Default'

    return render_template('index.html', prediction_result=result )

if __name__ == '__main__':
    app.run(debug=True)



