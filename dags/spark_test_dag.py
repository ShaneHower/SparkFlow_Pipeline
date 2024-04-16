# spark_test_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
import logging


"""
    TODO: This is finally working.  Some stuff that needs to be done next:
    1. clean up this repo and get it into git.
    2. Lets get this launched into an EC2 so I can start setting up SNS, connect to db, etc
    3. get a lambda to launch this whole thing
"""
logging.info('Hello World!')
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the Python functions to be used as tasks
def print_hello():
    logging.info("Hello")

def print_world():
    logging.info("World")

def submit_and_forget():
    try:
        task = SparkSubmitOperator(
            task_id='submit_spark_test',
            application="/opt/spark/apps/simple-application_2.12-1.0.jar",  # Path inside the container
            name="airflow-spark-test-job",
            conn_id="spark_default",  # Ensure this connection is configured in Airflow
            conf={
            'spark.driver.port': '4040',
            'spark.driver.blockManager.port': '4041',
            },
            total_executor_cores='4',
            executor_cores='4',
            executor_memory='8g',
            num_executors='1',
            verbose=True,
            status_poll_interval=0.5,
            deploy_mode='cluster'
        )
        task.execute(context={})
    except Exception as e:
        logging.info(f'Exception: {e}')

logging.info('Trying to connect')
with DAG(
    'spark_test_dag',
    default_args=default_args,
    description='A simple test DAG to submit a Spark job',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
) as dag:

    submit_spark_job = PythonOperator(
        task_id='submit_and_forget',
        python_callable=submit_and_forget
    )

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
    submit_spark_job >> task1 >> task2
