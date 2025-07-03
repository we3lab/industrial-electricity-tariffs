import os
import pytest
import subprocess

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_folder_path = os.path.join("data", "raw")
skip_all_tests = False


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
def test_download():
    # check that the script runs without error
    command = ["python", "scripts/download.py"]
    subprocess.run(command, check=True)

    # check the following files are downloaded without error:
    # (1) usurdb_raw.csv.gz
    # (2) iou_zipcodes_2020.csv
    # (3) non_iou_zipcodes_2020.csv
    # (4) WWTP_Billing.xlsx
    # (5) metadata.csv
    assert os.path.exists(os.path.join(data_folder_path, "usurdb_raw.csv.gz"))
    assert os.path.exists(os.path.join(data_folder_path, "iou_zipcodes_2020.csv"))
    assert os.path.exists(os.path.join(data_folder_path, "non_iou_zipcodes_2020.csv"))
    assert os.path.exists(os.path.join(data_folder_path, "WWTP_Billing.xlsx"))
    assert os.path.exists(os.path.join(data_folder_path, "metadata.csv"))

    # check that the file was unzipped properly
    assert os.path.exists(os.path.join(data_folder_path, "usurdb_raw.csv"))