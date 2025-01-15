import sys
import pandas as pd
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow import DAG
#from airflow.operators.python import PythonOperator

PATH_COMMON = '../'
sys.path.append(PATH_COMMON)
#from common.classes import *
from common.training_task import training_model
from common.notification import success_email, failure_email


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
    dag_id="training_dag_v2",
    default_args=default_args,
    description='training model with email notification',
    on_failure_callback = lambda context: failure_email(context),
    on_success_callback = lambda context: success_email(context),
    schedule=None,
)
def trainingdag():
    training_model()
    #pull_xcom()

training_dag = trainingdag()
