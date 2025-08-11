import os
from pathlib import Path
from airflow.models.dagbag import DagBag

dagBagDir = Path("/opt/testdags/empty")
def test_dir_exists():
    if(not dagBagDir.exists()):
        raise Exception(f"dag bag dir does not exist: {dagBagDir}")
    if(not dagBagDir.is_dir()):
        raise Exception(f"dag bag path is not a directory: {dagBagDir}")
    if(not os.listdir(dagBagDir)):
        raise Exception(f"dag bag dir is empty: {dagBagDir}")
def test_import_dags():
    """
    Pytest to ensure there will be no import errors in dagbag. These are generally syntax problems.
    """
    dags = DagBag(dag_folder=dagBagDir)
    
    assert len(dags.import_errors) == 0

    # for dag_id, dag in dags.dags.items():
test_import_dags();