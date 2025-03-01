import os
import sqlite3
import requests
import pandas as pd 
from dotenv import load_dotenv
from tabulate import tabulate
from bs4 import BeautifulSoup

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Dict of companies to track Key: Company Name, Value: Stock market Symbol
COMPANIES = {
    "Nvidia": "NVDA",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Alphabet": "GOOGL"
}


def fetch_stock_data(symbol):
    # Fetches daily stock data for a given company symbol from Alpha Vantage api
    
    # Alpha Vantage API URL
    BASE_URL = "https://www.alphavantage.co/query"
    
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Global Quote" not in data:
        print(f"Error fetching data for {symbol}: {data}")
        return None
    
    print()
    print((data["Global Quote"]))
    return data["Global Quote"]



def get_yahoo_headlines(companies):
    """
    For each company in the companies dictionary, scrape Yahoo Finance for the latest headline.
    
    Parameters:
        companies (dict): A dictionary with company names as keys and their stock symbols as values.
    
    Returns:
        dict: A dictionary with company names as keys and the top headline for that company as values.
    """
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/115.0.0.0 Safari/537.36')
    }
    company_headlines = {}
    
    for company, symbol in companies.items():
        # Yahoo Finance URL for the company's news page
        # url = f"https://finance.yahoo.com/quote/{symbol}/news?p={symbol}"
        # url = f"https://search.yahoo.com/search?p={symbol}&fr=yfp-t&fr2=p%3Afp%2Cm%3Asb&ei=UTF-8&fp=1"
        url= f"https://search.yahoo.com/search;_ylt=AwrEtespXrtnjPQMAQRXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Fydw--?ei=UTF-8&fp=1&p={symbol}&norw=1&fr=yfp-t"
        #  Auto cirrect was changeing the search term
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            headlines[company] = f"Error retrieving data: {e}"
            continue
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
          # Find the span with inner HTML "Top Stories"
        top_stories_span = soup.find('span', string="Top Stories")
        headlines = [title.get_text(strip=True) for title in soup.select("div.title.u-trunc3 span.s-title")]
        
        # if top_stories_span:
        #     # Find the grandparent div of the span
        #     grandparent_div = top_stories_span.find_parent('div').find_parent('div')
            
        #     # Find the sibling of the grandparent div
        #     sibling_element = grandparent_div.find_next_sibling()
            
        #     # Find all articles within the sibling element
        #     articles = sibling_element.find_all('article')
        #     headlines = [title.get_text(strip=True) for title in soup.select("div.title.u-trunc3 span.s-title")]
            
            # for article in articles:
            #     print(f"Article found for {company}: {article}")
            # for headline in headlines:
            #     print(f"{company}: {headline}")
            
            
            
        # else:
        #     print(f"'Top Stories' span not found for {company}")
        company_headlines[company] = headlines
    
    return company_headlines




def verify_db_contents(db_file='stocks.db'):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT * FROM stocks")
    rows = cur.fetchall()
    print("\nDatabase contents:")
    for row in rows:
        print(row)
    conn.close()

def update_stock_db(stock_list, db_file='stocks.db'):
    # Connect to the SQLite database (or create it if it doesn't exist)
    print(f"\nConnecting to database: {db_file}")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    # // composite UNIQUE constraint that combines both the company and latest_trading_day
    
    # Create the table if it doesn't exist.
    print("Creating/verifying table structure...")
    cur.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            symbol TEXT,
            open TEXT,
            high TEXT,
            low TEXT,
            price TEXT,
            volume TEXT,
            latest_trading_day TEXT,
            previous_close TEXT,
            change TEXT,
            change_percent TEXT,
            UNIQUE(company, latest_trading_day)
        );
    ''')
    
    # Iterate through the list of stock data
    for item in stock_list:
        for company, data in item.items():
            print(f"\nProcessing data for company: {company}")
            # Initialize the row data with the company name.
            row_data = {'company': company}
            
            # Process the inner dictionary keys.
            # Example: '01. symbol' -> 'symbol'
            for key, value in data.items():
                # Strip the first 4 characters and any extra whitespace
                new_key = key[4:].strip()
                # Optionally, replace spaces with underscores so they match the table column names
                new_key = new_key.replace(" ", "_")
                row_data[new_key] = value
            
            # Define the expected columns in the table.
            columns = [
                'company', 'symbol', 'open', 'high', 'low', 
                'price', 'volume', 'latest_trading_day', 
                'previous_close', 'change', 'change_percent'
            ]
            # Extract the values in the order of the columns.
            values = [row_data.get(col) for col in columns]
            
            # INSERT OR REPLACE statement to handle unique constraint conflicts
            placeholders = ", ".join("?" for _ in columns)
            update_cols = ", ".join(f"{col}=excluded.{col}" for col in columns if col not in ['company', 'latest_trading_day'])
            sql = f"""
                INSERT INTO stocks ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT(company, latest_trading_day) 
                DO UPDATE SET {update_cols}
            """
            
            try:
                # Execute the SQL command.
                cur.execute(sql, values)
                print(f"Successfully inserted/updated data for {company}")
            except sqlite3.Error as e:
                print(f"Error with database operation for {company}: {e}")
    
    # Commit the changes and close the connection.
    conn.commit()
    conn.close()
    print("\nDatabase operations completed.")

def main():
    all_stock_data = []

    # for company, symbol in COMPANIES.items():
    #     print(f"Fetching data for {company} symbol:({symbol})...")
    #     stock_data = fetch_stock_data(symbol)

    #     if stock_data:
    #         all_stock_data.append({company: stock_data})
    
    all_stock_data = [{
        'Nvidia': {'01. symbol': 'NVDA', '02. open': '118.0200', '03. high': '125.0900', '04. low': '116.4000', '05. price': '124.9200', '06. volume': '389091145', '07. latest trading day': '2025-02-28', '08. previous close': '120.1500', '09. change': '4.7700', '10. change percent': '3.9700%'},
        'Microsoft': {'01. symbol': 'MSFT', '02. open': '392.6550', '03. high': '397.6300', '04. low': '386.5700', '05. price': '396.9900', '06. volume': '32845658', '07. latest trading day': '2025-02-28', '08. previous close': '392.5300', '09. change': '4.4600', '10. change percent': '1.1362%'},
        'Tesla': {'01. symbol': 'TSLA', '02. open': '279.5000', '03. high': '293.8800', '04. low': '273.6000', '05. price': '292.9800', '06. volume': '115696968', '07. latest trading day': '2025-02-28', '08. previous close': '281.9500', '09. change': '11.0300', '10. change percent': '3.9120%'},
        'Alphabet': {'01. symbol': 'GOOGL', '02. open': '168.6800', '03. high': '170.6100', '04. low': '166.7700', '05. price': '170.2800', '06. volume': '48130565', '07. latest trading day': '2025-02-28', '08. previous close': '168.5000', '09. change': '1.7800', '10. change percent': '1.0564%'}
        }]
    
    print("Starting database update...")
    update_stock_db(all_stock_data)
    verify_db_contents()
    
    # news_headlines = get_yahoo_headlines(COMPANIES)
    # print(news_headlines)
    # for company, headline in news_headlines.items():
    #     print(f"{company}: {headline}")
    
#    company_headlines = get_yahoo_headlines(COMPANIES)
   
#    for company, headlines in company_headlines.items():
#        for headline in headlines:
#            print(f"{headline}")

if __name__ == "__main__":
    main()
    
    

  
    
