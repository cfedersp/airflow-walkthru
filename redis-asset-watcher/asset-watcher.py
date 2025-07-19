from airflow.models.dag import DAG
from airflow.sdk import Asset
# from airflow.providers.redis import RedisMessageQueueTrigger
from airflow.providers.common.messaging.triggers.msg_queue import MessageQueueTrigger
from airflow.sdk import AssetWatcher
from airflow.decorators import task
import pendulum

queueWatcher = Asset("review_queue_asset", watchers=[
        AssetWatcher(
            name="demo-redis-watcher", 
            trigger=MessageQueueTrigger( 
                queue="redis://SC1WASPNAPP03.res.prod.global:6383/CJF_REVIEW_QUEUE"
            )
        )
    ]);

with DAG(
    dag_id="example_event_driven_pipeline",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule=[queueWatcher],
    catchup=False,
) as dag:
    @task
    def process_data_from_queue(context, queueWatcher):
        print(f"Processing data from the queue: { queueWatcher[-1].extra }")