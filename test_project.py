from project import Energy_Prices
from project import analyze_data
from project import battery_calculations_gain
from project import battery_calculations_invest
import pytest

def test_energy_prices():
    energy = Energy_Prices("2026-08-24", "12:00", 100)

    assert energy.date == "2026-08-24"
    assert energy.time == "12:00"
    assert energy.price == 100

def test_analyze_data():
    prices = {
        "00:00": Energy_Prices("2026-08-24", "00:00", 100),
        "01:00": Energy_Prices("2026-08-24", "01:00", 50),
        "02:00": Energy_Prices("2026-08-24", "02:00", 80),
    }

    highest, highest_time, lowest, lowest_time, average, spread = analyze_data(prices)

    assert highest == 100
    assert highest_time == "00:00"
    assert lowest == 50
    assert lowest_time == "01:00"
    assert round(average, 2) == 76.67
    assert spread == 50

def test_battery_calculations_gain():
    assert battery_calculations_gain(10, 0.9, 100) == 900


def test_battery_calculations_invest():
    prices = {
        "00:00": Energy_Prices("2026-08-24", "00:00", 100),
        "01:00": Energy_Prices("2026-08-24", "01:00", 50),
        "02:00": Energy_Prices("2026-08-24", "02:00", 80),
    }

    total_cost, charging_data, total_charged = battery_calculations_invest(10, 5, prices, "00:00")

    assert total_charged == 0
    assert total_cost == 0
    assert charging_data == []

def test_battery_partial_charging():
    prices = {
        "00:00": Energy_Prices("2026-08-24", "00:00", 30),
        "01:00": Energy_Prices("2026-08-24", "01:00", 10),
        "02:00": Energy_Prices("2026-08-24", "02:00", 100),
        "03:00": Energy_Prices("2026-08-24", "03:00", 1),
    }

    total_cost, charging_data, total_charged = battery_calculations_invest(10, 4, prices, "02:00")

    assert total_charged == 8
    assert total_cost == 160
    assert charging_data == [("00:00", 4, 30), ("01:00", 4, 10)]