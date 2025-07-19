import asyncio
import hashlib

from airflow.triggers.base import BaseEventTrigger, TriggerEvent
from airflow.providers.redis.hooks.redis import RedisHook

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

class RedisKeyTrigger(BaseEventTrigger):
    def __init__(self, redis_conn_id, queue_name):
        super.__init__()
        self.redis_conn_id = redis_conn_id;
        self.queue_name = queue_name;

    def serialize(self) -> tuple[str, dict[str, str]]:
        return {"RedisKeyTrigger", {"redis_conn_id": self.redis_conn_id, "queue_name": self.queue_name} };


    # RedisHook gives us key lookup. we need queue poll. with pika
    async def run(self):
        hook = RedisHook(redis_conn_id = self.redis_conn_id);
        while True:
            redis_value = hook.get_conn().get(self);
            if redis_value is not None:
                yield TriggerEvent(redis_value)
                return;
            await asyncio.sleep(5)
    def cleanup():
        return

    def hash(self, classpath, kwargs):
        return hashlib.md5(classpath + self.serialize());

class RedisSensor(BaseOperator):
    @apply_defaults
    def __init__(self, redis_conn_id: str, key: str, value: str = None, **kwargs):
        super().__init__(**kwargs)
        self.redis_conn_id = redis_conn_id
        self.key = key
        self.value = value

    def execute(self, context):
        self.defer(
            trigger=RedisKeyTrigger(
                redis_conn_id=self.redis_conn_id, key=self.key, value=self.value
            ),
            method_name="execute_complete",
        )

    def execute_complete(self, context, event=None):
        self.log.info(f"RedisKeySensor complete. Event: {event}")
        # Further processing based on the event payload (e.g., key_value)
        return "Done"