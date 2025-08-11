import docker
import pathlib
import time

# import argparse

# Its easier to launch an airflow container than install airflow.
# We aren't actually running the DAGs in Airflow, just using its python environment.

# This doesn't run the harness -it runs docker exec to run the harness
# This controller script: start the container, mounting the dir containing the script that performs the validation.
# Then it tells docker to execute the test harness

# https://docker-py.readthedocs.io/en/stable/containers.html#container-objects
# https://faun.pub/a-simple-way-to-validate-your-airflow-dags-upon-pull-request-1b25f19dd496

# This script does the same as:
# docker run --name airflow-qa -d -p 8080:8080 -v $(pwd)/test-results:/opt/test-results -v $(pwd):/opt/testdags apache/airflow:slim-3.0.3-python3.12  airflow standalone
# no need to copy the dags to a staging dir since we mounted current dir
# docker exec -it airflow-qa /bin/bash
# python /opt/testdags/automated-test/import-dagbag.py
# pip install pytest
# pytest --override-ini=cache_dir=/opt/test-results /opt/testdags/automated-test/import-dagbag.py

def run_airflow(standalone_image, rw_volume_spec={}, ro_volume_spec={}):
    rw_volume_mounts = dict();
    if not rw_volume_spec:
        rw_volume_mounts = dict(map(lambda item: (item[0], {"bind": item[1], "mode": "rw"}), rw_volume_spec.items()))
    if not ro_volume_spec:
        ro_volume_mounts = dict(map(lambda item: (item[0], {"bind": item[1], "mode": "ro"}), ro_volume_spec.items()))
    client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    client.images.pull(standalone_image)
    print("got image");
    standalone_container = client.containers.run(
        standalone_image,
        detach=True,
        ports={"8080/tcp": 8080},  # expose local port 8080 to container
        volumes=rw_volume_mounts | ro_volume_mounts,
        # command="while true; do echo \"Container is running...\"; sleep 5; done"
        command="airflow standalone"
    )
    time.sleep(4)
    standalone_container.exec_run(
        "airflow initdb", detach=True
    )  # docker execute command to initialize the airflow db
    time.sleep(40)
    standalone_container.exec_run(
        "airflow scheduler", detach=True
    )  # docker execute command to start airflow scheduler


    return standalone_container


airflow_container_tag = "apache/airflow:slim-3.0.3-python3.12";
validate_dag_folder = pathlib.Path.cwd() 
wip_folder_in_container = "/opt/testdags";
airflow_container = run_airflow(airflow_container_tag, { validate_dag_folder: wip_folder_in_container})

print(f"name: {airflow_container.name} status: {airflow_container.status}");
time.sleep(40);
import_result = airflow_container.exec_run(f"pytest {wip_folder_in_container}/automated-test/import-dagbag.py")
exit_code = import_result[0];
print(f"validation exit status: {exit_code}");

airflow_container.stop()

if(exit_code != 0):
    airflow_container
