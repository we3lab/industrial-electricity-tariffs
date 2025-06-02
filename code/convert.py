import os
import ast
import math
import numpy as np
import pandas as pd

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Source: DOI: 10.1109/ICRERA52334.2021.9598561
POWER_FACTOR = 0.95
HP_TO_KW_CONVERSION = 0.7457

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

state_abbr = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",   
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "MD",
}

def make_dict():
    """
    creates a dictionary for the tariff file

    Parameters
    ----------
    None

    Returns
    -------
    dictionary
        empty dictionary with all the keys needed for the tariff file
    """
    data_dict = {
        "label": "",
        "utility": "",
        "type": "",
        "assessed": "",
        "period": "",
        "basic_charge_limit (imperial)": "",
        "basic_charge_limit (metric)": "",
        "month_start": "",
        "month_end": "",
        "hour_start": "",
        "hour_end": "",
        "weekday_start": "",
        "weekday_end": "",
        "charge (imperial)": "",
        "charge (metric)": "",
        "units": "",
        "Notes": "",
    }
    return data_dict


def find_consecutive_ranges(lst):
    """
    Finds the consecutive ranges in a list of integers.

    Parameters
    ----------
    lst : list
        A list of integers.

    Returns
    -------
    list
        A list of tuples, where each tuple contains the start and end indices of a consecutive range.
    """
    if not lst:
        return []

    ranges = []
    start = 0

    for i in range(1, len(lst)):
        if lst[i] != lst[start]:
            ranges.append((start, i - 1))
            start = i

    ranges.append((start, len(lst) - 1))

    return ranges


def process_demand_unit(charge, unit, charge_dict):
    """
    Processes the demand unit for the tariff file

    Parameters
    ----------
    charge : float
        The demand charge in the given units.

    unit : str
        The demand unit for the tariff file.

    charge_dict : dict
        The dictionary for the tariff file.

    Returns
    -------
    dictionary
        The dictionary for the tariff file with the processed demand unit.
    """
    if isinstance(unit, float) and math.isnan(unit):
        charge_dict["units"] = "$/kW"
        charge_dict["charge (imperial)"] = charge
        charge_dict["charge (metric)"] = charge
        return charge_dict

    unit_arr = unit.split(" ")
    unit_name = unit_arr[0]

    if len(unit_arr) > 1:
        unit_daily = unit_arr[1]
        if unit_daily == "daily":
            charge_dict["Notes"] = "demand measured daily "
    if unit_name == "kW":
        charge_dict["units"] = "$/kW"
        charge_dict["charge (imperial)"] = charge
        charge_dict["charge (metric)"] = charge
    elif unit_name == "kVA":  # Converted from $/kVA to $/kW using PF=0.95
        charge_dict["units"] = "$/kW"
        charge_dict["charge (imperial)"] = charge / POWER_FACTOR
        charge_dict["charge (metric)"] = charge / POWER_FACTOR
    elif unit_name == "hp":  # Converted from $/hp to $/kW using factor of 0.7457
        charge_dict["units"] = "$/kW"
        charge_dict["charge (imperial)"] = charge * HP_TO_KW_CONVERSION
        charge_dict["charge (metric)"] = charge * HP_TO_KW_CONVERSION

    return charge_dict


def process_customer(openei_tariff_row):
    """
    Processes the customer monthly rate for the tariff file

    Parameters
    ----------
    openei_tariff_row : pandas.DataFrame
        A row of the original data from OpenEI's utility rate database.

    Returns
    -------
    list
        The list of dictionaries for the tariff file with the processed customer monthly rate.
    """
    data_dict = make_dict()
    data_dict["label"] = openei_tariff_row["label"]
    data_dict["utility"] = "electric"
    data_dict["type"] = "customer"
    data_dict["assessed"] = ""
    data_dict["period"] = ""
    data_dict["basic_charge_limit (imperial)"] = ""
    data_dict["basic_charge_limit (metric)"] = ""
    data_dict["month_start"] = ""
    data_dict["month_end"] = ""
    data_dict["hour_start"] = ""
    data_dict["hour_end"] = ""
    data_dict["weekday_start"] = ""
    data_dict["weekday_end"] = ""
    data_dict["charge (imperial)"] = openei_tariff_row["fixedchargefirstmeter"]
    data_dict["charge (metric)"] = openei_tariff_row["fixedchargefirstmeter"]
    data_dict["units"] = "$/month"
    data_dict["Notes"] = str(openei_tariff_row["source"]) + (
        "\t" + str(openei_tariff_row["sourceparent"]) if openei_tariff_row["sourceparent"] != "" else ""
    )
    return [data_dict]


def process_flat_demand(openei_tariff_row):
    """
    Processes the demand rate for the tariff file

    Parameters
    -------
    openei_tariff_row : pandas.DataFrame
        A row from the original data from OpenEI's utility rate database.

    Raises
    -------
    ValueError, KeyError
        If the demand rate is not found in the openei dataframe.

    Returns
    -------
    list
        The list of dictionaries for the tariff file with the processed demand rate.
    """

    # all the possible month arrays
    MONTH_ARRAY = [
        "flatDemandMonth_jan",
        "flatDemandMonth_feb",
        "flatDemandMonth_mar",
        "flatDemandMonth_apr",
        "flatDemandMonth_may",
        "flatDemandMonth_jun",
        "flatDemandMonth_jul",
        "flatDemandMonth_aug",
        "flatDemandMonth_sep",
        "flatDemandMonth_oct",
        "flatDemandMonth_nov",
        "flatDemandMonth_dec",
    ]
    # for each month, add the value from the raw data into sched
    sched = {}
    for j in range(len(MONTH_ARRAY)):
        sched[j] = openei_tariff_row[MONTH_ARRAY[j]]
    new_list = list(sched.values())
    ranges = find_consecutive_ranges(new_list)

    if len(ranges) == 0:
        ranges = [(1, 12)]

    time_index = 0
    tier_index = 0
    charge_limit = 0

    dict_list = []

    while time_index < len(ranges):
        try:
            # tier_str first to catch ValueErrors from null values in the dataframe
            tier_str = (
                "flatdemandstructure/period"
                + str(int(sched[ranges[time_index][0]]))
                + "/tier"
                + str(tier_index)
            )
            charge = openei_tariff_row[tier_str + "rate"]
        except (ValueError, KeyError):
            return []

        data_dict = make_dict()
        data_dict["label"] = openei_tariff_row["label"]
        # Add one to all month temporal data in order to convert 0-index months to 1-index
        data_dict["month_start"] = str(ranges[time_index][0] + 1)
        data_dict["month_end"] = str(ranges[time_index][1] + 1)
        data_dict["utility"] = "electric"
        data_dict["type"] = "demand"
        data_dict["assessed"] = ""
        data_dict["period"] = "flat"
        data_dict["basic_charge_limit (imperial)"] = charge_limit
        data_dict["basic_charge_limit (metric)"] = charge_limit
        data_dict["hour_start"] = "0"
        data_dict["hour_end"] = "24"
        data_dict["weekday_start"] = "0"
        data_dict["weekday_end"] = "6"
        if not np.isnan(openei_tariff_row[tier_str + "adj"]):
            charge += openei_tariff_row[tier_str + "adj"]
            data_dict["Notes"] += f'adjustment factor of {openei_tariff_row[tier_str + "adj"]}'
        else:
            data_dict["Notes"] += ""
        data_dict = process_demand_unit(charge, openei_tariff_row["flatdemandunit"], data_dict)

        dict_list.append(data_dict)

        max_str = (
            "flatdemandstructure/period"
            + str(int(sched[ranges[time_index][0]]))
            + "/tier"
            + str(tier_index)
            + "max"
        )
        if not np.isnan(openei_tariff_row[max_str]):
            charge_limit = openei_tariff_row[max_str]
            tier_index += 1
        else:
            time_index += 1
            tier_index = 0

    return dict_list


def unpack_array(
    lst, sched, string, units, tariff_type, week_start, week_end, openei_tariff_row
):
    """
    Produces tariff rates for rates where temporal data is stored in nested lists

    Parameters
    ----------
    lst : list
        The list of tuples, where each tuple contains the start and end indices of a consecutive range.
    sched : list
        The schedule for the tariff rate, a nested list with the indexing information for tariffs at different times.
    string : str
        A string used to construct the indexing into the dataframe based on the syntax of the OpenEI headers.
    units : str
        The units for the tariff rate.
    tariff_type : str
        The tariff_type of the tariff rate— either "demand" or "energy".
    week_start : int
        The numeric value for the start day of the week where the tariff is in effect.
    week_end : int
        The numeric value for the end day of the week where the tariff is in effect.
    tariff : list
        The list of dictionaries for the tariff file.
    openei : pandas.DataFrame
        The original data from OpenEI's utility rate database.

    Raises
    -------
    IndexError, ValueError, KeyError
        If the index is out of range or the key is not found in the openei dataframe.

    Returns
    -------
    list
        The list of dictionaries for the tariff file with the processed rate added.
    """
    day_index = 0
    hour_index = 0
    tier_index = 0
    charge_limit = 0

    hour_list = sched[lst[day_index][0]]  # month_lst is the current month looked at
    hour_ranges = find_consecutive_ranges(hour_list)  # processed month_lst
    hour = hour_ranges[hour_index][0]

    dict_list = []

    while day_index < len(lst) and hour_index < len(hour_ranges):

        data_dict = make_dict()
        try:
            # tier_str first to catch ValueErrors from null values in the dataframe
            tier_str = (
                string + "/period" + str(hour_list[hour]) + "/tier" + str(tier_index)
            )
            rate = openei_tariff_row[tier_str + "rate"]
        except (IndexError, ValueError, KeyError):
            return dict_list

        data_dict["label"] = openei_tariff_row["label"]
        # Add one to all month temporal data in order to convert 0-index months to 1-index
        data_dict["month_start"] = str(lst[day_index][0] + 1)
        data_dict["month_end"] = str(lst[day_index][1] + 1)
        data_dict["utility"] = "electric"
        data_dict["type"] = tariff_type
        data_dict["assessed"] = ""
        data_dict["period"] = "period" + str(hour_list[hour])
        data_dict["basic_charge_limit (imperial)"] = charge_limit
        data_dict["basic_charge_limit (metric)"] = charge_limit
        data_dict["hour_start"] = hour_ranges[hour_index][0]
        data_dict["hour_end"] = hour_ranges[hour_index][1] + 1
        # Not the case for all structures
        data_dict["weekday_start"] = week_start
        data_dict["weekday_end"] = week_end
        if not np.isnan(openei_tariff_row[tier_str + "adj"]):
            rate += openei_tariff_row[tier_str + "adj"]
        data_dict["charge (imperial)"] = float(rate)
        data_dict["charge (metric)"] = float(rate)

        data_dict["units"] = units
        data_dict["Notes"] = ""
        
        # append to list of dictionaries - each dict is a charge 
        dict_list.append(data_dict)

        max_str = (
            string
            + "/period"
            + str(hour_list[hour])
            + "/tier"
            + str(tier_index)
            + "max"
        )
        if not np.isnan(openei_tariff_row[max_str]):
            charge_limit = openei_tariff_row[max_str]
            tier_index += 1
        elif hour_index < len(hour_ranges) - 1:
            hour_index += 1
            charge_limit = 0
        else:
            day_index += 1
            hour_index = 0

        try:
            hour_list = sched[
                lst[day_index][0]
            ]  # month_lst is the current month looked at
            hour_ranges = find_consecutive_ranges(hour_list)  # processed month_lst
            hour = hour_ranges[hour_index][0]
        except IndexError:
            return dict_list

    return dict_list


def process_tou_demand(openei_tariff_row):
    """
    Processes TOU tariff rates for the tariff file

    Parameters
    ----------
    i : int
        The index of the row in the openei dataframe.
    tariff : list
        The list of dictionaries for the tariff file.
    openei : pandas.DataFrame
        The original data from OpenEI's utility rate database.

    Returns
    -------
    list
        The list of dictionaries for the tariff file with the processed TOU rates.
    """
    if pd.isna(openei_tariff_row["demandweekdayschedule"]) and pd.isna(
        openei_tariff_row["demandweekendschedule"]
    ):
        return []

    weekday_sched = ast.literal_eval(openei_tariff_row["demandweekdayschedule"])
    weekend_sched = ast.literal_eval(openei_tariff_row["demandweekendschedule"])

    weekday_ranges = find_consecutive_ranges(weekday_sched)
    weekend_ranges = find_consecutive_ranges(weekend_sched)

    dict_list_weekday = unpack_array(
        weekday_ranges,
        weekday_sched,
        "demandratestructure",
        "$/kW",
        "demand",
        0,
        4,
        openei_tariff_row,
    )

    dict_list_weekend = unpack_array(
        weekend_ranges,
        weekend_sched,
        "demandratestructure",
        "$/kW",
        "demand",
        5,
        6,
        openei_tariff_row,
    )
    dict_list_weekday.extend(dict_list_weekend)

    return dict_list_weekday


def process_energy(openei_tariff_row):
    """
    Processes energy structure tariff rates for the tariff file

    Parameters
    ----------
    i : int
        The index of the row in the openei dataframe.
    tariff : list
        The list of dictionaries for the tariff file.
    openei : pandas.DataFrame
        The original data from OpenEI's utility rate database.

    Returns
    -------
    list
        The list of dictionaries for the tariff file with the processed energy structure rates.
    """
    if pd.isna(openei_tariff_row["energyweekdayschedule"]) and pd.isna(
        openei_tariff_row["energyweekendschedule"]
    ):
        return []

    weekday_sched = ast.literal_eval(openei_tariff_row["energyweekdayschedule"])
    weekend_sched = ast.literal_eval(openei_tariff_row["energyweekendschedule"])

    weekday_ranges = find_consecutive_ranges(weekday_sched)
    weekend_ranges = find_consecutive_ranges(weekend_sched)

    dict_list_weekday = unpack_array(
        weekday_ranges,
        weekday_sched,
        "energyratestructure",
        "$/kWh",
        "energy",
        0,
        4,
        openei_tariff_row
    )
    dict_list_weekend = unpack_array(
        weekend_ranges,
        weekend_sched,
        "energyratestructure",
        "$/kWh",
        "energy",
        5,
        6,
        openei_tariff_row
    )

    dict_list_weekday.extend(dict_list_weekend)

    return dict_list_weekday


def sector_filter(acceptable_sectors, openei_tariff_row):
    """
    Filter the openei dataframe based on the desired sector

    Parameters
    ----------
    acceptable_sectors : str list
        The list of sectors to filter by.
    openei : pandas.DataFrame
        The original data from OpenEI's utility rate database.

    Returns
    -------
    bool
        True if the sector fits within the list of acceptable sectors.
    """
    if openei_tariff_row["sector"] in acceptable_sectors:
        return True
    return False

def generate_metadata(openei_tariff_row, eia_zipcode_database, state_abbr):
    """
    Generates a metadata dictionary for the tariff sheet/openei index
    Parameters
    ----------
    openei_tariff_row : pandas.DataFrame
        A row of the original data from OpenEI's utility rate database.
    eia_zipcode_database : pandas.DataFrame
        The dataframe of zipcodes mapping to EIA IDs.
    Returns
    -------
    metadata : dict
        A dictionary of metadata for the tariff sheet with the following keys:
        eiaid, name, label, utility, source, zipcode, state, city, county, notes
    """
    metadata = {}
    metadata['eiaid'] = str(int(openei_tariff_row["eiaid"]))

    for key in ["label", "name", "utility", "source"]:
        metadata[key] = openei_tariff_row[key]

    try:
        #subset the list of zipcodes that match the eiaid
        valid_zips = eia_zipcode_database[eia_zipcode_database["eiaid"] == openei_tariff_row["eiaid"]]
        # just take the first one - TODO: do something better/more sophisticated with more info
        zip_val = int(valid_zips["zip"].iloc[0])
        # check if the zip code is 5 digits otherwise add a leading 0
        if len(str(zip_val)) < 5:
            zip_val = "0" + str(zip_val)
        metadata["zipcode"] = zip_val
        metadata["state"] = valid_zips["state"].iloc[0] # likely all the states are the same 
    except:
        metadata["zipcode"] = np.nan
        metadata["state"] = np.nan
        for key, val in state_abbr.items():
            if key in str(openei_tariff_row["utility"]) or key in str(openei_tariff_row["source"]):
                metadata["state"] = val
                break
        
    metadata["notes"] = openei_tariff_row["description"]

    return metadata
    
def add_index(zipcodes, metadata_list, openei_tariff_row):
    """
    Add entire tariff sheet at index i to the tariff list and metadata list

    Parameters
    ----------
    zipcodes : pandas.DataFrame
        The dataframe of zipcodes mapping to EIA IDs.
    metadata_list : list
        The list of metadata dictionaries for the metadata file.
    openei : pandas.DataFrame
        The original data from OpenEI's utility rate database.

    Returns
    -------
    list
        The list of tariff sheets with a new list added for the index just added.
    """
    tariff = []

    tariff.extend(process_customer(openei_tariff_row))
    tariff.extend(process_flat_demand(openei_tariff_row))
    tariff.extend(process_tou_demand(openei_tariff_row))
    tariff.extend(process_energy(openei_tariff_row))
    return tariff


def main(savefolder="data/converted/", metadata_path="data/converted/metadata.csv"):
    os.chdir(os.path.dirname(os.path.dirname(__file__)))

    zipcodes_path = "data/filtered/merged_zipcodes.csv"
    zipcodes = pd.read_csv(zipcodes_path, low_memory=False)

    openei_path ="data/filtered/usurdb_filtered.csv"
    openei_df = pd.read_csv(openei_path, low_memory=False)
    openei_df["sourceparent"] = openei_df["sourceparent"].fillna("")

    if not os.path.exists(savefolder):
        os.mkdir(savefolder)
    
    metadata_list = []

    # for each row of openei_df - build the tariff sheet, find the metadata and produce a metadata row
    for i in range(len(openei_df)):
        openei_tariff_row = openei_df.iloc[i]
        # # check if the utility is in the top utilities list
        # if openei_tariff_row["utility"] not in top_utils["Name"].values:
        #     continue

        # add the index to indexes
        # tariff = add_index(zipcodes, metadata_list, openei_tariff_row)
        
        # process the tariff
        tariff = add_index([], [], openei_tariff_row)
        tariff_df = pd.DataFrame(tariff)
        label = tariff_df["label"][0]
        tariff_df.to_csv(savefolder + f"{label}.csv", index=False)

        # create a row for the metadata
        metadata_row = generate_metadata(openei_tariff_row, zipcodes, state_abbr)

        metadata_list.append(metadata_row)

        print(f"Saved {label} to {savefolder}")
    
    # save the metadata
    metadata_df = pd.DataFrame(metadata_list)
    # order the columns
    metadata_df = metadata_df[["label", "eiaid", "name", "utility", "source", "zipcode", "state","notes"]]
    metadata_df.to_csv(metadata_path, index=False)

if __name__ == "__main__":
    main(
        savefolder="data/converted/bundled/", 
        metadata_path="data/converted/metadata_bundled.csv"
    )
    main(
        savefolder="data/converted/delivery_only/", 
        metadata_path="data/converted/metadata_delivery_only.csv"
    )