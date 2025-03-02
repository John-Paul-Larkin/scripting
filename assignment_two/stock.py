#  John Paul Larkin
#  C00001754
#  Assignment 2
# 1/3/2025

import os
import sqlite3
import requests
from tabulate import tabulate
from dotenv import load_dotenv
# from tabulate import tabulate
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

def fetch_data() -> tuple[list[dict[str, str]], list[dict[str, list[tuple[str, str]]]]]:

    # company_stock_data = []
    # headlines_data = []
    
    # for company, symbol in COMPANIES.items():
    #     print(f"Fetching data for {company} symbol:({symbol})...")
    #     company_data = fetch_stock_data(symbol)
    #     company_stock_data.append(company_data)        
    #     headline_data = get_yahoo_headlines(symbol)
    #     headlines_data.append({symbol: headline_data})
    
    headlines_data = [
        {'NVDA': [('IsNVIDIACorporation (NVDA) The Best Money Making Stock To Buy Now?', 'https://r.search.yahoo.com/_ylt=AwrhWNbmRMRnwBIBTyNXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125543/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fnvidia-corporation-nvda-best-money-164657872.html%3ffr%3dsycsrp_catchall/RK=2/RS=geeDjOznYxM0qUvaiOjOeD_Vwd4-'), ('Jim Cramer onNVIDIACorporation (NVDA): ‘There Are People Who Think It’s Dramatically Overvalued. And I Don’t Get That’', 'https://r.search.yahoo.com/_ylt=AwrhWNbmRMRnwBIBUyNXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125543/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fjim-cramer-nvidia-corporation-nvda-080254921.html%3ffr%3dsycsrp_catchall/RK=2/RS=WGJGNfohRkQnN9jl_ReR7R4XB88-'), ('Jim Cramer onNVIDIA(NVDA): ‘I Think You Have To Wait To See What The Numbers Are Because The Company...', 'https://r.search.yahoo.com/_ylt=AwrhWNbmRMRnwBIBVyNXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125543/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fjim-cramer-nvidia-nvda-think-115144647.html%3ffr%3dsycsrp_catchall/RK=2/RS=YIezBKqVCrU0WanZD6KCUyJWx8U-')]}, 
        {'MSFT': [('Here’s WhyMicrosoft(MSFT) Stock Returned 13% in Q4', 'https://r.search.yahoo.com/_ylt=AwrhUL3nRMRnPQIAT6BXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125544/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fwhy-microsoft-msft-stock-returned-142857739.html%3ffr%3dsycsrp_catchall/RK=2/RS=qD.mhqWeXwaYkaUQZuVOna55gkM-'), ('MicrosoftCorporation (MSFT): Among the Best Stocks to Buy According to Bill Gates', 'https://r.search.yahoo.com/_ylt=AwrhUL3nRMRnPQIAU6BXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125544/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fmicrosoft-corporation-msft-among-best-191748014.html%3ffr%3dsycsrp_catchall/RK=2/RS=ElJl.tRNPxxcJ6RcENB1O0zTMuk-'), ('MicrosoftCorporation (MSFT): A Bull Case Theory', 'https://r.search.yahoo.com/_ylt=AwrhUL3nRMRnPQIAV6BXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125544/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fmicrosoft-corporation-msft-bull-case-174225857.html%3ffr%3dsycsrp_catchall/RK=2/RS=jRIQ96zBXnjaCOqwx6nVsrroCmo-')]}, 
        {'TSLA': [('WhyTesla(TSLA) Stock Is Sinking Today', 'https://r.search.yahoo.com/_ylt=AwrFGnboRMRnSAIAJ_pXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125545/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fwhy-tesla-tsla-stock-sinking-173331602.html%3ffr%3dsycsrp_catchall/RK=2/RS=FKcIiwH2ReVSMVncIOMvzz_SDWw-'), ('Analyst:Tesla(TSLA) Still Trading At a ‘Fraction’ of Market Opportunity', 'https://r.search.yahoo.com/_ylt=AwrFGnboRMRnSAIAK_pXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125545/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fanalyst-tesla-tsla-still-trading-195358797.html%3ffr%3dsycsrp_catchall/RK=2/RS=J4I9VURTK6fgBANb8bGMmCC9Vw4-'), ('Jim Cramer onTesla, Inc. (TSLA) CEO Elon Musk: ‘There’s A Changeover That He’s Doing On The Autos’', 'https://r.search.yahoo.com/_ylt=AwrFGnboRMRnSAIAL_pXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125545/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fjim-cramer-tesla-inc-tsla-074529126.html%3ffr%3dsycsrp_catchall/RK=2/RS=T2Dn4h46A1kXc_md2nKRt9glsd8-')]}, 
        {'GOOGL': [('Alphabet (GOOGL) Reliance on International Sales: What Investors Need to Know', 'https://r.search.yahoo.com/_ylt=Awril_fpRMRnMgIAOVJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125546/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2falphabet-googl-reliance-international-sales-141527238.html%3ffr%3dsycsrp_catchall/RK=2/RS=bhwBBIlIhCD163gddYM6JBqmiw0-'), ("CanGOOGL's Cloud Investments Push the Stock Higher in 2025?", 'https://r.search.yahoo.com/_ylt=Awril_fpRMRnMgIAQlJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125546/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fgoogls-cloud-investments-push-stock-161300162.html%3ffr%3dsycsrp_catchall/RK=2/RS=AYinFGiT2MWC2Oi3mqFD0lXo7DY-'), ('Alphabet (GOOGL) Ascends But Remains Behind Market: Some Facts to Note', 'https://r.search.yahoo.com/_ylt=Awril_fpRMRnMgIARlJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125546/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2falphabet-googl-ascends-remains-behind-224518632.html%3ffr%3dsycsrp_catchall/RK=2/RS=aDjGqd7D7Ig5p.g43aEB.IMpl0A-')]}]
   
    #   original  
    company_stock_data = [
        {'01. symbol': 'NVDA', '02. open': '120.5000', '03. high': '127.0000', '04. low': '119.3000', '05. price': '126.4500', '06. volume': '400000000', '07. latest trading day': '2025-03-01', '08. previous close': '121.2000', '09. change': '5.2500', '10. change percent': '4.3320%'},
        {'01. symbol': 'MSFT', '02. open': '395.5000', '03. high': '401.2500', '04. low': '390.0000', '05. price': '400.5000', '06. volume': '33000000', '07. latest trading day': '2025-03-01', '08. previous close': '396.7500', '09. change': '3.7500', '10. change percent': '0.9450%'},
        {'01. symbol': 'TSLA', '02. open': '285.0000', '03. high': '300.5000', '04. low': '280.1000', '05. price': '299.8000', '06. volume': '117000000', '07. latest trading day': '2025-03-01', '08. previous close': '286.5000', '09. change': '13.3000', '10. change percent': '4.6450%'},
        {'01. symbol': 'GOOGL', '02. open': '170.0000', '03. high': '173.2500', '04. low': '168.9000', '05. price': '172.1000', '06. volume': '49000000', '07. latest trading day': '2025-03-01', '08. previous close': '169.7500', '09. change': '2.3500', '10. change percent': '1.3840%'}]
     
    # company_stock_data = [
    #     {'01. symbol': 'NVDA', '02. open': '118.0200', '03. high': '125.0900', '04. low': '116.4000', '05. price': '124.9200', '06. volume': '389091145', '07. latest trading day': '2025-02-28', '08. previous close': '120.1500', '09. change': '4.7700', '10. change percent': '3.9700%'}, 
    #     {'01. symbol': 'MSFT', '02. open': '392.6550', '03. high': '397.6300', '04. low': '386.5700', '05. price': '396.9900', '06. volume': '32845658', '07. latest trading day': '2025-02-28', '08. previous close': '392.5300', '09. change': '4.4600', '10. change percent': '1.1362%'}, 
    #     {'01. symbol': 'TSLA', '02. open': '279.5000', '03. high': '293.8800', '04. low': '273.6000', '05. price': '292.9800', '06. volume': '115696968', '07. latest trading day': '2025-02-28', '08. previous close': '281.9500', '09. change': '11.0300', '10. change percent': '3.9120%'}, 
    #     {'01. symbol': 'GOOGL', '02. open': '168.6800', '03. high': '170.6100', '04. low': '166.7700', '05. price': '170.2800', '06. volume': '48130565', '07. latest trading day': '2025-02-28', '08. previous close': '168.5000', '09. change': '1.7800', '10. change percent': '1.0564%'}] 
    
    
    # company_stock_data = [
    # {'01. symbol': 'NVDA', '02. open': '121.1000', '03. high': '128.2000', '04. low': '120.3000', '05. price': '127.6000', '06. volume': '405000000', '07. latest trading day': '2025-03-02', '08. previous close': '126.4500', '09. change': '1.1500', '10. change percent': '0.9091%'},
    # {'01. symbol': 'MSFT', '02. open': '397.8000', '03. high': '403.0000', '04. low': '392.4000', '05. price': '402.0000', '06. volume': '33500000', '07. latest trading day': '2025-03-02', '08. previous close': '400.5000', '09. change': '1.5000', '10. change percent': '0.3750%'},
    # {'01. symbol': 'TSLA', '02. open': '287.5000', '03. high': '302.0000', '04. low': '282.3000', '05. price': '300.5000', '06. volume': '118000000', '07. latest trading day': '2025-03-02', '08. previous close': '299.8000', '09. change': '0.7000', '10. change percent': '0.2334%'},
    # {'01. symbol': 'GOOGL', '02. open': '171.2000', '03. high': '174.5000', '04. low': '169.8000', '05. price': '173.5000', '06. volume': '49500000', '07. latest trading day': '2025-03-02', '08. previous close': '172.1000', '09. change': '1.4000', '10. change percent': '0.8139%'}]

    # company_stock_data = [
    #     {'01. symbol': 'NVDA', '02. open': '122.3000', '03. high': '129.5000', '04. low': '121.4000', '05. price': '128.7500', '06. volume': '410000000', '07. latest trading day': '2025-03-03', '08. previous close': '128.7500', '09. change': '1.2000', '10. change percent': '0.9310%'},
    #     {'01. symbol': 'MSFT', '02. open': '402.5000', '03. high': '408.0000', '04. low': '398.0000', '05. price': '407.0000', '06. volume': '34000000', '07. latest trading day': '2025-03-03', '08. previous close': '402.0000', '09. change': '5.0000', '10. change percent': '1.2438%'},
    #     {'01. symbol': 'TSLA', '02. open': '289.0000', '03. high': '305.0000', '04. low': '285.0000', '05. price': '303.5000', '06. volume': '119500000', '07. latest trading day': '2025-03-03', '08. previous close': '300.5000', '09. change': '3.0000', '10. change percent': '1.0000%'},
    #     {'01. symbol': 'GOOGL', '02. open': '172.5000', '03. high': '175.8000', '04. low': '171.0000', '05. price': '175.0000', '06. volume': '50000000', '07. latest trading day': '2025-03-03', '08. previous close': '173.5000', '09. change': '1.5000', '10. change percent': '0.8633%'}]

    
    return (company_stock_data, headlines_data)



# Helper function to color table cells based on comparison with its previous days value.
# Returns a Colored string if value changed, original string if unchanged
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
  
    # Print available companies with index numbers
    print("\nAvailable options:")
    companies_list = list(COMPANIES.items())
    for idx, (company, symbol) in enumerate(companies_list, 1):
        print(f"{idx}. {company} ({symbol})")
    print("A. All companies")
    
    # Get user input
    while True:
        choice = input("\nEnter selection number or 'A' for all (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        if choice.lower() == 'a':
            symbols = list(COMPANIES.values())
            company_name = "All Companies"
            break
        try:
            idx = int(choice)
            if 1 <= idx <= len(companies_list):
                company_name, symbol = companies_list[idx-1]
                symbols = [symbol]
                break
        except ValueError:
            pass
        print("Invalid selection. Please try again.")
    
    # Connect to database
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    
    # Query the database for historical data of the selected company/companies
    try:
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
        
        rows = cur.fetchall()
        if not rows:
            print(f"No data found for {company_name}")
            return
            
        headers = [
            'Symbol', 'Date', 'Price', 'Change', 'Change %',
            'Volume', 'High', 'Low', 'Open', 'Prev Close'
        ]
        
        table_data = []
        prev_values = {}
        current_symbol = None
        
 
        print("Colors indicate changes from previous day:")
        print(f"{Fore.GREEN}Green: Increase{Style.RESET_ALL}") 
        print(f"{Fore.RED}Red: Decrease{Style.RESET_ALL}")
        print(f"{Fore.WHITE}White: No change or first entry{Style.RESET_ALL}")
        input("Press any key to continue...")
          
        for row in rows:
            symbol = row[0]
            
            # Add empty row when switching to a new company
            if current_symbol is not None and symbol != current_symbol:
                table_data.append([''] * len(headers))  # Add empty row
                
            current_symbol = symbol
            
            # Convert row tuple -> list so we can replace strings with colored strings
            colored_row = list(row)
            
            # If it's the very first row we see for this symbol, just store & skip coloring
            if symbol not in prev_values:
                prev_values[symbol] = {
                    'price': float(row[2]),
                    'change': float(row[3]),
                    'change_percent': float(row[4].rstrip('%')),
                    'volume': int(row[5]),
                    'high': float(row[6]),
                    'low': float(row[7]),
                    'open': float(row[8])
                }
                table_data.append(colored_row)
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
            
            # Finally, update stored "previous" values
            prev_values[symbol] = {
                'price': curr_price,
                'change': curr_change,
                'change_percent': curr_chg_pct,
                'volume': curr_vol,
                'high': curr_high,
                'low': curr_low,
                'open': curr_open
            }
        
        print(f"\nHistorical Stock Data for {company_name}:")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    except sqlite3.Error as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()



def main():
    (company_stock_data, headlines_data) = fetch_data()
    
    # write_stock_data_to_txt_file(company_stock_data, headlines_data)
  
    
    print("\nStarting database update...")
    update_stock_db(company_stock_data, headlines_data) 
    # verify_db_contents()
    
    
    # Display the stock data in a formatted table
    # Display historical data for user-selected company
    tabulate_data()
    
if __name__ == "__main__":
    main()
    
    
 
  
    
