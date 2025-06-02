import os
import gzip
import shutil
from urllib.request import urlretrieve

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# This file is too large to be included on GitHub but can be found at 
# https://openei.org/wiki/Utility_Rate_Database
url = "https://openei.org/apps/USURDB/download/usurdb.csv.gz"
filename = os.path.join("data", "raw", "usurdb_raw.csv.gz")
outpath = os.path.join("data", "raw", "usurdb_raw.csv")
urlretrieve(url, filename)

# From XX
with gzip.open(filename, 'rb') as f_in:
    with open(outpath, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

# TODO: What is the original source of merged_zipcodes.csv ?
# for now I just archived the CSV from the other repo
# https://data.openei.org/files/5650/iou_zipcodes_2020.csv
# https://data.openei.org/files/5650/non_iou_zipcodes_2020.csv