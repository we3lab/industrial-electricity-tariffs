import os
import glob
import pytest
import subprocess
import pandas as pd

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_folder_path = os.path.join("data", "validated")
skip_all_tests = False

@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
def test_main():
    # run the pre-scripts if data does not exist
    if not os.path.exists(os.path.join("data", "raw", "usurdb_raw.csv")):
        command = ["python", "scripts/download.py"]
        subprocess.run(command, check=True)
    if not os.path.exists(os.path.join("data", "filtered", "usurdb_bundled.csv")):
        command = ["python", "scripts/filter.py"]
        subprocess.run(command, check=True)
    if not os.path.exists(os.path.join("data", "converted", "bundled")):
        command = ["python", "scripts/convert.py"]
        subprocess.run(command, check=True)
    if not os.path.exists(os.path.join("data", "merged", "bundled")):
        command = ["python", "scripts/merge.py"]
        subprocess.run(command, check=True)

    # check that the script runs without error
    command = ["python", "scripts/validate.py"]
    subprocess.run(command, check=True)

    ## bundled
    # check the metadata file exists and has the number of rows fewer = # rejected tariffs
    old_metadata = pd.read_csv(os.path.join("data", "merged", "metadata_bundled.csv"))
    valid_metadata = pd.read_csv(os.path.join(data_folder_path, "metadata_bundled.csv"))
    reject_list = pd.read_csv(os.path.join(data_folder_path, "rejected_bundled.csv"))
    assert len(valid_metadata) == len(old_metadata) - len(reject_list)
    old_tariffs = glob.glob(os.path.join("data", "merged", "bundled", "*.csv"))
    valid_tariffs = glob.glob(os.path.join("data", "validated", "bundled", "*.csv"))
    assert len(valid_tariffs) == len(old_tariffs) - len(reject_list)

    ## delivery only
    old_metadata = pd.read_csv(os.path.join("data", "converted", "metadata_delivery_only.csv"))
    valid_metadata = pd.read_csv(os.path.join(data_folder_path, "metadata_delivery_only.csv"))
    reject_list = pd.read_csv(os.path.join(data_folder_path, "rejected_delivery_only.csv"))
    assert len(valid_metadata) == len(old_metadata) - len(reject_list)
    # check the tariff sheets have been copied to the new folder
    old_tariffs = glob.glob(os.path.join("data", "converted", "delivery_only", "*.csv"))
    valid_tariffs = glob.glob(os.path.join("data", "validated", "delivery_only", "*.csv"))
    assert len(valid_tariffs) == len(old_tariffs) - len(reject_list)

# TODO: write unit tests for validate_tariffs(), validate_tariff(), and check_continuity()