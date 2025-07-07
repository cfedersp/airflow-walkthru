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

# Dictionary
**DAG**: Represents a graph of tasks that represent a workflow.
**Task**: A step in a workflow. Can be an Operator or a Sensor
**Operator**:
**Sensor**: This is a task that polls for a certain condition. It is a wait condition within an existing DAGRun instance, it does not trigger a new job. 
**DataSet**: This is the Airflow 2.x metaphor for a logical grouping of data. It has been deprecated and replaced in Airflow 3.x with Assets.
**Asset**: This is the Airflow 3.0 metaphor for an abstract task representing a logical grouping of data that can be referred to by producer and consumer tasks. Assets act as a soft dependency between your workflow and external processes (other DagRuns or unrelated components)
**Asset Alias**:
**Asset Outlet**:
**Asset Producer Task**: this is a task that 
**Asset Inlet**:
**Asset Consumer Task**: This is a task that is activated when its inlet asset is created, changed or aliased.
**Custom Asset**:
**Connection**:
**XCOM**:
**Executor**: The component that queues tasks for execution on worker(s)
    CeleryExecutor
    SerialExecutor

# Configuring DAGs:
- UI Params
Params appear in the Airflow UI, and can be used to manually trigger DAGs from a web browser, but have nowhere else. Hosted airflow may not support params at all.

- DAG Run Config do not appear in the UI, but can be passed from the command line or REST. 
    Run Config CLI Usage:
        airflow trigger_dag --conf {"dealerInventoryFileName": "/path/to/file"} dag_id
    Run Config Python Usage:
        dag_run.conf.get("dealerInventoryFileName")

- Jinja Template Variables: Arguments to operators are parsed as jinja templates using predefined variables. 
    Ex: env="{{ logical_date }}"
    Doesn't work with @task decorator
    Templated fields are marked 'templated' in Airflow documentation.
    Template Reference: https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html

- Provided vars:
    dag_run: globals for that particular run instance

# Custom Operators
Operator has methods: 
 - pre_execute: performs jinja templating
 - execute
 - post_execute: cleanup

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

Running Workflows:
DAGs can include Tasks (Sensors, Operators)
A DAG must already be running for any of those to actually work.
A DAG can be triggered from the UI, Command Line, or REST.
Can a DAG start a run of another DAG? probably?
Bottom line is Airflow gives us a 'reactive' platform, but it doesn't react to external events - it reacts to well defined events within itself.






Config Examples:
airflow dags trigger --conf '{"warehouseDir": "/tmp", "dateDir": "2025-07-06", "fileName":"inventory.json"}' ProcessFileForDay
airflow dags unpause ProcessFileForDay
AirflowNotFoundException: The conn_id `fs_default` isn't defined
Make sure you created a filesytem connection
mkdir -p /tmp/2025-07-06/
touch /tmp/2025-07-06/inventory.json

Asset Driven Tasks:
@asset consumer-task args are: context, inlet-asset-names..
@asset producer-task args are: self, context
'name' and 'uri' attributes are required, but if there are upstream asset-tasks, then only 1 is needed.
inlet-asset-names are not positional args! The annotation is re-written as @task(inlets=[inlet-asset-names..])
Asset events: [on_asset_created, on_asset_changed, on_asset_alias_created]
Get asset event trigger(s) within a consumer: context["inlet_events"][asset1]

Using FileSensor & Asset together:
FileSensor is limited to answering 1 of 2 questions:
Dir: Are there any files in that directory?
File: Does that file exist?

Objectives:
Use Operators for a basic dag - done.
Use TaskFlow Annotations for a basic dag - done
Pass variables from one Task to another ("params")
https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/params.html
Isolate task impls using PythonVenvOperator
Get AWS credentials and run aws commands in a job.
Run a java jar within a task. -done
Airflow 2.0:
Create a DAG using a DataSet
Create a DAG using a composite DataSet of multiple object types under a single tenant or client.
Create a DAG with a DataSet and a Sensor dependency
Airflow 3.0:
Create a DAG with a task that has Asset outputs (outlets=[asset1,asset2])
Create a DAG with a task that has an Asset dependency/responds to an asset updated event (schedule=[asset1,asset2]) 
Use inlets and inlet_events and outlet_events
use variables in an Asset URI
Create DAGs with cross-communication (XCOM)
Create a DAG using Assets with custom scheme (starts with "x-". Ex: "x-aia-campaign-up")
Create a DAG that has conditional logic with BranchPythonOperator.
Create a DAG that short circuits the remaining tasks with ShortCircuitOperator (or @task.short_circuit.
Error handling:
 - retry a task
 - quit trying and send email

 Advanced:
 Custom TimeTable: https://airflow.apache.org/docs/apache-airflow/stable/howto/timetable.html
 Extend BaseOperator: https://airflow.apache.org/docs/apache-airflow/stable/howto/custom-operator.html
 Customize the view: https://airflow.apache.org/docs/apache-airflow/stable/howto/custom-view-plugin.html