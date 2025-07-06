from airflow.sdk import dag, task
# from airflow.decorators import task
import pendulum

@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)

def SyncFromReviewObject():
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

  #loadTask = loadFile();
  #transformTask = transformFile();
  #uploadTask = uploadFile();

  # loadTask >> transformTask >> uploadTask
  loadTask = loadFile();
  transformTask = transformFile();
  uploadTask = uploadFile();

  loadTask >> transformTask >> uploadTask
SyncFromReviewObject();
