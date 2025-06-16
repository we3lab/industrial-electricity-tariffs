import os
import datetime
import pandas as pd

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def filter_tariffs(
    allowed_service_types=["Bundled", "Delivery with Standard Offer"], 
    outpath="data/filtered/usurdb_filtered.csv",
    date_cutoff=datetime.datetime.today()
):
    raw_tariff_list = pd.read_csv("data/raw/usurdb_raw.csv", )
    num_tariffs = len(raw_tariff_list)
    print(f"Number of tariffs before filtering: {num_tariffs}")

    # filter by sector
    df = raw_tariff_list[raw_tariff_list['sector'].isin(['Industrial', 'Commercial'])]
    num_tariffs = len(df)
    print(f"Number of tariffs after filtering by sector (Industrial, Commercial): {num_tariffs}")

    # filter by service type
    df = df[df['servicetype'].isin(allowed_service_types)]
    num_tariffs = len(df)
    print(f"Number of tariffs after filtering by service type {allowed_service_types}: {num_tariffs}")

    # filter by peakkwcapacitymin
    df = df[(df['peakkwcapacitymin'] <= 1000) | (df['peakkwcapacitymin'].isna())]
    df = df[(df['peakkwcapacitymax'] >= 1000) | (df['peakkwcapacitymax'].isna())]
    num_tariffs = len(df)
    print(f"Number of tariffs after filtering by capacity (1000 kW): {num_tariffs}")

    # filter by startdate and enddate
    df["startdate"] = pd.to_datetime(df["startdate"], errors="coerce")
    df["enddate"] = pd.to_datetime(df["enddate"], errors="coerce")
    df = df[(df['startdate'] <= date_cutoff) | (df['startdate'].isna())]
    df = df[(df['enddate'] >= date_cutoff) | (df['enddate'].isna())]
    num_tariffs = len(df)
    print(f"Number of tariffs after filtering by start and end date: {num_tariffs}")

    # save filtered data to csv
    df.to_csv(outpath, index=False)


def main():
    iou_filename = os.path.join("data", "raw", "iou_zipcodes_2020.csv")
    non_iou_filename = os.path.join("data", "raw", "non_iou_zipcodes_2020.csv")
    iou_zips = pd.read_csv(iou_filename)
    non_iou_zips = pd.read_csv(non_iou_filename)
    merged_outpath = os.path.join("data", "filtered", "merged_zipcodes.csv")
    pd.concat([iou_zips, non_iou_zips]).to_csv(merged_outpath, index=False)
    filter_tariffs(
        allowed_service_types=["Bundled", "Delivery with Standard Offer"],
        outpath="data/filtered/usurdb_bundled.csv",
        # date_cutoff=datetime.datetime(2023, 6, 1)
    )
    filter_tariffs(
        allowed_service_types=["Delivery"],
        outpath="data/filtered/usurdb_delivery_only.csv",
        # date_cutoff=datetime.datetime(2023, 6, 1)
    )


if __name__ == "__main__":
    main()