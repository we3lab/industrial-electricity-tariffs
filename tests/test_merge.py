import os
import glob
import pytest
import subprocess
from scripts.merge import *

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_folder_path = os.path.join("data", "merged")
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

    # check that the script runs without error
    main(os.path.join("data", "merged", "bundled"), suffix="_bundled")

    # check the metadata file exists and has 100 additional rows
    old_metadata = pd.read_csv(os.path.join("data", "converted", "metadata_bundled.csv"))
    merged_metadata = pd.read_csv(os.path.join(data_folder_path, "metadata_bundled.csv"))
    assert len(merged_metadata) == len(old_metadata) + 100

    # check the tariff sheets have been copied to the 
    old_tariffs = glob.glob(os.path.join("data", "converted", "bundled", "*.csv"))
    merged_tariffs = glob.glob(os.path.join("data", "merged", "bundled", "*.csv"))
    assert len(merged_tariffs) == len(old_tariffs) + 100


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize("lat_str, expected", [("124.47N", 124.47)])
def test_lat_str_to_float(lat_str, expected):
    result = lat_str_to_float(lat_str)
    assert result == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize("long_str, expected", [("53.4W", -53.4),])
def test_long_str_to_float(long_str, expected):
    result = long_str_to_float(long_str)
    assert result == expected
