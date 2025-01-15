import sys
import pandas as pd
from airflow.decorators import dag, task
from airflow import DAG
#from airflow.operators.python import PythonOperator

#PATH_COMMON = '../'
#sys.path.append(PATH_COMMON)
#from common.classes import *
#from common.training_task import save_pipeline_model


data = pd.read_csv('/opt/airflow/dags/data/input/train_coche.csv')
features = pd.read_csv('/opt/airflow/dags/data/input/selected_features.csv')


@task
def push_xcom(ti):
    value_to_push = 'Este es un valor enviado a XCom'
    ti.xcom_push(key='sample_xcom_key', value=value_to_push)
    print(f'Valor enviado a XCom: {value_to_push}')

@task
def pull_xcom(ti):
    pulled_value = ti.xcom_pull(key='pipeline', task_ids='task_train_model_docker')
    print(f'Valor recuperado de XCom: {pulled_value}')


@task.docker(image="train_model_docker:latest", 
             mount_tmp_dir=False,
             multiple_outputs=True)
def task_train_model_docker(data, features):
    # data manipulation and plotting
    import pandas as pd
    import numpy as np

    # pipeline save
    import joblib

    # from Scikit-learn
    #from sklearn.linear_model import Lasso, LinearRegression
    #from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split
    #from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.preprocessing import LabelEncoder
    from lightgbm import LGBMRegressor

    #from feature_engine.encoding import OrdinalEncoder
    #from feature_engine.transformation import YeoJohnsonTransformer
    from datetime import datetime
    import scipy.stats as stats

    #from sklearn.base import BaseEstimator, TransformerMixin

    #class TemporalVariableTransformer(BaseEstimator, TransformerMixin):
    #    # Temporal elapsed time transformer
    #    def __init__(self, variables, reference_variable):           
    #        if not isinstance(variables, list):
    #            raise ValueError('variables should be a list')
            
    #        self.variables = variables
    #        self.reference_variable = reference_variable

    #    def fit(self, X, y=None):
    #        # we need this step to fit the sklearn pipeline
    #        return self

    #    def transform(self, X):
            # so that we do not over-write the original dataframe
    #        X = X.copy()          
    #        for feature in self.variables:
    #            X[feature] = self.reference_variable - X[feature]
    #        return X
        
    # load dataset
    
    features = features['0'].to_list()

    # Quitamos etiquetas km y miles de variable running y convertimos a numérico
    data["running"] = data["running"].astype(str)
    data["running"] = data["running"].str.replace(" km","")
    data["running"] = data["running"].str.replace(" miles","")
    data["running"] = data["running"].astype(float)
    data["running"]

    # Variables temporales
    TEMPORAL_VARS = ['year']
    REF_VAR = datetime.now().year
    data[TEMPORAL_VARS] = REF_VAR - data[TEMPORAL_VARS]

    # Separamos dataset en train y test
    X_train, X_test, y_train, y_test = train_test_split(
        data.drop(['price'], axis=1), # predictive variables
        data['price'], # target
        test_size=0.1, # portion of dataset to allocate to test set
        random_state=0, # we are setting the seed here
    )
    
    # Transformación de variable target
    y_train = np.log(y_train)
    y_test = np.log(y_test)

    # Variables seleccionadas del proceso feature selection
    FEATURES = features

    X_train = X_train[FEATURES]
    X_test = X_test[FEATURES]

    # Variables para tranformaciion yeo 
    NUMERICALS_YEO_VARS = ['running', 'motor_volume', 'year']
    for var in NUMERICALS_YEO_VARS:
        X_train[var], param = stats.yeojohnson(X_train[var])
        #X_test[NUMERICALS_YEO_VARS], param = stats.yeojohnson(X_test[NUMERICALS_YEO_VARS])

    # Variables categoricas para codificar
    CATEGORICAL_VARS = ['model', 'motor_type', 'color', 'type', 'status']
    le=LabelEncoder()
    for var in CATEGORICAL_VARS:
         X_train[var]=le.fit_transform(X_train[var])

    # ESCALAMIENTO
    scaler = MinMaxScaler()
    scaler.fit(X_train)

    X_train = pd.DataFrame(
        scaler.transform(X_train),
        columns=X_train.columns
        )
    
    lin_model = LGBMRegressor()
    lin_model.fit(X_train, y_train)
   
    #print(X_train.head())
    #for var in CATEGORICAL_VARS:
        

#for var in X_train.columns[X_train.dtypes=='object']:
 #   X_train[var]=le.fit_transform(X_train[var])
    
    

    #X_train[CATEGORICAL_VARS] = X_train[CATEGORICAL_VARS].astype('category')


    
    
   # pipeline = Pipeline([
    
    # VARIABLE TRANSFORMATION
     #('yeojohnson', YeoJohnsonTransformer(variables=NUMERICALS_YEO_VARS)),   
     # CATEGORICAL ENCODING
    #('categorical_encoder', OrdinalEncoder(
    #    encoding_method='ordered', variables=CATEGORICAL_VARS)),    
    # ESCALAMIENTO
   # ('scaler', MinMaxScaler()),
    # MODELO
   # ('model', LGBMRegressor())
    #])

    #pipeline.fit(X_train, y_train)
    # guardamos pipeline
    #joblib.dump(pipeline, 'precio_coches_pipeline.joblib')
    print("pipeline exportado")
    return {"pipeline": lin_model}

@dag(
    dag_id="training_dag",
    schedule=None
)
def trainingdag():
    task_train_model_docker(data, features)
    #pull_xcom()

training_dag = trainingdag()
