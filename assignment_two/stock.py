#  John Paul Larkin
#  c00001754
#  Assignment 2
# 1/3/2025

import os
import sqlite3
import requests
import pandas as pd 
from dotenv import load_dotenv
# from tabulate import tabulate
from bs4 import BeautifulSoup

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

#  Fetches daily stock data(in json format) for a given company symbol from Alpha Vantage api
def fetch_stock_data(symbol: str) -> dict:
    #  symbol is the stock symbol of the company to fetch data for i.e. NVDA, MSFT, TSLA, GOOGL
    #  Returns a dictionary of stock data for a single company
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

    if "Global Quote" not in data:
        #  If the data is not found, print an error message
        print(f"Error fetching data for {symbol}: {data}")
    
    print(f"Fetched data for {symbol}:")
    print((data["Global Quote"]))
    #  Returns the data for the company
    return data["Global Quote"]



def get_yahoo_headlines(symbol: str) -> list[tuple[str, str]]:

    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/115.0.0.0 Safari/537.36')
    }
    
    url= f"https://search.yahoo.com/search;_ylt=AwrEtespXrtnjPQMAQRXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Fydw--?ei=UTF-8&fp=1&p={symbol}&norw=1&fr=yfp-t"
    #  Auto cirrect was changeing the search term - had to experiment
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error retrieving data: {e}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    headlines = []
    
    for article in soup.select("div.title.u-trunc3"):
        title_span = article.select_one("span.s-title")
        link = article.find_parent('a', class_='bkgLink')
        if title_span is not None and link is not None:
            headline = title_span.get_text(strip=True)
            #  Second argument ensures that if the link is not found, and cast to a str if an empty string is returned - instead of list[str] | None
            headline_url = str(link.get('href', ''))  # Forces string type  
            headlines.append((headline, headline_url))
             
    return headlines



def verify_db_contents(db_file='stocks.db'):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT * FROM stocks")
    rows = cur.fetchall()
    print("\nDatabase contents:")
    for row in rows:
        print(row)
    conn.close()

def update_stock_db(company_stock_data: list[dict[str, str]], headlines_data: list[dict[str, list[tuple[str, str]]]], db_file='stocks.db'):
    print(f"\nConnecting to database: {db_file}")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    print("Creating stocks table...")
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
    
    for company in company_stock_data:
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
        
        symbol = row_data['symbol']
        latest_trading_day = row_data['latest_trading_day']
        
        # Debug print to see what we're trying to insert
        print("\nAttempting to insert data:")
        print(f"Symbol: {symbol}")
        print(f"Latest Trading Day: {latest_trading_day}")
        
        columns = row_data  # Use row_data as our columns dictionary
        
        values = [columns[col] for col in columns.keys()]
        
        placeholders = ", ".join("?" for _ in columns)
        update_cols = ", ".join(f"{col}=excluded.{col}" for col in columns.keys() if col not in ['symbol', 'latest_trading_day'])
        
        sql = f"""
            INSERT INTO stocks ({', '.join(columns.keys())})
            VALUES ({placeholders})
            ON CONFLICT(symbol, latest_trading_day) 
            DO UPDATE SET {update_cols}
        """
        
        try:
            cur.execute(sql, values)
            print(f"Successfully inserted/updated data for {symbol}")
        except sqlite3.Error as e:
            print(f"Error with database operation: {e}")
            print("Values being inserted:", values)  # Debug print 
 
    
        for headline_dict in headlines_data:
     
            if symbol in headline_dict:
                for headline_text, headline_url in headline_dict[symbol]:
                   
                       
                    headlines_row_data =  {
                        'symbol': symbol,
                        'headline': headline_text,
                        'url': headline_url,
                        'latest_trading_day': latest_trading_day
                    }
        
                    try:
                        cur.execute('''
                            INSERT INTO headlines (symbol, headline, url, latest_trading_day   )
                            VALUES (?, ?, ?, ?)
                        ''', (headlines_row_data['symbol'], headlines_row_data['headline'], headlines_row_data['url'], headlines_row_data['latest_trading_day']))
                        print(f"Successfully inserted/updated headline for {symbol}")
                    except sqlite3.Error as e:
                        print(f"Error inserting headline: {e}")
 
    
    conn.commit()
    conn.close()
    print("\nDatabase operations completed.")

def write_stock_data_to_txt_file(company_stock_data: list[dict[str, str]], headlines_data: list[dict[str, list[tuple[str, str]]]]):
    with open('stock_data.txt', 'w') as f:
        f.write(str(company_stock_data))
        f.write("\n\n")
        f.write(str(headlines_data))

def fetch_data() -> tuple[list[dict[str, str]], list[dict[str, list[tuple[str, str]]]]]:
    

    # company_stock_data = []
    # headlines_data = []
    
    # for company, symbol in COMPANIES.items():
    #     print(f"Fetching data for {company} symbol:({symbol})...")
    #     company_data = fetch_stock_data(symbol)
    #     company_stock_data.append(company_data)        
        # headline_data = get_yahoo_headlines(symbol)
        # headlines_data.append({symbol: headline_data})
        
    company_stock_data = [
        {'01. symbol': 'NVDA', '02. open': '118.0200', '03. high': '125.0900', '04. low': '116.4000', '05. price': '124.9200', '06. volume': '389091145', '07. latest trading day': '2025-02-28', '08. previous close': '120.1500', '09. change': '4.7700', '10. change percent': '3.9700%'}, 
        {'01. symbol': 'MSFT', '02. open': '392.6550', '03. high': '397.6300', '04. low': '386.5700', '05. price': '396.9900', '06. volume': '32845658', '07. latest trading day': '2025-02-28', '08. previous close': '392.5300', '09. change': '4.4600', '10. change percent': '1.1362%'}, 
        {'01. symbol': 'TSLA', '02. open': '279.5000', '03. high': '293.8800', '04. low': '273.6000', '05. price': '292.9800', '06. volume': '115696968', '07. latest trading day': '2025-02-28', '08. previous close': '281.9500', '09. change': '11.0300', '10. change percent': '3.9120%'}, 
        {'01. symbol': 'GOOGL', '02. open': '168.6800', '03. high': '170.6100', '04. low': '166.7700', '05. price': '170.2800', '06. volume': '48130565', '07. latest trading day': '2025-02-28', '08. previous close': '168.5000', '09. change': '1.7800', '10. change percent': '1.0564%'}] 
    
    headlines_data = [
        {'NVDA': [('IsNVIDIACorporation (NVDA) The Best Money Making Stock To Buy Now?', 'https://r.search.yahoo.com/_ylt=AwrhWNbmRMRnwBIBTyNXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125543/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fnvidia-corporation-nvda-best-money-164657872.html%3ffr%3dsycsrp_catchall/RK=2/RS=geeDjOznYxM0qUvaiOjOeD_Vwd4-'), ('Jim Cramer onNVIDIACorporation (NVDA): ‘There Are People Who Think It’s Dramatically Overvalued. And I Don’t Get That’', 'https://r.search.yahoo.com/_ylt=AwrhWNbmRMRnwBIBUyNXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125543/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fjim-cramer-nvidia-corporation-nvda-080254921.html%3ffr%3dsycsrp_catchall/RK=2/RS=WGJGNfohRkQnN9jl_ReR7R4XB88-'), ('Jim Cramer onNVIDIA(NVDA): ‘I Think You Have To Wait To See What The Numbers Are Because The Company...', 'https://r.search.yahoo.com/_ylt=AwrhWNbmRMRnwBIBVyNXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125543/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fjim-cramer-nvidia-nvda-think-115144647.html%3ffr%3dsycsrp_catchall/RK=2/RS=YIezBKqVCrU0WanZD6KCUyJWx8U-')]}, 
        {'MSFT': [('Here’s WhyMicrosoft(MSFT) Stock Returned 13% in Q4', 'https://r.search.yahoo.com/_ylt=AwrhUL3nRMRnPQIAT6BXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125544/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fwhy-microsoft-msft-stock-returned-142857739.html%3ffr%3dsycsrp_catchall/RK=2/RS=qD.mhqWeXwaYkaUQZuVOna55gkM-'), ('MicrosoftCorporation (MSFT): Among the Best Stocks to Buy According to Bill Gates', 'https://r.search.yahoo.com/_ylt=AwrhUL3nRMRnPQIAU6BXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125544/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fmicrosoft-corporation-msft-among-best-191748014.html%3ffr%3dsycsrp_catchall/RK=2/RS=ElJl.tRNPxxcJ6RcENB1O0zTMuk-'), ('MicrosoftCorporation (MSFT): A Bull Case Theory', 'https://r.search.yahoo.com/_ylt=AwrhUL3nRMRnPQIAV6BXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125544/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fmicrosoft-corporation-msft-bull-case-174225857.html%3ffr%3dsycsrp_catchall/RK=2/RS=jRIQ96zBXnjaCOqwx6nVsrroCmo-')]}, 
        {'TSLA': [('WhyTesla(TSLA) Stock Is Sinking Today', 'https://r.search.yahoo.com/_ylt=AwrFGnboRMRnSAIAJ_pXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125545/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fwhy-tesla-tsla-stock-sinking-173331602.html%3ffr%3dsycsrp_catchall/RK=2/RS=FKcIiwH2ReVSMVncIOMvzz_SDWw-'), ('Analyst:Tesla(TSLA) Still Trading At a ‘Fraction’ of Market Opportunity', 'https://r.search.yahoo.com/_ylt=AwrFGnboRMRnSAIAK_pXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125545/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fanalyst-tesla-tsla-still-trading-195358797.html%3ffr%3dsycsrp_catchall/RK=2/RS=J4I9VURTK6fgBANb8bGMmCC9Vw4-'), ('Jim Cramer onTesla, Inc. (TSLA) CEO Elon Musk: ‘There’s A Changeover That He’s Doing On The Autos’', 'https://r.search.yahoo.com/_ylt=AwrFGnboRMRnSAIAL_pXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125545/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fjim-cramer-tesla-inc-tsla-074529126.html%3ffr%3dsycsrp_catchall/RK=2/RS=T2Dn4h46A1kXc_md2nKRt9glsd8-')]}, 
        {'GOOGL': [('Alphabet (GOOGL) Reliance on International Sales: What Investors Need to Know', 'https://r.search.yahoo.com/_ylt=Awril_fpRMRnMgIAOVJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125546/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2falphabet-googl-reliance-international-sales-141527238.html%3ffr%3dsycsrp_catchall/RK=2/RS=bhwBBIlIhCD163gddYM6JBqmiw0-'), ("CanGOOGL's Cloud Investments Push the Stock Higher in 2025?", 'https://r.search.yahoo.com/_ylt=Awril_fpRMRnMgIAQlJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125546/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fgoogls-cloud-investments-push-stock-161300162.html%3ffr%3dsycsrp_catchall/RK=2/RS=AYinFGiT2MWC2Oi3mqFD0lXo7DY-'), ('Alphabet (GOOGL) Ascends But Remains Behind Market: Some Facts to Note', 'https://r.search.yahoo.com/_ylt=Awril_fpRMRnMgIARlJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742125546/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2falphabet-googl-ascends-remains-behind-224518632.html%3ffr%3dsycsrp_catchall/RK=2/RS=aDjGqd7D7Ig5p.g43aEB.IMpl0A-')]}]
    
    write_stock_data_to_txt_file(company_stock_data, headlines_data)
    
    return (company_stock_data, headlines_data)

def main():
    (company_stock_data, headlines_data) = fetch_data()

    print("Starting database update...")
    update_stock_db(company_stock_data, headlines_data) 
    # verify_db_contents()
    
if __name__ == "__main__":
    main()
    
    
 
  
    
