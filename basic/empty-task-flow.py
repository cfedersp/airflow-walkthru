import datetime

from airflow.sdk import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator


# only import the libs you need to define the DAG
# If some operators are python, they can run in their own env. how?

dagName = "empty-taskflow"

# Define a DAG Resource Manager
with DAG(
     dag_id=dagName,
     start_date=datetime.datetime(2021, 1, 1),
     catchup=False,
     schedule="@daily",
):
    # Define Operators
    generator = EmptyOperator(task_id="generator")
    transformer = EmptyOperator(task_id="transformer")
    uploader = BashOperator(task_id="uploader", bash_command="echo 'aws s3 cp'",)

    # Define the flow
    generator >> transformer >> uploader