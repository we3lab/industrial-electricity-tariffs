import os
import gzip
import shutil
import pandas as pd
from urllib.request import urlretrieve

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    # This file is too large to be included on GitHub but can be found at
    # https://openei.org/wiki/Utility_Rate_Database
    url = "https://openei.org/apps/USURDB/download/usurdb.csv.gz"
    filename = os.path.join("data", "raw", "usurdb_raw.csv.gz")
    outpath = os.path.join("data", "raw", "usurdb_raw.csv")
    urlretrieve(url, filename)

    # From https://stackoverflow.com/questions/31028815/how-to-unzip-gz-file-using-python
    with gzip.open(filename, "rb") as f_in:
        with open(outpath, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    iou_url = "https://data.openei.org/files/5650/iou_zipcodes_2020.csv"
    iou_filename = os.path.join("data", "raw", "iou_zipcodes_2020.csv")
    urlretrieve(iou_url, iou_filename)

    non_iou_url = "https://data.openei.org/files/5650/non_iou_zipcodes_2020.csv"
    non_iou_filename = os.path.join("data", "raw", "non_iou_zipcodes_2020.csv")
    urlretrieve(non_iou_url, non_iou_filename)

    # Incorporate tariffs from https://github.com/we3lab/wwtp-energy-tariffs
    xls_url = "https://raw.githubusercontent.com/we3lab/wwtp-energy-tariffs/main/data/WWTP_Billing.xlsx"
    xls_filename = os.path.join("data", "raw", "WWTP_Billing.xlsx")
    urlretrieve(xls_url, xls_filename)
    metadata_url = "https://raw.githubusercontent.com/we3lab/wwtp-energy-tariffs/main/data/metadata.csv"
    metadata_filename = os.path.join("data", "raw", "metadata.csv")
    urlretrieve(metadata_url, metadata_filename)


if __name__ == "__main__": 
    main()