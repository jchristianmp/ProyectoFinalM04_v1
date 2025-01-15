from airflow.decorators import task
from airflow.exceptions import AirflowFailException
from airflow.models import Variable



@task
def evaluate_status(mensaje: str):
    if mensaje == "Prediccion": 
        print("OK")
    else:
        Variable.set(key="error_val", value="ERROR, datos no coinciden con fecha de ejecución")
        #print(mensaje)
        raise AirflowFailException("error")#task_to_fail()
@task
def set_var():
    #from airflow.models import Variable
    Variable.set(key="error_val", value="_")