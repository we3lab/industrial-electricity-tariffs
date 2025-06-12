import os
import shutil
import warnings
import pandas as pd

# change to repo parent directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# define maximum charge dictionary
MAX_CHARGES = {
    "electric_demand": 100, 
    "electric_energy": 2,
    "electric_customer": 5000,
    "gas_energy": 3,
    "gas_demand": 40, 
    "gas_customer": 5000,
}

def check_continuity(df, charge_type):
    if charge_type == "customer" or "demand":
        return True

    month_start = 1
    day_start = 0
    hour_start = 0

    while month_start < 13:
        row = df[(df["month_start"] <= month_start) & (df["month_end"] >= month_start)
                 & (df["weekday_start"] <= day_start) & (df["month_end"] >= day_start)
                 & (df["hour_start"] <= hour_start) & (df["hour_end"] >= hour_start)]
        if len(df.columns) == 0:
            return False

        hour_start = row[0, "hour_end"]

        if hour_start == 24:
            hour_start = 0
            day_start += 1

        if day_start == 7:
            day_start = 0
            month_start += 1

    return True


def validate_tariff(tariff_df, tariff_id, max_charges=MAX_CHARGES):
    try:
        utilities = tariff_df["utility"].unique()
        for utility in utilities:
            for charge_type in tariff_df.loc[tariff_df["utility"] == utility]["type"].unique():
                # Check that all days of a year are included
                slice = tariff_df.loc[(tariff_df["utility"] == utility) & (tariff_df["type"] == charge_type)]
                assert check_continuity(slice, charge_type)

                # Check prices are positive and below a threshold
                assert slice["charge (imperial)"].min() >= 0
                assert slice["charge (metric)"].min() >= 0
                assert slice["charge (imperial)"].max() <= max_charges[utility + "_" + charge_type]
                if utility == "gas":
                    assert slice["charge (metric)"].max() <= max_charges[utility + "_" + charge_type] / 2.83168
                elif utility == "electric":
                    assert slice["charge (metric)"].max() <= max_charges[utility + "_" + charge_type] 
                else:
                    raise ValueError("utility must be 'gas' or 'electric'")
        # Check units (i.e. demand is in kW and energy in kWh)
        assert (tariff_df.loc[tariff_df["type"] == "customer"]["units"] == "$/month").all()
        assert (tariff_df.loc[(tariff_df["type"] == "demand") & (tariff_df["utility"] == "electric")]["units"] == "$/kW").all()
        assert (tariff_df.loc[(tariff_df["type"] == "energy") & (tariff_df["utility"] == "electric")]["units"] == "$/kWh").all()
        assert (tariff_df.loc[(tariff_df["utility"] == "gas") & (tariff_df["type"] == "energy")]["units"] == "$/therm or $/m3").all()
        assert (tariff_df.loc[(tariff_df["utility"] == "gas") & (tariff_df["type"] == "demand")]["units"] == "$/therm/hr or $/m3/hr").all()
        
        # Check that month_start <= month_end, weekday_start <= weekday_end, and hour_start < hour_end
        assert (tariff_df.loc[tariff_df["type"] != "customer"]["month_start"] <= tariff_df.loc[tariff_df["type"] != "customer"]["month_end"]).all() 
        assert (tariff_df.loc[tariff_df["type"] != "customer"]["weekday_start"] <= tariff_df.loc[tariff_df["type"] != "customer"]["weekday_end"]).all() 
        assert (tariff_df.loc[tariff_df["type"] != "customer"]["hour_start"] < tariff_df.loc[tariff_df["type"] != "customer"]["hour_end"]).all() 

        # Check that conversion between metric and imperial units is correct
        assert (tariff_df.loc[tariff_df["utility"] == "electric"]["charge (imperial)"] 
            == tariff_df.loc[tariff_df["utility"] == "electric"]["charge (metric)"]
        ).all()
        assert (tariff_df.loc[(tariff_df["utility"] == "gas") & (tariff_df["type"] != "customer")]["charge (imperial)"] / 2.83168
            ==  tariff_df.loc[(tariff_df["utility"] == "gas") & (tariff_df["type"] != "customer")]["charge (metric)"] 
        ).all()
        assert (tariff_df.loc[(tariff_df["utility"] == "gas") & (tariff_df["type"] == "customer")]["charge (imperial)"] 
            == tariff_df.loc[(tariff_df["utility"] == "gas") & (tariff_df["type"] == "customer")]["charge (metric)"]
        ).all()
        assert (tariff_df.loc[(tariff_df["utility"] == "electric") & (tariff_df["type"] != "customer")]["basic_charge_limit (imperial)"] 
            == tariff_df.loc[(tariff_df["utility"] == "electric") & (tariff_df["type"] != "customer")]["basic_charge_limit (metric)"]
        ).all()
        assert (tariff_df.loc[(tariff_df["utility"] == "gas") & (tariff_df["type"] != "customer")]["basic_charge_limit (imperial)"] * 2.83168
            == tariff_df.loc[(tariff_df["utility"] == "gas") & (tariff_df["type"] != "customer")]["basic_charge_limit (metric)"]
        ).all() 
    except Exception as e:
        print(f"Error with {tariff_id}:", e)
        return False

    return True

def validate_tariffs(savefolder="data/validated/", sourcefolder="data/converted/", suffix=""):
    valid_tariffs = []
    reject_tariffs = []
    for tariff_id in tariff_ids:
        sourcepath = sourcefolder + tariff_id + ".csv"
        tariff_df = pd.read_csv(sourcepath)
        # copy valid_tariffs to data/validated folder with suffix
        if validate_tariff(tariff_df, tariff_id):
            outpath = savefolder + tariff_id + ".csv"
            shutil.copyfile(sourcepath, outpath)
        else:
            rejected_tariffs.append(tariff_id)

    # save reject_tariffs list in data/validated folder with suffix
    pd.DataFrame({"tariff_id": reject_tariffs}).to_csv("data/validated/rejected" + suffix + ".csv", index=False)


if __name__ == "__main__":
    validate_tariffs(
        savefolder="data/validated/bundled/", 
        sourcefolder="data/converted/bundled/",
        suffix="_bundled"
    )
    validate_tariffs(
        savefolder="data/validated/delivery_only/",
        sourcefolder="data/converted/delivery_only/",
        suffix="_delivery_only"
    )