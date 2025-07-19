# Purpose
This repo is an introduction to Airflow including a walk though consisting of a series of relatable examples.<br/>
The official Airflow documentation is extensive, but it does little to help the uninitiated run practical examples quickly.<br/>
The Quickstart isn't helpful in evaluating Airflow professionally.
DAG inlets and outlets, required method signatures, and the filesystem connector are not explained concisely, so these concepts and others are provided here to absorb at a glance.<br/>

# Parsing vs Instantiating vs Task Execution
DAGs are defined in python, but you cannot consistently write and read global scope python variables (runs on the scheduler) within Task factory methods (run on workers). dag_run.conf is not available outside an operator or sensor attribute. The dag Resource only has attributes related to scheduling. A global scope variable can only be used in an attribute at time of **parsing**, not when the DAG Run is instantiated or executed.

Tutorials:
https://airflow.apache.org/docs/apache-airflow/stable/tutorial/fundamentals.html

DAG consists of 2 things: DAG Nodes and a flow
A single DAG Node has attributes and a task(operators or Sensors)
A Task can be an Operator or a Sensor
DAG:
+ Dag Scheduling Attributes
+ Assets (data] [asset watcher]
+ DAG Nodes (Tasks)
  + Task attributes
  + Task Impl:(Sensor or Operator)
+ Flow (Sequence of Tasks)

# Dag and Task Scheduling
Ways the Scheduler will instantiate a DAG:
Manually through the UI.
Manually through the Command Line
REST call
schedule (DAG attribute)
schedule_interval (DAG attribute)
Asset Watcher (Assets are global).

Tasks are chained using chain(*args) method or the bitshift >> operator. Join multiple upstream tasks in using chain by giving an array of tasks or if using >> give the same task instance multiple times.
In general, downstream tasks get activated when all upstream tasks complete - but if a successor task has an empty Asset inlet, it will also wait for that Asset to produce an event.

# FileSensor vs Asset vs AssetWatcher:
FileSensor checks for existence of a file. filepath attribute does not require scheme.
Asset emits events related to a dataset (may be file, may be something else) that activate asset consumer tasks. Asset uri requires scheme.
Asset Watcher is an Asset with the watcher attribute and triggers a DAG.

# Dictionary
**Airflow Providers**: A provider is a python package that supplies integration with a cloud provider. Ex: S3 Object Store is accessed with the AWS provider package. The provider package is a dependency that must be installed and a S3 Connection must be provided before S3 can be accessed from a DAG.
**DAG**: A python script that defines a graph of tasks that represent a workflow.<br/>Named by the dag_id attribute or the name of the @dag annotated factory method.
**DAG Folder**: This is the directory within the Airflow scheduler where ad-hoc DAGs are parsed and ingested into the Airflow database. Airflow ingests new DAGs every 30 seconds. This folder is useful for local development, but production should use DAG Bundles or enable a git plugin to read versioned DAGs.
**DAG Run**: This is an instance of a DAG. It can be in 'queued', 'running', 'paused', 'completed' states. A triggered dag may start in 'paused' state and will proceed by unpausing it either from the command line or the UI.
**DAG Schedule**: 'schedule' and 'schedule_interval' are attributes of a DAG. 'schedule' can be a cron, timedelta, timetable, or Asset Watcher. Airflow 2.x allowed Dataset in the schedule attribute, but that is now deprecated.
**DAG Bag**:<br/>
**DAG Bundle**:https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/dag-bundles.html<br/>
**Task**: A step in a workflow. Can be an Operator or a Sensor.<br/>
**Operator**: This is a task within a DAG that executes a method.<br/>
**Sensor**: This is a task within a DAG that polls an external resource for a condition. It is a wait condition within the workflow- it cannot by itself trigger a new DAG Run. <br/>It is stateless - it does not remember the result of previous polls. <br/>
**DataSet**: This is the Airflow 2.x concept for a logical grouping of data. It has been deprecated and replaced in Airflow 3.x with Assets.<br/>
**Task Inlets**:A task can have an inlets attribute that is an array of upstream task outlets.<br/>
**Task Outlets**:A task can have an outlet attribute that is an array of names for its generated data. The task returns a dictionary whose keys match the outlet names. Those names can be used as inlets by downstream tasks.<br/>
**Asset**: This is the Airflow 3.0 concept for a logical grouping of data that can be referred to by producer and consumer tasks. An Asset definition is preprocessed into its own DAG and references to it from tasks are automatically defined to be the new DAG's inlets or outlets.Assets can be used in producer task 'outlets' attribute and consumer tasks 'schedule' and 'inlets' attributes.Inlets and outlets refer to data within the Asset. A task's schedule composed of assets can have boolean logic that specifies whether the task should be triggered when those Assets are created, updated, or aliased.<br/>
**Asset Inlet**:<br/>
**Asset Outlet**:<br/>
**Asset Alias**:<br/>
**Asset Producer Task**: <br/>
**Asset Consumer Task**: This is a task that is activated when its inlet asset is created, changed or aliased.<br/>
**Asset Watcher**: An asset by itself cannot trigger a DAG. Only when the Asset includes a watcher. An Asset Watcher exists outside any DAGs and may trigger a DAG by an file create or update or an event from a message queue. Read Event-driven Scheduling for more information: https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/event-scheduling.html
**Custom Asset**:<br/>
**Connection**: A Connection provides integration details, including hostname and credentials for external systems. Different types support uri schemes. Connections can be provided in the UI or as environment variables. Even the local filesystem provider must be specified as a Connection or you will see an <br/>
**Hooks**: A Hook builds off a particular Connection and provides a consistent interface for interacting with it. Example?
**XCOM**:<br/>
**Executor**: This is the pluggable component that queues tasks for execution on worker(s)<br/>
    LocalExecutor
    CeleryExecutor
    SerialExecutor
    Kubernetes Executor

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

# Troubleshooting
AirflowNotFoundException: The conn_id `fs_default` isn't defined
Make sure you created a filesytem Connection in your Airflow runtime environment or Airflow UI.
airflow connections add 'fs_default' --conn-type 'fs'

FileSensor immediately succeeds when file given by filepath attribute does not exist:
Sensor is setup incorrectly.
Dont use the decorators like @task and @task.sensor as factory methods. The decorators are used to define a custom Tasks. Those methods are called by a PythonOperator that is serialized and run on workers. @task.sensor annotated method doesn't return a sensor - it IS THE SENSOR and must return PokeReturnValue.

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
Example:
cp config-workflow/file-sensor.py $AIRFLOW_HOME/dags/

Delete DAG metadata from DB:
airflow dags delete ProcessFileForDay

Config Examples:
airflow dags trigger --conf '{"warehouseDir": "/tmp", "dateDir": "2025-07-08", "fileName":"inventory.json"}' ProcessFileForDay
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

Trigger: 
This is similar to an Sensor, but it executed in a single **trigggerer** instead of a worker, freeing up atask-slot until the trigger returns an event.

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

 # Chat Session:
 **Prompt**: A number of engineers are learning how to use Apache Airflow so they can refactor a number of sophisticated workflows to be implemented as DAGs that are run and managed within it. They need sufficient knowledge to decide whether Airflow is an adequate tool to adopt. They currently only know java, python, Spring Framework and Hibernate without docker containers. List the high level Airflow concepts and detail the purpose of each to someone that has never used it before.
**Response 1** 
Apache Airflow is an open-source platform designed to programmatically author, schedule, and monitor complex workflows. It’s particularly powerful for orchestrating data pipelines. For engineers familiar with Java, Python, Spring Framework, and Hibernate, it may require some adaptation but knowing Python will certainly help as Airflow is written in Python. Below are the high-level concepts of Apache Airflow, detailed in a way that should be approachable:
1.	DAG (Directed Acyclic Graph):
o	Purpose: At the heart of Airflow is the concept of a DAG, which is a collection of tasks organized in a way that reflects their dependencies with each other. The DAG defines the sequence in which these tasks are executed. It’s like a workflow template where each node represents a task, and the directed edges define the execution order.
o	Analogy: Think of it like a flowchart that outlines each step in a process and the order in which they need to be completed.
2.	Task:
o	Purpose: A Task is a node in the DAG that performs a single unit of work. It's an implementation of a step within the DAG and can be anything from running a Python script, executing a SQL command, sending emails, etc.
o	Analogy: Similar to a method or a function call in programming where a specific operation is executed.
3.	Operator:
o	Purpose: Operators are the building blocks of Airflow, which determine what actually gets done in each task. They are predefined templates for specific types of tasks, such as executing a Python script (PythonOperator), running a command in the shell (BashOperator), or kicking off an external process (SimpleHttpOperator, etc.).
o	Analogy: These are like pre-built functions/methods you can call to perform common actions without needing to write all the code yourself.
4.	Task Instance:
o	Purpose: It's the run-time instance of a task that provides contextual data and tracks the state and output of tasks. It’s essentially a specific run of a task with its execution context.
o	Analogy: Comparable to the invocation of a method in an object-oriented language that carries its own execution state and context.
5.	Executor:
o	Purpose: This determines how tasks are executed by Airflow. Executors can manage the distribution and parallelism of task execution across a pool of workers. Examples include the SequentialExecutor (for debugging or low-scale environments), LocalExecutor (for running on a single machine), and CeleryExecutor (for distributed execution).
o	Analogy: Like a task runner that decides where and how your method calls should be processed depending on your environment setup.
6.	Scheduler:
o	Purpose: The scheduler is a vital component that orchestrates the execution of tasks by monitoring all DAGs and scheduling their associated tasks as per dependencies and execution frequency (often defined using cron syntax).
o	Analogy: Similar to a cron job scheduler but much more sophisticated, keeping track of complex dependencies and schedules in a workflow.
7.	Worker:
o	Purpose: Workers are the entities that execute the tasks. Depending on the chosen executor, you might have multiple workers which retrieve tasks from the queue to execute in parallel.
o	Analogy: In a server-client architecture, they act like servers that actually perform the computation work as requested by the client.
8.	Metadata Database:
o	Purpose: Airflow uses a metadata database (usually a relational database like PostgreSQL or MySQL) to store status, configurations, and logs of the task executions. It acts as the single source of truth for the state of your DAGs.
o	Analogy: This can be seen as the 'brain' of Airflow that retains all runtime information, akin to a persistent data store in a distributed application.
9.	Web UI:
o	Purpose: Airflow includes a rich web-based UI for easier management and monitoring of DAGs. Users can view task schedules and status, logs, and even trigger or modify DAGs manually.
o	Analogy: Like a dashboard in a monitoring tool that shows real-time insights and status of your systems/applications.
10.	Logs:
o	Purpose: Airflow logs provide detailed output on what happened during task execution, making debugging and oversight easier.
o	Analogy: Similar to logs in a server application, they give insights into what's happening under the hood, helping diagnose issues.
Understanding these concepts will help engineers evaluate Apache Airflow's capabilities against their needs for orchestrating complex workflows and managing task dependencies effectively. Once accustomed to these concepts, engineers will be able to refactor their workflows using Airflow effectively.
 
**Prompt**: Explain the purpose of each of these Airflow components:
**DAG**
**DAG Run**
**DAG Inlet**
**DAG Outlet**
**DAG Bag**
**DAG Bundle**:
**Task**
**Operator**
**Sensor**
**Task Inlet**
**Task Outlet**
**Asset**
**Asset Alias**
**Asset Producer Task**
**Asset Consumer Task**
**Custom Asset Scheme**
**Connection**
**XCOM**
**Executor**
Certainly! Here's an explanation of each Apache Airflow component, covering both the core concepts and some of the more advanced or less common features:

**DAG (Directed Acyclic Graph)**:
Purpose: A DAG is a top-level structure in Airflow that organizes a series of tasks with defined dependencies and execution order. It ensures tasks are scheduled and executed in a specified sequence, forming a complete workflow from start to finish.
**DAG Run**:
Purpose: A DAG Run represents an individual execution instance of a DAG. Each run corresponds to an execution date and maintains its own state, allowing you to track when and how successfully the DAG was executed.
**DAG Bag**:
Purpose: A DAG Bag is a collection of all the DAGs that Airflow has loaded. It's essentially a container that houses all defined DAG objects that Airflow can discover, manage, and execute.
**DAG Bundle**:
Purpose: Although not a standard term in the Airflow ecosystem, it might relate to a group of related DAGs that are managed collectively, often for organizational and versioning purposes.
**Task**:
Purpose: A Task is a basic execution unit within a DAG, defined by operators. It represents a single step in your workflow and can include operations like data extraction, transformation, loading, and more.
**Operator**:
Purpose: An Operator defines a specific operation that a task will perform. They range from executing Python code, triggering external scripts, interacting with databases, and more. Operators provide reusable templates for standard task functionalities.
**Sensor**:
Purpose: A Sensor is a special type of Operator in Airflow that blocks the execution of a workflow until a certain condition is met—such as a file appearing in a directory or an event occurring at an external system.
**Task Inlet**:
Purpose: Task Inlet refers to the set of inputs or prerequisites required for a particular task within a DAG. It denotes what data or conditions are needed for the task to execute.
**Task Outlet**:
Purpose: Task Outlet specifies the outputs of a task, indicating what data or results the task produces and possibly what subsequent tasks can consume.
**Asset**:
Purpose: In a data pipeline context, an Asset usually refers to a data entity or artifact, such as a dataset, file, or database table that is manipulated or produced during DAG execution.
**Asset Alias**:
Purpose: An Asset Alias provides alternative naming to assets to improve clarity or relevance in workflows, potentially enhancing asset management across DAGs and projects.
**Asset Producer Task**:
Purpose: This task is responsible for creating or updating an asset, paving the way for subsequent consumption by other tasks or workflows. It ensures data provisioning for the workflow.
**Asset Consumer Task**:
Purpose: An Asset Consumer Task is designed to utilize an asset produced by another task. It relies on the correct and timely provision of these assets to function accurately.
**Custom Asset Scheme**:
Purpose: A Custom Asset Scheme allows the definition of custom identifiers or schemas for assets, facilitating better organization, compatibility, and consistency in workflows and data management.
**Connection**:
Purpose: Connections in Airflow are used to define information needed to connect to external systems, services, or databases. They encapsulate authentication credentials and configuration details, abstracting them from task logic.
**XCOM (Cross-Communication)**:
Purpose: XCOM, short for Cross-Communication, allows for the transfer of small amounts of data between tasks within a DAG. XCOMs enable inter-task communication and state sharing to facilitate dynamic workflow behaviors.
**Executor**:
Purpose: An Executor handles the scheduling and running of tasks. It determines how Airflow distributes and executes tasks across available resources, supporting scalable and efficient workflow execution. Executors range from simple (SequentialExecutor) to distributed (CeleryExecutor).
These components come together to form a robust platform for orchestrating, scheduling, and monitoring complex workflows, allowing for flexibility and efficiency in managing data pipelines and other automation tasks.
 
