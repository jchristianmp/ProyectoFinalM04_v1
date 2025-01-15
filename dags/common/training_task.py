from airflow.decorators import task

@task.virtualenv(
        task_id="training_model", 
        requirements=["pandas==2.2.3",
                      "joblib==1.3.2",
                      "feature-engine==1.8.2",
                      "scikit-learn==1.5.2",
                      "numpy==1.26.4",
                      "python-multipart==0.0.17",
                      ], 
        system_site_packages=False
)
def training_model():
    
    import pandas as pd
    import numpy as np
    import joblib
    from datetime import datetime
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import MinMaxScaler
    from feature_engine.transformation import YeoJohnsonTransformer
    from feature_engine.encoding import OrdinalEncoder
    from sklearn.linear_model import Lasso

    data = pd.read_csv('/opt/airflow/dags/data/input/train_coche.csv')
    features = pd.read_csv('/opt/airflow/dags/data/input/selected_features.csv')  
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

    # Variables para tranformaciion yeo 
    NUMERICALS_YEO_VARS = ['running', 'motor_volume', 'year']

    # Variables categoricas para codificar
    CATEGORICAL_VARS = ['model', 'motor_type', 'color', 'type', 'status']

    # Variables seleccionadas del proceso feature selection
    FEATURES = features

    X_train = X_train[FEATURES]
    X_test = X_test[FEATURES]


    X_train[CATEGORICAL_VARS] = X_train[CATEGORICAL_VARS].astype('category')

    pipeline = Pipeline([
    # VARIABLE TRANSFORMATION
     ('yeojohnson', YeoJohnsonTransformer(variables=NUMERICALS_YEO_VARS)),
     #('log', LogTransformer(variables=NUMERICALS_YEO_VARS)),
        
     # CATEGORICAL ENCODING
    ('categorical_encoder', OrdinalEncoder(
        encoding_method='ordered', variables=CATEGORICAL_VARS)),
        
    # ESCALAMIENTO
    ('scaler', MinMaxScaler()),

    # MODELO
    ('Lasso', Lasso(alpha=0.001, random_state=0)),
    ])

    pipeline.fit(X_train, y_train)

    # Guardamos pipeline
    joblib.dump(pipeline, '/opt/airflow/dags/data/model/precio_coches_pipeline.joblib')
    print("pipeline guardado")

