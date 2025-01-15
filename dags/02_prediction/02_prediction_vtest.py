# Función para enviar datos a XCom
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import get_current_context
from airflow.decorators import dag, task


PATH_COMMON = '../'
sys.path.append(PATH_COMMON)
from common.prediction_task import data_preparation

#@task(task_id="push_xcom_task")
#def push_xcom():
#    value_to_push = 'Este es un valor enviado a XCom'
#    return value_to_push

# Función para recuperar datos de XCom
#@task(task_id="pull_xcom_task")
#def pull_xcom(mensaje):
    #pulled_value = ti.xcom_pull(key='sample_xcom_key', task_ids='push_xcom_task')
#    print(f'Valor recuperado de XCom: {mensaje}')

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
    dag_id="execution_date_test",
    default_args=default_args,
    description='test',
    #on_failure_callback = lambda context: failure_email(context),
    #on_success_callback = lambda context: success_email(context),
    schedule=None
)
def predictiondag():
    data_preparation()
    #pull_xcom()

prediction_dag = predictiondag()
