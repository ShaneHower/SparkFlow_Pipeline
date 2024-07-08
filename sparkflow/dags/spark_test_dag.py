# Basic Libraries
import logging
from datetime import datetime, timedelta

# DAG support
from core.config import Config
from utils.helper_functions import get_half_system_resources

# Airflow
from airflow import DAG
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


FILE_TYPE = 'capital_one'

def check_s3_file(config: Config):
    prefix = f'{config.input_location}/{FILE_TYPE}/'
    keys = S3Hook().list_keys(bucket_name=config.bucket_name, prefix=prefix)

    if keys:
        logging.info(f'There are new {FILE_TYPE} files to process')
        return 'submit_and_forget'
    else:
        logging.info(f'There are NO new {FILE_TYPE} files to process')
        return 'file_does_not_exist'


def submit_and_forget(config: Config):
    memory_alloc, cpu_alloc = get_half_system_resources()

    try:
        task = SparkSubmitOperator(
            task_id='submit_spark_test',
            application=f'{config.jar_location}/dag-manager_2.12-1.0.jar',
            name='airflow-spark-test-job',
            conn_id=config.spark_conn_id,
            executor_cores=cpu_alloc,
            executor_memory=f'{memory_alloc}g',
            num_executors='1',
            verbose=True,
            status_poll_interval=0.5,
            deploy_mode='cluster',
            java_class='com.main.DAGManager'
        )
        task.execute(context={})
    except Exception as e:
        logging.info(f'Exception: {e}')


logging.info('Begin')

config = Config()

with DAG(
    'spark_test_dag',
    default_args=config.airflow_default_args,
    description='A simple test DAG to submit a Spark job',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
) as dag:

    check_file_exists = BranchPythonOperator(
        task_id='check_file_exists',
        python_callable=check_s3_file,
        op_kwargs={
            'config': config
        }
    )

    submit_and_forget = PythonOperator(
        task_id='submit_and_forget',
        python_callable=submit_and_forget,
        op_kwargs={
            'config': config
        }
    )

    file_does_not_exist = DummyOperator(
        task_id='file_does_not_exist',
    )


    # Set task dependencies.  We are using the BranchPythonOperator to determine if we should send the spark job or not.
    check_file_exists >> [submit_and_forget, file_does_not_exist]
