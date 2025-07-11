#  John Paul Larkin
#  C00001754
#  Assignment 2
# 1/3/2025

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import datetime
import os
import sqlite3
import pandas as pd
# from matplotlib import pyplot as plt
import requests
from tabulate import tabulate
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from colorama import Fore, Style

# Load API key from .env file
# Alpha Vantage is a financial data platform providing free APIs for stocks data
load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Dict of companies to track Key: Company Name, Value: Stock market Symbol
COMPANIES = {
    "Nvidia": "NVDA",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Alphabet": "GOOGL"
}

DB_FILENAME='stocks.db'

#  Fetches daily stock data(in json format) for a given company symbol from Alpha Vantage api
#  Returns a dictionary of stock data for a single company
def fetch_stock_data(symbol: str) -> dict:
    #  symbol is the stock symbol of the company to fetch data for i.e. NVDA, MSFT, TSLA, GOOGL
    # Alpha Vantage API URL
    BASE_URL = "https://www.alphavantage.co/query"
    
    #  Parameters for the API request
    #  Global Quote is a function that returns the latest quote for a prrticular stock
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    #  Requests the data from the API and converts it to a dictionary from json
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    #  If the data is not found, print an error message
    if "Global Quote" not in data:
        print(f"Error fetching data for {symbol}: {data}")
    
    print(f"Fetched data for {symbol}:")
    print((data["Global Quote"]))
    #  Returns the data for the company
    return data["Global Quote"]

#  Fetches the headlines for a given company symbol from Yahoo Finance
#  Returns a list of tuples( headline and the url of the article)
def get_yahoo_headlines(symbol: str) -> list[tuple[str, str]]:

    #  Usied a real browser User-Agent string to avoid being blocked by Yahoo anti-bot measures
    #  This makes our request appear as if it's coming from a Chrome browser rather than a script
    # taken from https://www.zenrows.com/blog/user-agent-web-scraping#importance
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/115.0.0.0 Safari/537.36')
    }
    
    #  url when a search is made on yahoo finance for a given company symbol
    #  Auto correct was changeing the search term - had to experiment with the url
    url= f"https://search.yahoo.com/search;_ylt=AwrEtespXrtnjPQMAQRXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Fydw--?ei=UTF-8&fp=1&p={symbol}&norw=1&fr=yfp-t"
    
    try:
        print(f"Fetching data for {symbol} from Yahoo Finance")
        #  Requests the data from the url
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error retrieving data: {e}")
    
    #  BeautifulSoup is used to parse the response as html
    soup = BeautifulSoup(response.text, 'html.parser')
    
    headlines = []
    #  Selects all the articles with the class title u-trunc3 and iterates through them
    #  This is the class for the headline of the article and greatly reduces the amount of data to parse
    for article in soup.select("div.title.u-trunc3"):
        #  Selects the span with the class s-title which contains the headline text
        title_span = article.select_one("span.s-title")
        #  Selects the parent anchor tag with the class bkgLink which contains the url of the article
        link = article.find_parent('a', class_='bkgLink')
        #  If the span and link are found, the headline and url are added to the list
        if title_span is not None and link is not None:
            headline = title_span.get_text(strip=True)
            #  Second argument ensures that if the link is not found an empty string is returned. also cast to a str to eleminate list[str] | None
            headline_url = str(link.get('href', '')) 
            #  Appends the headline and url tuple to the list
            headlines.append((headline, headline_url))           
    return headlines



#  Updates the database with the stock and headline data
#  company_stock_data is a list of dictionaries containing the stock data for each company for the latest trading day
#  headlines_data is a list of dictionaries containing the headlines data for each company(tuple of headline and url)
def update_stock_db(company_stock_data: list[dict[str, str]], headlines_data: list[dict[str, list[tuple[str, str]]]]):
    print(f"\nConnecting to database: {DB_FILENAME}")
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    
    #  Creates the stocks and headlines tables in the database - if they don't already exist
    create_tables(cur)
    
    #  Iterates through the company stock data 
    for company in company_stock_data:
        #  Inserts the stock data into the stocks table
        symbol, latest_trading_day = insert_into_stocks_table(cur, company)

        # Now that the stock data has been inserted
        # Iterate through the headlines data and insert the headlines - for that company
        for headline_dict in headlines_data:
            insert_into_headlines_table(cur, symbol, latest_trading_day, headline_dict)
 
    
    conn.commit()
    conn.close()
    print("\nDatabase operations completed.")
    
#  Creates the stocks and headlines tables in the database - if they don't already exist
def create_tables(cur: sqlite3.Cursor)-> None:
    print("Creating stocks table...")
    #  Creates the stocks table - if it doesn't already exist 
    #  Unique constraint (symbol, latest_trading_day) ensures that each company's stock data is unique for a given trading day
    cur.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            open TEXT,
            high TEXT,
            low TEXT,
            price TEXT,
            volume TEXT,
            latest_trading_day TEXT,
            previous_close TEXT,
            change TEXT,
            change_percent TEXT,
            UNIQUE(symbol, latest_trading_day)
        );
    ''')
    
    print("Creating headlines table...")
    #  Creates the headlines table - if it doesn't already exist 
    #  Unique constraint (headline, latest_trading_day) ensures that each headline is unique for a given trading day
    #  Foreign key constraint (symbol) references the stocks table - if the stock is deleted, the headline is also deleted
    cur.execute('''
        CREATE TABLE IF NOT EXISTS headlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            headline TEXT,
            url TEXT,
            latest_trading_day TEXT,
            UNIQUE(headline, latest_trading_day)
            FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
        );
    ''') 

#  Inserts the stock data into the stocks table - for an individual company
#  Returns the symbol and latest trading day - as they are used in the headlines table
def insert_into_stocks_table(cur: sqlite3.Cursor, company: dict) -> tuple[str, str]:
    #  For each company, the stock data is extracted from the dictionary and added to a row_data dictionary
    row_data = {
        'symbol': company['01. symbol'],
        'open': company['02. open'],
        'high': company['03. high'],
        'low': company['04. low'],
        'price': company['05. price'],
        'volume': company['06. volume'],
        'latest_trading_day': company['07. latest trading day'],
        'previous_close': company['08. previous close'],
        'change': company['09. change'],
        'change_percent': company['10. change percent'],
    }

    # symbol and latest trading day - Used in the headlines table
    symbol = row_data['symbol']
    latest_trading_day = row_data['latest_trading_day']    
    
    # print to see what we are trying to insert
    print("\nAttempting to insert data:")
    print(f"Symbol: {symbol}")
    print(f"Latest Trading Day: {latest_trading_day}")
    
    # Creates a list of the column names 
    columns = list(row_data.keys())
    # Creates a string of ?'s for each column ie - "?, ?, ?, ?, ?, ?, ?, ?, ?, ?"
    placeholders = ", ".join("?" for _ in columns)
    # A list of the values to be inserted
    values = [row_data[col] for col in columns]
     
    try:
        cur.execute(f"""
            INSERT INTO stocks ({', '.join(columns)})
            VALUES ({placeholders})
        """, values)
        
        print(f"Successfully inserted/updated data for {symbol}")
    except sqlite3.Error as e:
        print(f"Error with database operation: {e}")
        print("Values being inserted:", values)  

    return symbol, latest_trading_day

#  Inserts the headlines into the headlines table - for an individual company
def insert_into_headlines_table(cur: sqlite3.Cursor, symbol: str, latest_trading_day: str,headline_dict: dict[str, list[tuple[str, str]]]):
     #  We only insert the headlines for the current company(aka symbol)
    if symbol in headline_dict:
        for headline_text, headline_url in headline_dict[symbol]:
            #  Inserts the headline data into the headlines table
            try:
                cur.execute('''
                    INSERT INTO headlines (symbol, headline, url, latest_trading_day   )
                    VALUES (?, ?, ?, ?)
                ''', (symbol, headline_text, headline_url, latest_trading_day))
                print(f"Successfully inserted/updated headline for {symbol}")
            except sqlite3.Error as e:
                print(f"Error inserting headline: {e}")

#  Writes the stock and headlines data to a text file 
#  This is used to verify the data that is being inserted into the database
def write_stock_data_to_txt_file(company_stock_data: list[dict[str, str]], headlines_data: list[dict[str, list[tuple[str, str]]]]):
    with open('stock_data.txt', 'w') as f:
        f.write(str(company_stock_data))
        f.write("\n\n")
        f.write(str(headlines_data))
        
#  Helper function to verify the contents of the database 
#  by printing the contents of the stocks and headlines tables - after the data has been inserted 
def verify_db_contents(cur: sqlite3.Cursor) -> None:
    cur.execute("SELECT * FROM stocks")
    rows = cur.fetchall()
    print("\Stock table contents:")
    for row in rows:
        print(row)
    print("\nHeadlines table contents:")
    cur.execute("SELECT * FROM headlines")
    rows = cur.fetchall()
    for row in rows:
        print(row)

#  Fetches the stock and headline data for all companies
def fetch_data() -> tuple[list[dict[str, str]], list[dict[str, list[tuple[str, str]]]]]:

    company_stock_data = []
    headlines_data = []
    
    for company, symbol in COMPANIES.items():
        print(f"Fetching data for {company} symbol:({symbol})...")
        #  Fetch the stock data for the company 
        company_data = fetch_stock_data(symbol)
        company_stock_data.append(company_data)        
        #  Fetch the headlines for the company
        headline_data = get_yahoo_headlines(symbol)
        headlines_data.append({symbol: headline_data})
    
    return (company_stock_data, headlines_data)


# Displays a list of companies and their symbols to the user.
# Returns the user's selection as a company name.
def get_user_option() -> str:
    # Create a list of companies from the COMPANIES dictionary keys
    companies_list = list(COMPANIES.keys())
    
    # Print available companies with index numbers and their symbols
    print("\nAvailable options:")
    # Start at index 1, rather than 0
    for idx, company in enumerate(companies_list, 1):
        print(f"{idx}. {company} ({COMPANIES[company]})")
    print("A. All companies")
    
    # Get user input
    while True:
        choice = input("\nEnter selection number or 'A' for all (or 'Q' to quit): ").strip()
        if choice.lower() == 'q':
            return 'quit'
        elif choice.lower() == 'a':
            return 'all'
        elif choice.isdigit() and 0 < int(choice) <= len(companies_list):
            return companies_list[int(choice) - 1]
        else:
            print("Invalid selection. Please try again.")

# Helper to fetch historical stock data for given company symbols from the database. 
def fetch_historical_stock_data(symbols: list[str]) -> list[tuple]:
    # Symbols can be a list with a single company, or a list of all companies
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()

    try:
        # Create a comma-separated string of placeholders for the query ie - "?, ?, ?, ?, ?, ?, ?, ?, ?, ?"
        placeholders = ','.join('?' * len(symbols))
        cur.execute(f"""
            SELECT 
                symbol,
                latest_trading_day,
                price,
                change,
                change_percent,
                volume,
                high,
                low,
                open,
                previous_close
            FROM stocks 
            WHERE symbol IN ({placeholders})
            ORDER BY symbol, latest_trading_day ASC
        """, symbols)
        
        return cur.fetchall()
        
    except sqlite3.Error as e:
        print(f"Error querying database: {e}")
        return []
    finally:
        conn.close()

# Helper function to color table cells based on comparison with its previous days value.
# Returns a green/red string if value changed, white string if unchanged
def color_numeric_cell_value(curr_val: float, prev_val: float, value_str: str) -> str:
    # If current value is greater than previous value, color green
    if curr_val > prev_val:
        return f"{Fore.GREEN}{value_str}{Style.RESET_ALL}"
    # If current value is less than previous value, color red
    elif curr_val < prev_val:
        return f"{Fore.RED}{value_str}{Style.RESET_ALL}"
    # If current value is equal to previous value, color white - ie no change, or first entry
    else:
        return f"{Fore.WHITE}{value_str}{Style.RESET_ALL}"

# Displays historical stock data for a user-selected company in a formatted table.
# Data is retrieved from the database and shows how the stock has changed over time.
def tabulate_data() -> None:
  
    # Print the list of companies and get the user's selection
    user_option = get_user_option()
    if user_option == 'quit':
        return
    elif user_option == 'all':
        # Symbols can be a list with a single company, or a list of all companies
        symbols = list(COMPANIES.values())
    else:
        symbols = [COMPANIES[user_option]]
         
    # Create headers for the table
    headers = [
        'Symbol', 'Date', 'Price', 'Change', 'Change %',
        'Volume', 'High', 'Low', 'Open', 'Prev Close'
    ]
    
    # table_data contains the data to be printed by tabulate
    table_data = []
    # prev_values contains the comparison value
    prev_values = {}
    current_symbol = None
    
    print("Colors indicate changes from previous day:")
    print(f"{Fore.GREEN}Green: Increase{Style.RESET_ALL}") 
    print(f"{Fore.RED}Red: Decrease{Style.RESET_ALL}")
    print(f"{Fore.WHITE}White: No change or first entry{Style.RESET_ALL}")
    input("Press any key to continue...")
    
    #  query the database for the historical stock data
    rows = fetch_historical_stock_data(symbols)
    if not rows:
        print(f"No data found")
        return
      
    #  iterate through the rows and add the data to the table
    for row in rows:
        symbol = row[0]
        
        # Add empty row when switching to a new company
        # Simply for clarity in the table, when printing multiple companies
        if current_symbol is not None and symbol != current_symbol:
            table_data.append([''] * len(headers))  # Add empty row
            
        current_symbol = symbol
        
        # Convert row tuple to a list so we can replace strings with colored strings
        colored_row = list(row)
        
        # If it's the very first row we see for this symbol, just store & skip coloring
        if symbol not in prev_values:
            prev_values[symbol] = {
                'price': float(row[2]),
                'change': float(row[3]),
                # remove the % sign and convert to float
                'change_percent': float(row[4].rstrip('%')),
                'volume': int(row[5]),
                'high': float(row[6]),
                'low': float(row[7]),
                'open': float(row[8])
            }
            table_data.append(colored_row)
            #  continue to the next row - we don't need to compare the first row to itself
            continue
        
        # Otherwise compare day vs. previous day for that symbol:
        prev = prev_values[symbol]
        
        # (2) Price
        curr_price = float(row[2])
        colored_row[2] = color_numeric_cell_value(curr_price, prev['price'], row[2])
        
        # (3) Change vs. yesterday's Change
        curr_change = float(row[3])
        colored_row[3] = color_numeric_cell_value(curr_change, prev['change'], row[3])
        
        # (4) Change % vs. yesterday's Change %
        curr_chg_pct = float(row[4].rstrip('%'))
        colored_row[4] = color_numeric_cell_value(curr_chg_pct, prev['change_percent'], row[4])
        
        # (5) Volume
        curr_vol = int(row[5])
        colored_row[5] = color_numeric_cell_value(curr_vol, prev['volume'], row[5])
        
        # (6) High
        curr_high = float(row[6])
        colored_row[6] = color_numeric_cell_value(curr_high, prev['high'], row[6])
        
        # (7) Low
        curr_low = float(row[7])
        colored_row[7] = color_numeric_cell_value(curr_low, prev['low'], row[7])
        
        # (8) Open
        curr_open = float(row[8])
        colored_row[8] = color_numeric_cell_value(curr_open, prev['open'], row[8])
        
        # Append colored row
        table_data.append(colored_row)
        
        # update stored previous values - used for comparing to the next row
        prev_values[symbol] = {
            'price': curr_price,
            'change': curr_change,
            'change_percent': curr_chg_pct,
            'volume': curr_vol,
            'high': curr_high,
            'low': curr_low,
            'open': curr_open
        }
    
    print(f"\nHistorical Stock Data for {symbols}:")
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    

#  Visualise the stock data in a candlestick chart
def visualise_data():
    # Print the list of companies and get the user's selection
    user_option = get_user_option()
    if user_option == 'quit':
        return
    elif user_option == 'all':
        # Symbols can be a list with a single company, or a list of all companies
        symbols = list(COMPANIES.values())
    else:
        symbols = [COMPANIES[user_option]]
        
    #  query the database for the historical stock data
    rows = fetch_historical_stock_data(symbols)
    
    # Column names matching the tuple order
    columns = [
        "symbol", "date", "close", "change", "percent_change", "volume",
        "high", "low", "open", "prev_close"
    ]

    # Convert rows to a DataFrame
    dataframe = pd.DataFrame(rows, columns=columns)
    
    # Convert date to datetime - this is required for the candlestick chart 
    dataframe['date'] = pd.to_datetime(dataframe['date'])

    # Convert numeric columns
    numeric_cols = ["close", "change", "volume", "high", "low", "open", "prev_close"]
    for col in numeric_cols:
        dataframe[col] = pd.to_numeric(dataframe[col])

    symbols = dataframe['symbol'].unique()
    symbol_count = len(symbols)
    #  Calculate the number of days in the dataset - Newest date less the oldest date
    #  This is used to determine the width of the chart
    days_count = (dataframe['date'].max() - dataframe['date'].min()).days


    # Create subplots – one row per symbol
    fig, axs = plt.subplots(symbol_count, 1, figsize=(days_count * 2, 4 * symbol_count))
    if symbol_count == 1:
        # Make sure axs is iterable if there's only one symbol
        # There may be multiiple symobls if the user selects all
        axs = [axs]  

    # Create legend patches (green for increase, red for decrease)
    up_patch = mpatches.Patch(color='green', label='Indicates daily increase')
    down_patch = mpatches.Patch(color='red', label='Indicates daily drop')
    high_low_patch = mpatches.Patch(color='yellow', label='Daily High-Low')

    #  Iterate through the subplots and symbols
    for ax, symbol in zip(axs, symbols):
        df_symbol = dataframe[dataframe['symbol'] == symbol].sort_values('date')

        # Plot candlesticks
        x_vals = df_symbol['date']
    
        closes = df_symbol['close']
        
        for _, row in df_symbol.iterrows():
            day = row['date']
            open = row['open']
            close = row['close']
            high = row['high']
            low = row['low']

            # Choose color: green if close >= open, otherwise red for the candlestick body
            color = 'green' if close >= open else 'red'

            # Compute the bottom, top, and height for the candlestick body
            bar_bottom = min(open, close)
            bar_top = max(open, close)
            bar_height = bar_top - bar_bottom
            
            # Draw the candlestick body for open and close
            ax.bar(day, bar_height, bottom=bar_bottom, width=0.3, color=color, align='edge')


            # Annotate with opening and closing 
            # The top and bottom logic is required, since the bar is inverted on days when the symbol price drops.(red bar)
            ax.text(day, open, f"Open: {open:.2f}", ha='left', 
                    va= 'top' if close >= open else 'bottom', fontsize=8, color='black')
            ax.text(day, close, f"Close: {close:.2f}", ha='left', 
                    va= 'bottom' if close >= open else 'top', fontsize=8, color='black')
            
            #  Draw the candlestick body for high and low
            #  -7 is the offset to the left to align to the left of the open-close candlestick 
            ax.bar(day + pd.Timedelta(hours=-7), high - low, bottom=low, width=0.3, color='yellow', align='edge')
            
            # Annotate yellow bar with high and low
            ax.text(day, high, f"High: {high:.2f}", ha='right', 
                    va= 'bottom', fontsize=8, color='black')         
            ax.text(day, low, f"Low: {low:.2f}", ha='right', 
                    va= 'bottom', fontsize=8, color='black')

        # plot the line for daily highs (blue line with markers)
        line_high, = ax.plot(
            x_vals, 
            closes, 
            color='blue', 
            marker='o', 
            linewidth=1, 
            label='Daily Close'
        )

        # Configure the subplot / header
        #  Get the company name from the COMPANIES dictionary which matches the symbol
        company_name = [name for name, sym in COMPANIES.items() if sym == symbol][0]
        ax.set_title(f'Chart for {company_name}', fontsize=12)
        ax.set_ylabel('Price')
        ax.grid(True)

        # Get all unique dates for this symbol
        dates = df_symbol['date'].unique()

        # Set one tick for each date
        ax.set_xticks(dates)

        # Format x-axis with gridlines for each date
        ax.grid(True, axis='x')  # Add vertical gridlines
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())  # Force a tick for each day

        # Rotate labels for better readability
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_horizontalalignment('right')

        # Plot the legend
        ax.legend(handles=[up_patch, down_patch, line_high, high_low_patch], loc='best')

    # Tighten the layout to prevent overlapping labels
    plt.tight_layout()
    plt.show()
    
    

def main():
    (company_stock_data, headlines_data) = fetch_data()
    print("\nStarting database update...")
    update_stock_db(company_stock_data, headlines_data) 
    
    # This functions are commented out as they are only used in development
    # write_stock_data_to_txt_file(company_stock_data, headlines_data)
    # verify_db_contents()
    
    # Display the stock data in a formatted table
    tabulate_data()
    # Display historical data for user-selected company
    visualise_data()
    
if __name__ == "__main__":
    main()
    
    
 
  
    
