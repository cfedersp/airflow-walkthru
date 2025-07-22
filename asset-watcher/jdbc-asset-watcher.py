from typing import Any
from airflow.sdk import Asset
from airflow.sdk import dag, task, AssetWatcher
from airflow.decorators import task
import pendulum

import asyncio
import hashlib

from airflow.triggers.base import BaseEventTrigger, TriggerEvent
from airflow.providers.jdbc.hooks.jdbc import JdbcHook

from airflow.models.baseoperator import BaseOperator


class JDBCTableTrigger(BaseEventTrigger):
    def __init__(self, jdbc_conn_id, ingest_select, interval_seconds, id_column, update_statement, bind_values=()):
        super().__init__()
        self.jdbc_conn_id = jdbc_conn_id;
        self.ingest_select = ingest_select;
        self.interval_seconds = interval_seconds;
        self.id_column = id_column;
        self.update_statement = update_statement;
        self.bind_values = bind_values;
        # TODO: validate:
        # select statement must be SELECT
        # update_statement must be UPDATE and have as many placeholders as there are bind_values
        # bind values must be a tuple or a list

    def serialize(self) -> tuple[str, dict[str, Any]]:
        triggerParams = {"jdbc_conn_id": self.jdbc_conn_id, "ingest_select": self.ingest_select, "interval_seconds": self.interval_seconds, "id_column": self.id_column, "update_statement": self.update_statement, "bind_values": self.bind_values };
        return ("jdbc-asset-watcher.JDBCTableTrigger", triggerParams );


    async def run(self):
        hook = JdbcHook(jdbc_conn_id = self.jdbc_conn_id);
        while True:
            conn = hook.get_conn();
            cursor = conn.cursor()
            cursor.execute(self.ingest_select) 

            column_names = [desc[0] for desc in cursor.description]

            results = cursor.fetchall()
            for row in results:
                print("reading row from db");
                row_dict = dict(zip(column_names, row))
                idValue = row_dict[self.id_column];
                cursor.execute(self.update_statement, (idValue, ));
                conn.commit();
                yield TriggerEvent(row_dict);
                return;
            await asyncio.sleep(self.interval_seconds)
    def cleanup(): # Parent impl should be OK - DELETE THIS
        return

    def hash(self, classpath, kwargs): # Parent impl should be OK - DELETE THIS
        return hashlib.md5(classpath + self.serialize());


database = "cfederspiel"
sqlTrigger = JDBCTableTrigger(jdbc_conn_id="oracle", interval_seconds=30, ingest_select=f"select SID, REVIEW_TYPE, STATUS, AIRFLOW_INGESTED_DATE, CREATED_DATE from {database}.REVIEW_QUEUE", id_column="SID", update_statement=f"UPDATE {database}.REVIEW_QUEUE set AIRFLOW_INGESTED_DATE=NOW() where SID=?")
# max_messages

queueWatcher = Asset("review_queue_asset", watchers=[
        AssetWatcher(
            name="rq-watcher", 
            trigger=sqlTrigger
        )
    ]);

@dag(start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule=[queueWatcher],
    catchup=False)
def review_queue_pipeline():
    @task
    def process_data_from_review_queue(**context):
        triggering_asset_events = context["triggering_asset_events"]
        # triggers can only emit a single event, but keep this until that is verified in practice.
        for event in triggering_asset_events[queueWatcher]:
            # Get the message from the TriggerEvent payload
            print(f"Processing row! Columns: { event.extra.keys() }. entire dict: {event.extra}");
    process_data_from_review_queue();

review_queue_pipeline();