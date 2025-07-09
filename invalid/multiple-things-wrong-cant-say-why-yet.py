# from airflow.sdk import dag, task
from airflow.models.taskinstance import TaskInstance
from airflow.models.dagrun import DagRun
from airflow.sensors.filesystem import FileSensor
from airflow.decorators import dag, task
import pendulum

@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)

def ProcessFileForDay():
  waitForFile = "";
  
  @task()
  def createInventoryFileSensor(**context):
    waitForFile = f"{ context['dag_run'].conf.get('warehouseDir') }/{ context['dag_run'].conf.get('dateDir') }/{ context['dag_run'].conf.get('fileName') }"
    print(f"waiting for input file: { waitForFile }");

    return FileSensor(
        task_id="fileWaitTask",
        fs_conn_id='fs_default',
        filepath=waitForFile,
        poke_interval=60,  # Check every 60 seconds
        timeout=3600*4,      # Fail after 4 hours
    )
  @task()
  def loadFile():
    print(f"Loading input file: { waitForFile }");

  @task()
  def transformFile():
    print("Transforming file");
  
  @task.bash()
  def uploadFile():
    print("hello java jar!")
    return f"/Users/chafeder/opt/amazon-corretto-17.jdk/Contents/Home/bin/java -jar /Users/chafeder/projects/poc/syncjob/target/syncjob-0.0.1-SNAPSHOT.jar /Users/chafeder/projects/poc/syncjob/src/test/resources/review-queue/minimal.json"

  fileSensorTask = createInventoryFileSensor();
  
  loadTask = loadFile();
  transformTask = transformFile();
  uploadTask = uploadFile();

  fileSensorTask >> loadTask >> transformTask >> uploadTask
ProcessFileForDay();