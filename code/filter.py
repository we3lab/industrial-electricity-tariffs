import os
import pandas as pd

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def filter_tariffs(
    allowed_service_types=["Bundled", "Delivery with Standard Offer"], 
    outpath="data/filtered/usurdb_filtered.csv"
):
    raw_tariff_list = pd.read_csv("data/raw/usurdb_raw.csv")
    num_tariffs = len(raw_tariff_list)
    print(f"Number of tariffs to start: {num_tariffs}")

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

    # save filtered data to csv
    df.to_csv(outpath, index=False)


def main():
    filter_tariffs(
        allowed_service_types=["Bundled", "Delivery with Standard Offer"],
        outpath="data/filtered/usurdb_bundled.csv"
    )
    filter_tariffs(
        allowed_service_types=["Delivery"],
        outpath="data/filtered/usurdb_delivery_only.csv"
    )


if __name__ == "__main__":
    main()