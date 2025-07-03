import os
import glob
import shutil
import openpyxl
import pandas as pd

def lat_str_to_float(lat_str):
    return float(lat_str[:-1])


def long_str_to_float(long_str):
    long_str = "-" + long_str[:-1]
    return float(long_str)


def main(savefolder="data/merged", suffix=""):
    if not os.path.exists(savefolder):
        os.mkdir(savefolder)

    # copy wttp-energy-tariffs to merged folder
    metadata_df = pd.read_csv(os.path.join("data", "raw", "metadata.csv"))
    new_metadata = []
    for cwns_no in metadata_df["CWNS_No"]:
        row = metadata_df[metadata_df["CWNS_No"] == cwns_no].iloc[0]
        tariff_df = pd.read_excel(
            os.path.join("data", "raw", "WWTP_Billing.xlsx"), sheet_name=str(cwns_no)
        )
        tariff_df.to_csv(
            os.path.join(savefolder, f"{cwns_no}.csv"), index=False
        )
        new_entry = {
            "label": str(cwns_no),
            "state": row["State"],
            "utility": row["Electricity Utility"],
            "source": "https://github.com/we3lab/wwtp-energy-tariffs/",
            "latitude": lat_str_to_float(row["Latitude"]),
            "longitude": long_str_to_float(row["Longitude"]),
        }
        new_metadata.append(new_entry)

    # copy converted tariffs to merged folder
    tariff_files = glob.glob(os.path.join("data", "converted", suffix[1:], "*.csv"))
    for tariff_file in tariff_files:
        tariff_id = os.path.basename(tariff_file)
        shutil.copyfile(tariff_file, os.path.join(savefolder, tariff_id))

    # merge metadata
    old_metadata_df = pd.read_csv(os.path.join("data", "converted", "metadata" + suffix + ".csv"))
    new_metadata_df = pd.DataFrame(new_metadata)
    new_metadata_df = pd.concat([old_metadata_df, new_metadata_df])
    new_metadata_df.to_csv(
        os.path.join("data", "merged", "metadata" + suffix + ".csv"), index=False
    )

if __name__ == "__main__":
    main(savefolder=os.path.join("data", "merged", "bundled"), suffix="_bundled")
