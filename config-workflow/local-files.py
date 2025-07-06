from airflow.sdk import dag, task
from airflow.models.taskinstance import TaskInstance
from airflow.models.dagrun import DagRun
from airflow.sensors.filesystem import FileSensor
# from airflow.decorators import task
import pendulum

@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)

def ProcessFileForDay():

  @task.sensor
  def createFileWait(task_instance: TaskInstance, dag_run: DagRun):
    return FileSensor(
        task_id="fileWaitTask",
        filepath=f"file://{ dag_run.conf.get('warehouseDir') }/{ dag_run.conf.get('dateDir') }/{ dag_run.conf.get('fileName') }",
        poke_interval=60,  # Check every 60 seconds
        timeout=3600*4,      # Fail after 4 hours
  )
  @task()
  def loadFile():
    print("Loading input file");

  @task()
  def transformFile():
    print("Transforming file");
  
  @task.bash()
  def uploadFile():
    print("hello java jar!")
    return f"/Users/chafeder/opt/amazon-corretto-17.jdk/Contents/Home/bin/java -jar /Users/chafeder/projects/poc/syncjob/target/syncjob-0.0.1-SNAPSHOT.jar /Users/chafeder/projects/poc/syncjob/src/test/resources/review-queue/minimal.json"

  fileWaitTask = createFileWait();
  loadTask = loadFile();
  transformTask = transformFile();
  uploadTask = uploadFile();

  fileWaitTask >> loadTask >> transformTask >> uploadTask
ProcessFileForDay();