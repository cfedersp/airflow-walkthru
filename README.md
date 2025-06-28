Tutorials:
https://airflow.apache.org/docs/apache-airflow/stable/tutorial/fundamentals.html

DAG consists of 2 things: DAG Nodes and a flow
A single DAG Node has attributes and a task(operators, Sensors)
A Task can be an Operator or a Sensor
DAG:
+ DAG Nodes
  + attributes
  + Single Task:(Sensor or Operator)
+ Flow

What about DataSets? We may want to trigger a job when vendor uploads today's data, which we can't predict.
Instead of defining sensors and/or a schedule to activate a job, assign a DataSet to the schedule property of a DAG node 
https://airflow.apache.org/docs/apache-airflow/2.5.0/concepts/datasets.html

What if i dont want to declare the execution flow? How to do imperatively? 
TaskFlow: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/taskflow.html

Validate:
python3 my-dag.py

Deploy:
$AIRFLOW_HOME/airflow.cfg specifies the location of a folder for dags that get automatically loaded.
By default, this folder is $AIRFLOW_HOME/dags. Copy your python script there, refresh the dag list after a minute.


Objectives:
Use Operators for a basic dag
Use Annotations for a basic dag
Pass variables from one Task to another ("params")
https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/params.html
Isolate packages using PythonVenvOperator
Get AWS credentials and run aws commands in a job.
Run a java jar within a task
Use DataSet
Use TaskFlow
Error handling:
 - retry a task
 - quit trying and send email