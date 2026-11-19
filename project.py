import sys
import time
import requests
import datetime
import io
import zipfile
import math

class Energy_Prices:
    def __init__(self, date, time, price):
        self.date = date
        self.time = time
        self.price = float(price)

class Historical_Energy_Prices_One:
    def __init__(self, date, time, price):
        self.date = date
        self.time = time
        self.price = float(price)

class Historical_Energy_Prices_Two:
    def __init__(self, date, time, price):
        self.date = date
        self.time = time
        self.price = float(price)


def main():

    while True:
        interface()
        wanted = user_choice()

        if wanted == "1":
            prices = download_data()
            if not prices:
                print("\nError downloading data. Please check your internet connection or try again later.\n")
                time.sleep(2)
                continue
            highest_price, highest_time, lowest_price, lowest_time, average_price, price_spread = analyze_data(prices)
            analyze_data_output(highest_price, highest_time, lowest_price, lowest_time, average_price, price_spread)

        elif wanted == "2":
            prices = download_data()
            if not prices:
                print("\nError downloading data. Please check your internet connection or try again later.\n")
                time.sleep(2)
                continue
            highest_price, highest_time, _, _, _, _ = analyze_data(prices)
            battery_capacity, max_charge_rate, efficiency = battery_questions()
            total_cost, charging_data, total_charged = battery_calculations_invest(battery_capacity, max_charge_rate, prices, highest_time)
            battery_interface(battery_capacity, max_charge_rate, efficiency, highest_time, highest_price, charging_data, total_charged, total_cost)

        elif wanted == "3":
            first_date, second_date = history_data_choice()
            try:
                prices1, prices2, _, _ = history_data_download(first_date, second_date)
            except requests.RequestException:
                print("\nError downloading data. Please check your internet connection or try again later.\n")
                time.sleep(2)
                continue
            except zipfile.BadZipFile:
                print("\nThe downloaded archive could not be read. Please try again later.\n")
                time.sleep(2)
                continue
            except KeyError:
                print("\nData for one of the selected dates was not found. Please try again with different dates.\n")
                time.sleep(2)
                continue

            if prices1 == {} or prices2 == {}:
                print("No price data is available for one of the selected dates")
                continue
            history_data_output(prices1, prices2, first_date, second_date)

        elif wanted == "4":
            print("Exiting the program...")
            time.sleep(1)
            sys.exit()

def interface():

    width = 45
    print("=" * width)
    print(f"{'POWER MARKET ANALYZER':^{width}}")
    print("=" * width)
    print("\n1. Today's market analysis\n2. Battery trading simulator\n3. Historical price comparision\n4. Exit\n")

def user_choice():
    while True:
        wanted = input("")
        if wanted in ["1", "2", "3", "4"]:
            return wanted


def download_data():

    now = datetime.datetime.now().strftime("%Y%m%d")
    url = f"https://www.omie.es/en/file-download?filename=marginalpdbc_{now}.1&parents=marginalpdbc"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

    except requests.RequestException:
        return None

    hourly_prices = {}
    for line in response.text.splitlines():
        data = line.strip().split(";")
        if len(data) >= 6 and data[0].isdigit():
            date = f"{data[0]}-{data[1]}-{data[2]}"
            period = int(data[3]) - 1
            hour = period // 4
            time_of_day = f"{hour:02d}:00"
            price = float(data[5])

            if time_of_day not in hourly_prices:
                hourly_prices[time_of_day] = []
            hourly_prices[time_of_day].append(price)

    prices = {}
    for time_of_day, hour_prices in hourly_prices.items():
            average_price = sum(hour_prices) / len(hour_prices)
            prices[time_of_day] = Energy_Prices(date, time_of_day, average_price)
    return prices
            
def analyze_data(prices):

    #HIGHEST PRICE
    highest_price = max(x.price for x in prices.values())
    highest_time = None
    for time_of_day, energy in prices.items():
        if energy.price == highest_price:
            highest_time = time_of_day

    #LOWEST PRICE
    lowest_price = min(x.price for x in prices.values())
    lowest_time = None
    for time_of_day, energy in prices.items():
            if energy.price == lowest_price:
                lowest_time = time_of_day

    #AVERAGE PRICE
    sum_prices = 0
    for energy in prices.values():
        sum_prices += energy.price
    average_price = sum_prices / len(prices)

    #PRICE SPREAD
    price_spread = highest_price - lowest_price

    return highest_price, highest_time, lowest_price, lowest_time, average_price, price_spread
        
def analyze_data_output(highest_price, highest_time, lowest_price, lowest_time, average_price, price_spread):

    print("Downloading today's electricity prices...")
    time.sleep(2)

    width = 45
    print("=" * width)
    print(f"{'TODAY"S MARKET ANALYSIS':^{width}}")
    print("=" * width, "\n")
    print(f"Highest Price:\n€{highest_price:.2f}/MWh at {highest_time}")
    print(f"\nLowest Price:\n€{lowest_price:.2f}/MWh at {lowest_time}")
    print(f"\nAverage price:\n€{average_price:.2f}/MWh")
    print(f"\nPrice spread:\n€{price_spread:.2f}/MWh")

    while True:
        x = input("\nPress Enter to return to menu...")
        if x == "":
            return False

def battery_questions():

    width = 45
    print("=" * width)
    print(f"{'BATTERY SIMULATOR':^{width}}")
    print("=" * width, "\n")

    try:
        battery_capacity = float(input("What is the battery capacity?: "))
        max_charge_rate = float(input("What is the maximum charge rate of the battery: "))
        efficiency = float(input("What is the efficiency of the battery?: ").rstrip("%")) * 0.01
        if not math.isfinite(battery_capacity) or not math.isfinite(max_charge_rate) or not math.isfinite(efficiency):
            raise ValueError
        if battery_capacity <= 0 or max_charge_rate <= 0:
            raise ValueError
        elif efficiency <= 0 or efficiency > 1:
            raise ValueError

    except ValueError:
        print("\nAn Error Occured!\nStick to this rules:\n- Capacity and charging rate must be positive numbers\n- Efficiency must be greater than 0% and at most 100%\n- The user should enter the values again\n")
        return battery_questions()

    return battery_capacity, max_charge_rate, efficiency
        
def battery_calculations_gain(total_charged, efficiency, highest_price):
    return total_charged * highest_price * efficiency

def battery_calculations_invest(battery_capacity, max_charge_rate, prices, highest_time):
    prices_list = []
    charging_data = []
    time_to_charge = battery_capacity / max_charge_rate

    if 0 < time_to_charge <= 23:
        for time_of_day, energy in prices.items():
            if time_of_day < highest_time:
                prices_list.append((energy.price, time_of_day))
        sorted_prices_list = sorted(prices_list)
        remaining_capacity = battery_capacity
        total_cost = 0
        total_charged = 0

        for price, time_of_day in sorted_prices_list:
            if remaining_capacity <= 0:
                break
            charge = min(max_charge_rate, remaining_capacity)
            total_charged += charge
            total_cost += charge * price
            remaining_capacity -= charge
            charging_data.append((time_of_day, charge, price))
        
        charging_data = sorted(charging_data)
        return total_cost, charging_data, total_charged

    elif 23 < time_to_charge:
        for time_of_day, energy in prices.items():
            if time_of_day < highest_time:
                prices_list.append((energy.price, time_of_day))
        sorted_prices_list = sorted(prices_list)
        remaining_capacity = 23 * max_charge_rate
        total_cost = 0
        total_charged = 0

        for price, time_of_day in sorted_prices_list:
            if remaining_capacity <= 0:
                break
            charge = min(max_charge_rate, remaining_capacity)
            total_charged += charge
            total_cost += charge * price
            remaining_capacity -= charge
            charging_data.append((time_of_day, charge, price))
        
        charging_data = sorted(charging_data)
        return total_cost, charging_data, total_charged
    
    else:
        print("Battery has no capacity to store energy!")


def battery_interface(battery_capacity, max_charge_rate, efficiency, highest_time, highest_price, charging_data, total_charged, total_cost):

    print("Analyzing today's electricity prices...")
    time.sleep(2)
    print("Calculating the charging schedule...")
    revenue = battery_calculations_gain(total_charged, efficiency, highest_price)
    income = revenue - total_cost
    time.sleep(2)

    width = 45
    print("=" * width)
    print(f"{'SIMULATION RESULT':^{width}}")
    print("=" * width, "\n")
    print(f"\nBattery capacity:   {battery_capacity}MWh\nMax charge rate:   {max_charge_rate}MW\nEfficiency:   {efficiency * 100}%")
    print(f"\nCharging:\n")

    for time_of_day, charge, price in charging_data:
        print(f"{time_of_day}   {charge:.1f} MWh   @  €{price:.2f}/MWh")

    print(f"\nTotal energy charged:   {total_charged:.1f} MWh")
    print(f"Charging cost:            €{total_cost:.2f}")
    print(f"\nSelected selling hour:\n{highest_time}   @ €{highest_price:.2f}/MWh")
    print(f"\nEnergy after losses:   {total_charged * efficiency:.1f} MWh")
    print(f"Revenue:                  €{revenue:.2f}\n")
    print(f"=" * width)
    print("PROFIT:", " " * 19, f"€{income:.2f}")
    while True:
        x = input("\nPress Enter to return to menu...")
        if x == "":
            return False


def history_data_choice():

    width = 45
    print("=" * width)
    print(f"{'HISTORICAL PRICE COMPARISON':^{width}}")
    print("=" * width, "\n")

    while True:
        first_date = input("Enter first date (year-month-day): ")

        try:
            date = datetime.datetime.strptime(first_date, "%Y-%m-%d").date()

            if date < datetime.date(2018, 1, 1):
                print("\nData for this date is not available. Minimum date is 2018-01-01.\n")
                continue

            if date > datetime.date.today():
                print("\nYou cannot enter a future date.\n")
                continue
            first_date = date.strftime("%Y-%m-%d")
            break

        except ValueError:
            print("\nInvalid date format, try once again.\n")

    while True:
        second_date = input("Enter second date (year-month-day): ")

        try:
            date = datetime.datetime.strptime(second_date, "%Y-%m-%d").date()

            if date < datetime.date(2018, 1, 1):
                print("\nData for this date is not available. Minimum date is 2018-01-01.\n")
                continue

            if date > datetime.date.today():
                print("\nYou cannot enter a future date.\n")
                continue
            second_date = date.strftime("%Y-%m-%d")
            if second_date == first_date:
                print("\nYou have entered the same date twice. Please enter two different dates.\n")
                continue

            break

        except ValueError:
            print("\nInvalid date format, try once again.\n")

    print("\nDownloading historical data...")
    time.sleep(2)
    print("Analyzing historical data...")
    time.sleep(2)
    return first_date, second_date

def get_response(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response

def history_data_download(first_date, second_date):

    first_date_new = first_date.replace("-", "")
    second_date_new = second_date.replace("-", "")

    
    if int(first_date_new) >= 20230101:
        url1 = f"https://www.omie.es/en/file-download?filename=marginalpdbc_{first_date_new}.1&parents=marginalpdbc"

        response1 = get_response(url1)
        response1_text = response1.text

    elif 20180101 <= int(first_date_new) < 20230101:
        year = first_date_new[:4]
        url1 = f"https://www.omie.es/en/file-download?filename=marginalpdbc_{year}.zip&parents=marginalpdbc"

        while True:
            response1 = get_response(url1)

            try:
                zip_file = zipfile.ZipFile(io.BytesIO(response1.content))
                wanted_file = f"marginalpdbc_{first_date_new}.1"

                with zip_file.open(wanted_file) as file:
                    response1_text = file.read().decode("utf-8")

                break

            except zipfile.BadZipFile:
                raise
            except KeyError:
                raise


    if int(second_date_new) >= 20230101:
        url2 = f"https://www.omie.es/en/file-download?filename=marginalpdbc_{second_date_new}.1&parents=marginalpdbc"

        response2 = get_response(url2)
        response2_text = response2.text

    elif 20180101 <= int(second_date_new) < 20230101:
        year = second_date_new[:4]
        url2 = f"https://www.omie.es/en/file-download?filename=marginalpdbc_{year}.zip&parents=marginalpdbc"


        while True:
            response2 = get_response(url2)
            try:
                zip_file = zipfile.ZipFile(io.BytesIO(response2.content))
                wanted_file = f"marginalpdbc_{second_date_new}.1"

                with zip_file.open(wanted_file) as file:
                    response2_text = file.read().decode("utf-8")
                break    

            except zipfile.BadZipFile:
                raise         
            except KeyError:
                raise
         
    
    prices1, prices2 = {}, {}
    for line in response1_text.splitlines():
        data = line.strip().split(";")
        if len(data) >= 6 and data[0].isdigit():
            date = f"{data[0]}-{data[1]}-{data[2]}"
            period = int(data[3]) - 1
            if int(first_date_new) < 20251001:
                hour = period
                minute = 0
            else:
                hour = period // 4
                minute = (period % 4) * 15
            time_of_day = f"{hour:02d}:{minute:02d}"
            
            price = float(data[5])
            prices1[time_of_day] = Historical_Energy_Prices_One(date, time_of_day, price)

    for line in response2_text.splitlines():
        data = line.strip().split(";")
        if len(data) >= 6 and data[0].isdigit():
            date = f"{data[0]}-{data[1]}-{data[2]}"
            period = int(data[3]) - 1
            if int(second_date_new) < 20251001:
                hour = period
                minute = 0
            else:
                hour = period // 4
                minute = (period % 4) * 15
            time_of_day = f"{hour:02d}:{minute:02d}"

            price = float(data[5])
            prices2[time_of_day] = Historical_Energy_Prices_Two(date, time_of_day, price)

    return prices1, prices2, first_date_new, second_date_new

def history_average_price(average_price_change):
    if average_price_change > 0:
        print(f"\nAverage price change: +{average_price_change:.2f}%")
    elif average_price_change < 0:
        print(f"\nAverage price change: {average_price_change:.2f}%")
    elif average_price_change == 0:
        print("\nAverage price has not changed")

def history_data_output(prices1, prices2, first_date, second_date):

    highest_price1, _, lowest_price1, _, average_price1, price_spread1 = analyze_data(prices1)
    highest_price2, _, lowest_price2, _, average_price2, price_spread2 = analyze_data(prices2)
    first_date_short = first_date.split("-")
    second_date_short = second_date.split("-")
    date1 = f"{first_date_short[2]}/{first_date_short[1]}"
    date2 = f"{second_date_short[2]}/{second_date_short[1]}"
    width = 45

    print("=" * width)
    print(f"{'HISTORICAL PRICE COMPARISON':^{width}}")
    print("=" * width, "\n")
    print(f"{'':<18}{date1:>10}{date2:>10}")
    print(f"{'Average price':<18}{f'€{average_price1:.2f}':>10}{f'€{average_price2:.2f}':>10}")
    print(f"{'Lowest price':<18}{f'€{lowest_price1:.2f}':>10}{f'€{lowest_price2:.2f}':>10}")
    print(f"{'Highest price':<18}{f'€{highest_price1:.2f}':>10}{f'€{highest_price2:.2f}':>10}")
    print(f"{'Price range':<18}{f'€{price_spread1:.2f}':>10}{f'€{price_spread2:.2f}':>10}")
    if average_price1 > 0:
        average_price_change = ((average_price2 - average_price1) / average_price1) * 100
        history_average_price(average_price_change)
    else:
        print("\nPercetage change unavailable: the first day's average price is zero or negative.")
    if average_price1 > average_price2:       
        print(f"More expensive day: {first_date_short[2]}/{first_date_short[1]}/{first_date_short[0]}")
    elif average_price1 < average_price2:   
        print(f"More expensive day: {second_date_short[2]}/{second_date_short[1]}/{second_date_short[0]}")
    elif average_price1 == average_price2:
        print("The average price was the same on both days")

    while True:
        x = input("\nPress Enter to return to menu...")
        if x == "":
            return False



if __name__ == "__main__":
    main()


