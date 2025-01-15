from airflow.decorators import task
from airflow.operators.python import get_current_context

import pandas as pd
import numpy as np
from datetime import datetime
import pytz as tz

@task(task_id="data_preparation")
def data_preparation():
    data = pd.read_csv('/opt/airflow/dags/data/input/test_coche.csv')
    #features = pd.read_csv('/opt/airflow/dags/data/input/selected_features.csv')  
    #features = features['0'].to_list()

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

    limaTz = tz.timezone("America/Lima")
    data["date"] = datetime.now(limaTz).date()

    #data = data[features]
    
    return data

@task.virtualenv(
        task_id="predict_model", 
        requirements=[
            "pandas==2.2.3",
            "joblib==1.3.2",
            "feature-engine==1.8.2",
            "scikit-learn==1.5.2",
            "numpy==1.26.4",
            "pendulum",
            ], 
        system_site_packages=True,
)
def task_predict_model(data, local_execution_date):
    import pandas as pd
    import numpy as np
    import joblib
    from datetime import datetime
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import MinMaxScaler
    from feature_engine.transformation import YeoJohnsonTransformer
    from feature_engine.encoding import OrdinalEncoder
    from sklearn.linear_model import Lasso
    import pendulum

    pipeline_de_produccion = joblib.load('/opt/airflow/dags/data/model/precio_coches_pipeline.joblib')
    features = pd.read_csv('/opt/airflow/dags/data/input/selected_features.csv')  
    features = features['0'].to_list()

    local_execution_date_str = local_execution_date.strftime('%Y-%m-%d')
    local_execution_date_date = datetime.strptime(local_execution_date_str, '%Y-%m-%d').date()

    print(local_execution_date_date)
    data_temp = data[data["date"] == local_execution_date_date]

    if data.shape[0] == data_temp.shape[0]:
        print("Datos coinciden con la fecha de ejecución")

        data = data[features]
        predicciones = pipeline_de_produccion.predict(data)
        predicciones_sin_escalar = np.exp(predicciones)
        print("Predicción Generada")

        # Resultados
        df_resultados = data.copy()
        #processing_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df_resultados['Prediccion_Escalada'] = predicciones
        df_resultados['Prediccion_sin_Escalar'] = predicciones_sin_escalar
        df_resultados['Fecha_procesamiento'] = local_execution_date
        
        # CSV export
        df_resultados.to_csv("/opt/airflow/dags/data/output/prediction.csv", index=False)
        print("Prediccion generada")

        msg = "Prediccion"
    else:
        msg = "Sin predicción"
    
    return msg
    

@task(task_id="extract_execution_date")
def task_extract_execution_date():
    import pendulum 
    from datetime import datetime

    #Validación de fecha
    context = get_current_context()
    execution_date_utc = context['execution_date'] 
    local_timezone = pendulum.timezone("America/Lima") 
    local_execution_date = execution_date_utc.in_timezone(local_timezone) 

    return local_execution_date

