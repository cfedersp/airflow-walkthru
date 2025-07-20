from airflow.sdk import Asset
# from airflow.providers.redis import RedisMessageQueueTrigger
# from airflow.providers.common.messaging.triggers.msg_queue import MessageQueueTrigger
from airflow.providers.amazon.aws.triggers.sqs import SqsSensorTrigger
from airflow.sdk import dag, task, AssetWatcher
from airflow.decorators import task
import pendulum

# https://www.astronomer.io/docs/learn/airflow-event-driven-scheduling/
# Enable the DAG with the slider - no need to trigger it manually
# aws configure list-profiles (in case you dont have the profile name for aws cli)

# SQS_QUEUE_URL="https://sqs.us-west-2.amazonaws.com/339713066603/CJF_EPSILON_REVIEW_QUEUE"
# aws sqs send-message --queue-url $SQS_QUEUE_URL --message-body "{'reviewType':1111111,'sid':'348938943348','status':'CREATED'}" --profile identity-center-user-profile
sqsTrigger = SqsSensorTrigger(aws_conn_id="aws_default", waiter_delay=30, sqs_queue="https://sqs.us-west-2.amazonaws.com/339713066603/CJF_EPSILON_REVIEW_QUEUE")
# max_messages

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
        # triggers can only emit a single event, but keep this until that is verified in practice.
        for event in triggering_asset_events[queueWatcher]:
            # Get the message from the TriggerEvent payload
            print(f"Processing message: {event.extra['payload']['message_batch'][0]['Body']}");
    process_data_from_queue();

example_sqs_driven_pipeline();