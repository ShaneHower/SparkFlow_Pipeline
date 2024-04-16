# Import necessary modules
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging

# Define the Python functions to be used as tasks
def print_hello():
    logging.info("Hello")

def print_world():
    logging.info("World")

# Set default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email': ['your_email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Define the DAG
with DAG(
    'simple_hello_world_dag_with_logging',
    default_args=default_args,
    description='A simple Hello World DAG with logging',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    # Define tasks
    task1 = PythonOperator(
        task_id='log_hello',
        python_callable=print_hello,
    )

    task2 = PythonOperator(
        task_id='log_world',
        python_callable=print_world,
    )

    # Set task dependencies
    task1 >> task2
