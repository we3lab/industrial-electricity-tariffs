import os
import shutil
import pandas as pd

# change to repo parent directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# define maximum charge dictionary
MAX_CHARGES = {
    "electric_demand": 100,
    "electric_energy": 2,
    "electric_customer": 15000,
    "gas_energy": 3,
    "gas_demand": 40,
    "gas_customer": 15000,
}


def check_continuity(df, charge_type):
    # Customer charges have no time windows; demand charges may deliberately
    # apply only during a subset of the year. Energy must cover the whole year.
    if charge_type in ("customer", "demand"):
        return True

    # Extract once; avoid constructing 84 intermediate DataFrames per tariff.
    windows = list(
        df[
            ["month_start", "month_end", "weekday_start", "weekday_end", "hour_start", "hour_end"]
        ].itertuples(index=False, name=None)
    )
    for month in range(1, 13):
        for weekday in range(7):
            hours = sorted(
                (hour_start, hour_end)
                for month_start, month_end, weekday_start, weekday_end, hour_start, hour_end in windows
                if month_start <= month <= month_end
                and weekday_start <= weekday <= weekday_end
            )

            # Merge hour intervals rather than walking dataframe positions.
            # Endpoints are half-open: [hour_start, hour_end).
            covered_to = 0
            for hour_start, hour_end in hours:
                if hour_start > covered_to:
                    return False
                covered_to = max(covered_to, hour_end)
                if covered_to >= 24:
                    break
            if covered_to < 24:
                return False

    return True


def validate_tariff(tariff_df, tariff_id, max_charges=MAX_CHARGES):
    try:
        utilities = tariff_df["utility"].unique()
        for utility in utilities:
            for charge_type in tariff_df.loc[tariff_df["utility"] == utility][
                "type"
            ].unique():
                # Check that all days of a year are included
                slice = tariff_df.loc[
                    (tariff_df["utility"] == utility)
                    & (tariff_df["type"] == charge_type)
                ]
                try:
                    assert check_continuity(slice, charge_type)
                except AssertionError:
                    raise ValueError("Tariff does not cover all hours/days of the year.")

                # Check prices are positive and below a threshold
                try:
                    assert slice["charge (imperial)"].min() >= 0
                    assert slice["charge (metric)"].min() >= 0
                except AssertionError:
                    raise ValueError(f"{charge_type} charge for tariff is negative")
                try:
                    assert (
                        slice["charge (imperial)"].max()
                        <= max_charges[utility + "_" + charge_type]
                    )
                    if utility == "gas":
                        assert (
                            slice["charge (metric)"].max()
                            <= max_charges[utility + "_" + charge_type] / 2.83168
                        )
                    elif utility == "electric":
                        assert (
                            slice["charge (metric)"].max()
                            <= max_charges[utility + "_" + charge_type]
                        )
                    else:
                        raise ValueError("utility must be 'gas' or 'electric'")
                except AssertionError:
                    raise ValueError(
                        f"{charge_type} charge of ${slice['charge (metric)'].max()} for tariff is above"
                        f" the expected max of ${max_charges[utility + '_' + charge_type]}"
                    )
        # Check units (i.e. demand is in kW and energy in kWh)
        try:
            assert (
                tariff_df.loc[tariff_df["type"] == "customer"]["units"] == "$/month"
            ).all()
            assert (
                tariff_df.loc[
                    (tariff_df["type"] == "demand")
                    & (tariff_df["utility"] == "electric")
                ]["units"]
                == "$/kW"
            ).all()
            assert (
                tariff_df.loc[
                    (tariff_df["type"] == "energy")
                    & (tariff_df["utility"] == "electric")
                ]["units"]
                == "$/kWh"
            ).all()
            assert (
                tariff_df.loc[
                    (tariff_df["utility"] == "gas") & (tariff_df["type"] == "energy")
                ]["units"]
                == "$/therm or $/m3"
            ).all()
            assert (
                tariff_df.loc[
                    (tariff_df["utility"] == "gas") & (tariff_df["type"] == "demand")
                ]["units"]
                == "$/therm/hr or $/m3/hr"
            ).all()
        except AssertionError:
            raise ValueError(
                "Incorrect units (demand charges should be $/kW and energy charges should be $/kWh)"
            )

        # Check that month_start <= month_end, weekday_start <= weekday_end, and hour_start < hour_end
        try:
            assert (
                tariff_df.loc[tariff_df["type"] != "customer"]["month_start"]
                <= tariff_df.loc[tariff_df["type"] != "customer"]["month_end"]
            ).all()
            assert (
                tariff_df.loc[tariff_df["type"] != "customer"]["weekday_start"]
                <= tariff_df.loc[tariff_df["type"] != "customer"]["weekday_end"]
            ).all()
            assert (
                tariff_df.loc[tariff_df["type"] != "customer"]["hour_start"]
                < tariff_df.loc[tariff_df["type"] != "customer"]["hour_end"]
            ).all()
        except AssertionError:
            raise ValueError(
                "Period start (e.g., `weekday_start`) occurs after period end (e.g., `weekday_end`)"
            )

        # Check that conversion between metric and imperial units is correct
        try:
            assert (
                tariff_df.loc[tariff_df["utility"] == "electric"]["charge (imperial)"]
                == tariff_df.loc[tariff_df["utility"] == "electric"]["charge (metric)"]
            ).all()
            assert (
                tariff_df.loc[
                    (tariff_df["utility"] == "gas") & (tariff_df["type"] != "customer")
                ]["charge (imperial)"]
                / 2.83168
                == tariff_df.loc[
                    (tariff_df["utility"] == "gas") & (tariff_df["type"] != "customer")
                ]["charge (metric)"]
            ).all()
            assert (
                tariff_df.loc[
                    (tariff_df["utility"] == "gas") & (tariff_df["type"] == "customer")
                ]["charge (imperial)"]
                == tariff_df.loc[
                    (tariff_df["utility"] == "gas") & (tariff_df["type"] == "customer")
                ]["charge (metric)"]
            ).all()
            assert (
                tariff_df.loc[
                    (tariff_df["utility"] == "electric")
                    & (tariff_df["type"] != "customer")
                ]["basic_charge_limit (imperial)"]
                == tariff_df.loc[
                    (tariff_df["utility"] == "electric")
                    & (tariff_df["type"] != "customer")
                ]["basic_charge_limit (metric)"]
            ).all()
            assert (
                tariff_df.loc[
                    (tariff_df["utility"] == "gas") & (tariff_df["type"] != "customer")
                ]["basic_charge_limit (imperial)"]
                * 2.83168
                == tariff_df.loc[
                    (tariff_df["utility"] == "gas") & (tariff_df["type"] != "customer")
                ]["basic_charge_limit (metric)"]
            ).all()
        except AssertionError:
            raise ValueError("Unit conversion error between imperial and metric")
    except Exception as e:
        error_str = f"Error with {tariff_id}: {e}"
        print(error_str)
        return False, error_str

    return True, "Success!"


def validate_tariffs(
    savefolder="data/validated/bundled/", datafolder="data/merged/bundled/", suffix=""
):
    reject_tariffs = []
    reject_messages = []
    metadatapath = (
        os.path.dirname(os.path.dirname(datafolder)) + "/metadata" + suffix + ".csv"
    )
    metadata_df = pd.read_csv(metadatapath)
    metadata_df.set_index("label", inplace=True)

    if not os.path.exists(savefolder):
        os.mkdir(savefolder)

    print(
        f"Number of tariffs after conversion, but before validation: {len(metadata_df)}"
    )

    for tariff_id in metadata_df.index:
        sourcepath = datafolder + tariff_id + ".csv"
        tariff_df = pd.read_csv(sourcepath)
        validation_result = validate_tariff(tariff_df, tariff_id)
        # copy valid_tariffs to data/validated folder with suffix
        if validation_result[0]:
            outpath = os.path.join(savefolder, tariff_id + ".csv")
            shutil.copyfile(sourcepath, outpath)
        else:
            # remove from metadata_df
            metadata_df = metadata_df.drop(tariff_id)
            # add to reject list
            reject_tariffs.append(tariff_id)
            reject_messages.append(validation_result[1])

    print(
        f"Number of tariffs after validation: {len(metadata_df) - len(reject_tariffs)}"
    )

    # save reject_tariffs list in data/validated folder with suffix
    pd.DataFrame({"tariff_id": reject_tariffs, "reason": reject_messages}).to_csv(
        "data/validated/rejected" + suffix + ".csv", index=False
    )

    # save metadata to data/validated folder
    metadata_df.to_csv("data/validated/metadata" + suffix + ".csv", index=True)


if __name__ == "__main__":
    validate_tariffs(
        savefolder="data/validated/bundled/",
        datafolder="data/merged/bundled/",
        suffix="_bundled",
    )
    validate_tariffs(
        savefolder="data/validated/delivery_only/",
        datafolder="data/converted/delivery_only/",
        suffix="_delivery_only",
    )
