# Power Market Analyzer

#### Video Demo: https://youtu.be/UseAPwtA7UA

#### Description:
Power Market Analyzer is a Python program I created to work with real electricity price data from the OMIE (the electricity market operator for Spain and Portugal). I wanted the project to be related to energy while also using different Python concepts I learned during CS50P, such as classes, functions, working with online data, calculations, user input, error handling, and testing.

The program has three main options. The first one is Today's Market Analysis. It downloads the current electricity prices and calculates the highest price, lowest price, average price, and the price spread during the day. This gives the user a quick overview of how electricity prices change throughout the day.

The second option is a Battery Trading Simulator. The user enters the battery capacity, maximum charging rate, and battery efficiency. The program selects the cheapest available hours before the selected selling hour to charge the battery, respecting its capacity and maximum charging rate. It then calculates the charging cost. It also estimates the revenue and final profit if the stored energy is sold during the hour with the highest electricity price. The simulator is simplified, but it shows how price differences during the day can be used in battery energy trading.

The third option is Historical Price Comparison. The user can enter two different dates and compare electricity prices from those days. The program shows the average, highest, and lowest prices, as well as the price range and the percentage change in the average price. It also shows which of the two days was more expensive.

The program downloads real data directly from OMIE. Newer data can be downloaded as individual files, while older historical data is stored in ZIP archives. Because of this, I used the requests, zipfile, and io modules to download and read the data. I also added error handling for invalid dates, future dates, incorrect numerical input, internet connection problems, invalid ZIP files, and missing historical data.

The main code is stored in project.py. The tests are stored in test_project.py, where I test some of the most important calculation functions. The requirements.txt file contains the external libraries needed to run the project.

My main goal was to create a program that is simple to use from the terminal, but still works with real-world electricity market data and connects Python programming with energy analysis.

## Installation and usage

Requires Python 3.12 or newer and an internet connection to download prices.

Install the dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the program:

```bash
python3 project.py
```

Choose an option from the terminal menu. For the battery simulator, enter capacity in MWh, maximum charging rate in MW, and efficiency as a percentage, such as 90.

## Tests

Run the tests with:

```bash
python3 -m pytest test_project.py -q
```

The tests cover price objects, market statistics, battery revenue, and charging schedules.

## Simulator assumptions and limitations

- The battery starts empty, and the day's prices are known in advance.
- The simulator uses hourly averages of Spanish electricity prices.
- It selects the highest-price hour for selling and charges during the cheapest available earlier hours.
- Charging respects battery capacity and maximum charging rate. The battery may only partially charge if insufficient time is available.
- Efficiency reduces the energy available for sale.
- All energy remaining after losses is assumed to be sold during the selected hour. Discharge power limits are not modelled.
- Battery degradation, investment costs, taxes, and trading fees are excluded.
- The time mapping assumes standard 24-hour days; daylight-saving transitions are not handled explicitly.
- This is a simplified educational simulation. It does not guarantee a profit or find the most profitable possible strategy.