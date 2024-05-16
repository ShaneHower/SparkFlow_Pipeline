# spark_test_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta
import logging
import psutil


logging.info('Hello World!')
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def get_half_system_resources():
    total_memory = psutil.virtual_memory().total // (1024 * 1024 * 1024)
    total_cores = psutil.cpu_count()
    return total_memory // 2, total_cores // 2

def print_hello():
    logging.info("Hello")

def print_world():
    logging.info("World")

def submit_and_forget():
    memory_alloc, cpu_alloc = get_half_system_resources()

    try:
        task = SparkSubmitOperator(
            task_id='submit_spark_test',
            application="s3a://picklepokeyhouse/sparkflow_jars/dag-manager_2.12-1.0.jar",  # Path inside the container
            name="airflow-spark-test-job",
            conn_id="spark_default",  # Ensure this connection is configured in Airflow
            conf={
                'spark.driver.port': '4040',
                'spark.driver.blockManager.port': '4041',
                'spark.hadoop.fs.s3a.impl': 'org.apache.hadoop.fs.s3a.S3AFileSystem',
                'spark.hadoop.fs.s3a.endpoint': 's3.amazonaws.com',
                'spark.hadoop.fs.s3a.path.style.access': 'true'
            },
            executor_cores=cpu_alloc,
            executor_memory=f'{memory_alloc}g',
            num_executors='1',
            verbose=True,
            status_poll_interval=0.5,
            deploy_mode='cluster',
            java_class='com.main.DAGManager',  # Specify the main class here
            jars='/opt/spark/jars/hadoop-aws-3.3.1.jar,/opt/spark/jars/aws-java-sdk-bundle-1.11.874.jar'
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
