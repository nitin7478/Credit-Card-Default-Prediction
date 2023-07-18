train_f_path  = r"D:\github\Credit Card Default Machine Learning\Credit-Card-Default-Prediction\src\cc_default_ml_nitin7478\src\artifact\data_ingestion\2023-07-18-13-55-03\ingested_data\train\default of credit card clients.csv"

import pandas as pd

def transform(X , column = 'ID'):
    print(X.columns[0] , column)
    if X.columns[0]==column:
        X.drop(columns = column , inplace = True)
    return X

df = pd.read_csv(train_f_path)


X = transform(df)

print(X.head())
    