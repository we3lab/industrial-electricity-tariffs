import os
import pytest
import datetime
import subprocess
import pandas as pd
from scripts.filter import *

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_folder_path = os.path.join("data", "filtered")
skip_all_tests = False

# ensure that data/raw/usurdb_raw.csv exists
if not os.path.exists("data/raw/usurdb_raw.csv"):
    command = ["python", "scripts/download.py"]
    subprocess.run(command, check=True)


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "allowed_sectors, allowed_service_types, outpath, date_cutoff",
    [
        (
            ["Industrial", "Commercial"],
            ["Bundled", "Delivery with Standard Offer"],
            os.path.join("data", "filtered", "usurdb_bundled.csv"),
            datetime.datetime(2023, 1, 1),
        ),
        (
            ["Industrial", "Commercial"],
            ["Delivery"],
            os.path.join("data", "filtered", "usurdb_delivery.csv"),
            datetime.datetime(2023, 1, 1),
        ),
        (
            ["Residential"],
            ["Bundled"],
            os.path.join("data", "filtered", "usurdb_bundled.csv"),
            datetime.datetime(2023, 1, 1),
        ),
        (
            ["Residential"],
            ["Bundled"],
            os.path.join("data", "filtered", "usurdb_residential.csv"),
            datetime.datetime.today(),
        ),
    ],
)
def test_filter_tariffs(allowed_sectors, allowed_service_types, outpath, date_cutoff):
    filter_tariffs(allowed_sectors, allowed_service_types, outpath, date_cutoff)

    # check that file was saved in outpath
    result = pd.read_csv(outpath)
    result["startdate"] = pd.to_datetime(result["startdate"], errors="coerce")
    result["enddate"] = pd.to_datetime(result["enddate"], errors="coerce")

    # check that only allowed_sectors are included
    assert result["sector"].isin(allowed_sectors).all()

    # check that only allowed_service_types are included
    assert result["servicetype"].isin(allowed_service_types).all()

    # check that results all have start dates before cutoff date and expiration dates after
    assert ((result["startdate"] <= date_cutoff) | (result["startdate"].isna())).all()
    assert ((result["enddate"] >= date_cutoff) | (result["enddate"].isna())).all()


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
def test_main():
    # run the main script
    main()

    # check that `merged_zipcodes.csv` is created
    assert os.path.exists(os.path.join(data_folder_path, "merged_zipcodes.csv"))
