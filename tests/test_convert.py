import os
import math
import pytest
from code.convert import *

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
skip_all_tests = False


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
def test_make_dict():
    expected = {
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
    result = make_dict()
    assert result == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "lst, expected",
    [
        (
            [   
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            ],
            [(0, 11)]
        ),
        (
            [math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan, math.nan],
            [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11)]
        ),
        (
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [(0, 7), (8, 19), (20, 23)]
        )
    ],
)
def test_find_consecutive_ranges(lst, expected):
    result = find_consecutive_ranges(lst)
    assert result == expected


@pytest.mark.skipif(skip_all_tests, reason="Exclude all tests")
@pytest.mark.parametrize(
    "charge, unit, charge_dict, expected",
    [
        (
            13.709999999999999,
            "kW",
            {
                'label': '539fc321ec4f024c27d8b8e5', 
                'utility': 'electric', 
                'type': 'demand', 
                'assessed': '', 
                'period': 'flat', 
                'basic_charge_limit (imperial)': 0, 
                'basic_charge_limit (metric)': 0, 
                'month_start': '1', 
                'month_end': '5', 
                'hour_start': '0', 
                'hour_end': '24', 
                'weekday_start': '0', 
                'weekday_end': '6', 
                'charge (imperial)': '', 
                'charge (metric)': '', 
                'units': '', 
                'Notes': 'adjustment factor of 3.68'
            },
            {
                'label': '539fc321ec4f024c27d8b8e5', 
                'utility': 'electric',
                'type': 'demand', 
                'assessed': '', 
                'period': 'flat', 
                'basic_charge_limit (imperial)': 0,
                'basic_charge_limit (metric)': 0,
                'month_start': '1', 
                'month_end': '5', 
                'hour_start': '0', 
                'hour_end': '24', 
                'weekday_start': '0', 
                'weekday_end': '6', 
                'charge (imperial)': 13.709999999999999, 
                'charge (metric)': 13.709999999999999, 
                'units': '$/kW', 
                'Notes': 'adjustment factor of 3.68'
            }
        )
    ],
)
def test_process_demand_unit(charge, unit, charge_dict, expected):
    result = process_demand_unit(charge, unit, charge_dict)
    assert result == expected

# (4) test_process_customer
    # (a)
    # (b)

# (5) test_process_flat_demand
    # (a)
    # (b)

# (6) test_unpack_array()

# (7) test_process_tou_demand

# (8) test_process_energy

# (9) test_sector_filter

# (10) test_generate_metadata

# (11) test_add_index

# (12) test_get_lat_long

# (13) test_main