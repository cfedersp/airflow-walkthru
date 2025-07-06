import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator


# only import the libs you need to define the DAG
# If some operators are python, they can run in their own env. how?

dagName = "hello-world"

# Define operators:
with DAG(
     dag_id=dagName,
     start_date=datetime.datetime(2021, 1, 1),
     catchup=False,
     schedule="@daily",
):
    generator = EmptyOperator(task_id="generator")
    transformer = EmptyOperator(task_id="transformer")
    uploader = BashOperator(task_id="uploader", bash_command="""
                            echo hello
                """)
# Now use the variables to compose the flow
# with does not create a new scope, so this composition doesn't need to be nested
    generator >> transformer >> uploader