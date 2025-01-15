# Función para enviar datos a XCom
import sys
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.exceptions import AirflowFailException

PATH_COMMON = '../'
sys.path.append(PATH_COMMON)
#from common.global_task import set_var, evaluate_status
from common.notification import success_email, failure_email
from common.prediction_task import (task_predict_model,
                                    data_preparation,
                                    task_extract_execution_date)

@task
def set_var():
    Variable.set(key="error_val", value="_")

@task
def evaluate_predict_status(mensaje: str):
    if mensaje == "Prediccion": 
        print("OK")
    else:
        Variable.set(key="error_val", value="ERROR, datos de entrada para predicción no coinciden con fecha de ejecución")
        #print(mensaje)
        raise AirflowFailException("error")

default_args={
    'owner': 'cm',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 17),
    'schedule_interval' : 'None',
    'email_on_failure': True,
    'email_on_success': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

@dag(
    dag_id="prediction_dag_v1",
    default_args=default_args,
    description='data preparation and model prediction with email notification',
    on_failure_callback = lambda context: failure_email(context),
    on_success_callback = lambda context: success_email(context),
    schedule=None
)
def predictiondag(): 
    set_var()
    #resp = task_predict_model(data_preparation(), 
    #                          local_execution_date)
    evaluate_predict_status(
        task_predict_model(
            data_preparation(),
            task_extract_execution_date())
            )
    #task_to_fail()
    


prediction_dag = predictiondag()
