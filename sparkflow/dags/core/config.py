from datetime import timedelta

class Config:
    def __init__(self):
        """This class is here for convenience, it stores variables that are shared throughout every DAG.  This is helpful
        as we only have to change these DAG variables in one place if the need arises.

        Attributes:
            bucket_name: S3 bucket name
            input_location: The location where we are monitoring input files
            jar_location: We store the JARs on S3 and pass them into the spark cluster to execute.
            spark_conn_id: The name of the Airflow connection ID for the spark cluster we are running on
            airflow_default_args: Airflow default arguments for a basic DAG
        """
        # S3 info
        self.bucket_name = 'picklepokeyhouse'
        self.input_location = 'finances/monitored_input/input'
        self.jar_location = 's3a://picklepokeyhouse/sparkflow_jars'


        # Airflow info
        self.spark_conn_id = 'spark_default'
        self.airflow_default_args = {
            'owner': 'airflow',
            'depends_on_past': False,
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        }
