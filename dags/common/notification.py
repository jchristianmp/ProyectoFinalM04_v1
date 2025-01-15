from airflow.utils.email import send_email
from datetime import datetime, timedelta


def success_email(context):
    task_instance = context['task_instance']
    task_status = "Success"
    subject = f'Airflow Task {task_instance.task_id} {task_status}'
    body = f'The task {task_instance.task_id} complete whit status: {task_status}. \n\n'\
    f'The task execution date is: {context["execution_date"]}\n'\
    f'log url: {task_instance.log_url}\n\n'
    to_email = "jchristian.mp@gmail.com"
    send_email(to = to_email, subject=subject, html_content=body)

def failure_email(context):
    error_var = context["var"]["value"].get("error_val")

    task_instance = context['task_instance']
    task_status = "Failed"
    subject = f'Airflow Task {task_instance.task_id} {task_status}'
    to_email = "jchristian.mp@gmail.com"

    if error_var == "_":
        body = f'The task {task_instance.task_id} complete whit status: {task_status}. \n\n'\
        f'The task execution date is: {context["execution_date"]}\n'\
        f'log url: {task_instance.log_url}\n\n'
    else:
        body = f'The task {task_instance.task_id} complete whit status: {task_status}. \n\n'\
        f'The task execution date is: {context["execution_date"]}\n'\
        f'Error: {error_var} \n\n'\
        f'log url: {task_instance.log_url}\n\n'

    send_email(to = to_email, subject=subject, html_content=body)


