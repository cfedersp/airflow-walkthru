import asyncio
import hashlib

from airflow.triggers.base import BaseEventTrigger, TriggerEvent
from airflow.providers.jdbc.hooks.jdbc import JdbcHook

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults


class JDBCTableTrigger(BaseEventTrigger):
    def __init__(self, conn_id, ingest_select, interval_seconds, update_statement, bind_values):
        super.__init__()
        self.jdbc_conn_id = conn_id;
        self.ingest_select = ingest_select;
        self.interval_seconds = interval_seconds;
        self.update_statement = update_statement;
        self.bind_values = bind_values;
        # TODO: validate:
        # select statement must be SELECT
        # update_statement must be UPDATE and have as many placeholders as there are bind_values
        # bind values must be a tuple or a list

    def serialize(self) -> tuple[str, dict[str, str]]:
        return {"JDBCTableTrigger", {"conn_id": self.conn_id, "ingest_select": self.ingest_select, "id_column": self.id_column, "update_statement": self.update_statement, "interval_seconds": self.interval_seconds} };


    async def run(self):
        hook = JdbcHook(redis_conn_id = self.redis_conn_id);
        while True:
            conn = hook.get_conn();
            cursor = conn.cursor()
            cursor.execute(self.ingest_select) 

            column_names = [desc[0] for desc in cursor.description]

            results = cursor.fetchall()
            for row in results:
                row_dict = dict(zip(column_names, row))
                idValue = row_dict[self.id_column];
                cursor.execute(self.update_statement, self.bind_values);
                conn.commit();
                yield TriggerEvent(row_dict);
                return;
            await asyncio.sleep(self.interval_seconds)
    def cleanup():
        return

    def hash(self, classpath, kwargs):
        return hashlib.md5(classpath + self.serialize());

