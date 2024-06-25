# Basic Libraries
import logging
from datetime import datetime, timedelta

# DAG support
from core.config import Config
from utils.helper_functions import get_half_system_resources

# Airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


def check_s3_file(config: Config):
    key = f'{config.input_location}/capital_one'
    return S3Hook().check_for_key(key, config.bucket_name)


def submit_and_forget(config: Config, file_exists: bool):
    if file_exists:
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

    else:
        logging.info('There is no Capital One file in input location.  Nothing to process.')


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

    check_file_exists = PythonOperator(
        task_id='check_s3_file_exists',
        python_callable=check_s3_file,
        op_kwargs={
            'config': config
        }
    )

    submit_spark_job = PythonOperator(
        task_id='submit_and_forget',
        python_callable=submit_and_forget,
        op_kwargs={
            'config': config
        }
    )


    # Set task dependencies
    check_file_exists >> submit_spark_job
