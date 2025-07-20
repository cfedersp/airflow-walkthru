from airflow.sdk import Asset
# from airflow.providers.redis import RedisMessageQueueTrigger
from airflow.providers.common.messaging.triggers.msg_queue import MessageQueueTrigger
# from airflow.providers.amazon.aws.triggers.sqs import SQSSensorTrigger
from airflow.sdk import dag, task, AssetWatcher
from airflow.decorators import task
import pendulum

# MessageQueueTrigger
sqsTrigger = MessageQueueTrigger(queue="https://sqs.us-west-2.amazonaws.com/339713066603/CJF_EPSILON_REVIEW_QUEUE")

queueWatcher = Asset("review_queue_asset", watchers=[
        AssetWatcher(
            name="rq-sqs-watcher", 
            trigger=sqsTrigger
        )
    ]);

@dag(start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule=[queueWatcher],
    catchup=False)
def example_sqs_driven_pipeline():
    @task
    def process_data_from_queue(**context):
        triggering_asset_events = context["triggering_asset_events"]
        for event in triggering_asset_events[queueWatcher]:
            # Get the message from the TriggerEvent payload
            print(f"Processing message: {event.extra['payload']['message_batch'][0]['Body']}");
    process_data_from_queue();

example_sqs_driven_pipeline();