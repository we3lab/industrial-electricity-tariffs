"""Energy coverage regression tests for scripts.validate (upstream schema)."""

import pandas as pd
import pytest
from scripts.validate import check_continuity, validate_tariff


def schedule_rows():
    # Seasonal schedule: summer all hours; winter weekday night/day/evening
    # windows plus weekday 6 all day. Rates are placeholder test values.
    rows = [(4, 10, 0, 6, 0, 24)]
    for m1, m2 in [(1, 3), (11, 12)]:
        rows.extend(
            [
                (m1, m2, 0, 5, 0, 7),
                (m1, m2, 0, 5, 7, 22),
                (m1, m2, 0, 5, 22, 24),
                (m1, m2, 6, 6, 0, 24),
            ]
        )
    return pd.DataFrame(
        rows,
        columns=[
            "month_start",
            "month_end",
            "weekday_start",
            "weekday_end",
            "hour_start",
            "hour_end",
        ],
    )


def tariff_df(schedule):
    return schedule.assign(
        utility="electric",
        type="energy",
        units="$/kWh",
        **{
            "charge (imperial)": 0.01,
            "charge (metric)": 0.01,
            "basic_charge_limit (imperial)": 0,
            "basic_charge_limit (metric)": 0,
        }
    )


def oracle(df):
    """Independent enumeration of all calendar slots for integer-hour cases."""
    rows = list(df.itertuples(index=False, name=None))
    return all(
        any(
            ms <= m <= me and ds <= d <= de and hs <= h < he
            for ms, me, ds, de, hs, he in rows
        )
        for m in range(1, 13)
        for d in range(7)
        for h in range(24)
    )


def test_complete_seasonal_schedule():
    df = schedule_rows()
    assert oracle(df)
    assert check_continuity(df, "energy")
    assert validate_tariff(tariff_df(df), "complete-seasonal")[0]


@pytest.mark.parametrize("row", range(9))
def test_removing_any_window_rejects_gap(row):
    df = schedule_rows().drop(index=row)
    assert not oracle(df)
    assert not check_continuity(df, "energy")
    ok, message = validate_tariff(tariff_df(df), "missing-window")
    assert not ok
    assert "does not cover" in message


@pytest.mark.parametrize("boundary", ["month_end", "weekday_end", "hour_end"])
def test_boundary_gap(boundary):
    df = pd.DataFrame([(1, 12, 0, 6, 0, 24)], columns=schedule_rows().columns)
    df.loc[0, boundary] -= 1
    assert not oracle(df)
    assert not check_continuity(df, "energy")


def test_endpoints_are_half_open_and_unsorted_rows_are_supported():
    df = pd.DataFrame(
        [(1, 12, 0, 6, 12, 24), (1, 12, 0, 6, 0, 7), (1, 12, 0, 6, 7, 12)],
        columns=schedule_rows().columns,
    )
    assert check_continuity(df, "energy")
    df.loc[1, "hour_end"] = 6
    assert not check_continuity(df, "energy")


def test_fractional_hour_gap():
    df = pd.DataFrame(
        [(1, 12, 0, 6, 0.0, 7.5), (1, 12, 0, 6, 7.75, 24.0)],
        columns=schedule_rows().columns,
    )
    assert not check_continuity(df, "energy")
    df.loc[1, "hour_start"] = 7.5
    assert check_continuity(df, "energy")


def test_empty_energy_and_overlapping_coverage():
    df = schedule_rows()
    assert not check_continuity(df.iloc[:0], "energy")
    assert check_continuity(pd.concat([df, df]), "energy")


@pytest.mark.parametrize("charge_type", ["customer", "demand"])
def test_partial_non_energy_schedules_remain_supported(charge_type):
    # Demand charges may apply only on peak hours; customer charges have no windows.
    assert check_continuity(pd.DataFrame(), "customer")
    assert check_continuity(schedule_rows().iloc[:1], charge_type)


def test_small_integer_schedule_property():
    # Remove each hour from a full-year schedule: no integer calendar cell can
    # escape the coverage check. Also exercise each weekday/month separately.
    for end in range(24):
        rows = []
        if end:
            rows.append((1, 12, 0, 6, 0, end))
        if end < 23:
            rows.append((1, 12, 0, 6, end + 1, 24))
        df = pd.DataFrame(rows, columns=schedule_rows().columns)
        assert check_continuity(df, "energy") == oracle(df) == False
    for month in range(1, 13):
        df = pd.DataFrame(
            [(m, m, 0, 6, 0, 24) for m in range(1, 13) if m != month],
            columns=schedule_rows().columns,
        )
        assert check_continuity(df, "energy") == oracle(df) == False
    for day in range(7):
        df = pd.DataFrame(
            [(1, 12, d, d, 0, 24) for d in range(7) if d != day],
            columns=schedule_rows().columns,
        )
        assert check_continuity(df, "energy") == oracle(df) == False
