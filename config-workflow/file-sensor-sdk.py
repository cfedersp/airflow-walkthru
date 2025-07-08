from airflow.sdk import DAG
from airflow.models.taskinstance import TaskInstance
from airflow.models.dagrun import DagRun
from airflow.sensors.filesystem import FileSensor
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator
import pendulum

with DAG(
     dag_id="ProcessFileForDayUsingSDK",
     catchup=False,
     schedule="@daily",
):
  

  fileSensorTask = FileSensor(
      task_id="fileWaitTask",
      fs_conn_id='fs_default',
      filepath="{{ dag_run.conf.get('warehouseDir') }}/{{ dag_run.conf.get('dateDir') }}/{{ dag_run.conf.get('fileName') }}",
      poke_interval=60,  # Check every 60 seconds
      timeout=3600*4,      # Fail after 4 hours
    )
  
  loadTask = EmptyOperator(task_id="generator")
  transformTask = EmptyOperator(task_id="transformer")
  uploadTask = BashOperator(task_id="uploader", bash_command="""
                      echo hello
              """)
  

  fileSensorTask >> loadTask >> transformTask >> uploadTask