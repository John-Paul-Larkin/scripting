import json
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



def get_yahoo_headlines(symbol):

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
    
    headlines_data = []
    for article in soup.select("div.title.u-trunc3"):
        headline = article.select_one("span.s-title").get_text(strip=True)
        url = article.find_parent('a', class_='bkgLink')['href']
        headlines_data.append({
            "headline": headline,
            "url": url
        })
    
    return headlines_data


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
    print(f"\nConnecting to database: {db_file}")
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    print("Creating stockstable...")
    cur.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            headlines TEXT,
            UNIQUE(symbol, latest_trading_day)
        );
    ''')
    
    for item in stock_list:
        company_data = item['company']
        headlines_data = item['headlines']

        # Convert headlines to json string
        headlines_str = json.dumps(headlines_data)
        
        # Initialize row_data with all the stock information
        row_data = {
            'symbol': company_data['01. symbol'],
            'open': company_data['02. open'],
            'high': company_data['03. high'],
            'low': company_data['04. low'],
            'price': company_data['05. price'],
            'volume': company_data['06. volume'],
            'latest_trading_day': company_data['07. latest trading day'],
            'previous_close': company_data['08. previous close'],
            'change': company_data['09. change'],
            'change_percent': company_data['10. change percent'],
            'headlines': headlines_str
        }
        
        # Debug print to see what we're trying to insert
        print("\nAttempting to insert data:")
        print(f"Symbol: {row_data['symbol']}")
        print(f"Latest Trading Day: {row_data['latest_trading_day']}")
        
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
            print(f"Successfully inserted/updated data for {row_data['symbol']}")
        except sqlite3.Error as e:
            print(f"Error with database operation: {e}")
            print("Values being inserted:", values)  # Debug print
    
    conn.commit()
    conn.close()
    print("\nDatabase operations completed.")

def write_stock_data_to_file(stock_data):
    with open('stock_data.txt', 'w') as f:
        f.write(str(stock_data))

def fetch_data():
    stock_data = []
    
    # for company, symbol in COMPANIES.items():
    #     print(f"Fetching data for {company} symbol:({symbol})...")
    #     stock_data = fetch_stock_data(symbol)
    #     headlines = get_yahoo_headlines(symbol)

    #     if stock_data and headlines:
    #         stock_data.append({'company': stock_data,'headlines': headlines})
    #     else:
    #         print(f"Error fetching data for {company} symbol:({symbol})")
    
    # write_stock_data_to_file(stock_data)
    
    stock_data = [
        {'company': {'01. symbol': 'NVDA', '02. open': '118.0200', '03. high': '125.0900', '04. low': '116.4000', '05. price': '124.9200', '06. volume': '389091145', '07. latest trading day': '2025-02-28', '08. previous close': '120.1500', '09. change': '4.7700', '10. change percent': '3.9700%'}, 'headlines': [{'headline': 'IsNVIDIACorporation (NVDA) The Best Money Making Stock To Buy Now?', 'url': 'https://r.search.yahoo.com/_ylt=AwrFY4hag8NnqlsF511XNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075995/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fnvidia-corporation-nvda-best-money-164657872.html%3ffr%3dsycsrp_catchall/RK=2/RS=2NuIv1L0xogfGvjhvPpZnB8RNHY-'}, {'headline': 'Jim Cramer onNVIDIACorporation (NVDA): ‘There Are People Who Think It’s Dramatically Overvalued. And I Don’t Get That’', 'url': 'https://r.search.yahoo.com/_ylt=AwrFY4hag8NnqlsF611XNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075995/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fjim-cramer-nvidia-corporation-nvda-080254921.html%3ffr%3dsycsrp_catchall/RK=2/RS=MyQtGG50XgAmAMlVStIDdwAxErs-'}, {'headline': 'Jim Cramer onNVIDIACorporation (NVDA): ‘While We Still Have To Worry About Tariffs And Export Restrictions, ...', 'url': 'https://r.search.yahoo.com/_ylt=AwrFY4hag8NnqlsF711XNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075995/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fjim-cramer-nvidia-corporation-nvda-121051471.html%3ffr%3dsycsrp_catchall/RK=2/RS=BqpBCXB10unLLCWkhdk4wfltdEg-'}]}, 
        {'company': {'01. symbol': 'MSFT', '02. open': '392.6550', '03. high': '397.6300', '04. low': '386.5700', '05. price': '396.9900', '06. volume': '32845658', '07. latest trading day': '2025-02-28', '08. previous close': '392.5300', '09. change': '4.4600', '10. change percent': '1.1362%'}, 'headlines': [{'headline': 'MicrosoftCorporation (MSFT): Among the Best Stocks to Buy According to Bill Gates', 'url': 'https://r.search.yahoo.com/_ylt=Awrigcpbg8NnaQIAt.JXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075996/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fmicrosoft-corporation-msft-among-best-191748014.html%3ffr%3dsycsrp_catchall/RK=2/RS=8IMqvDhkJfzxBc6aRZpat2Otpxs-'}, {'headline': 'MicrosoftCorporation (MSFT): A Bull Case Theory', 'url': 'https://r.search.yahoo.com/_ylt=Awrigcpbg8NnaQIAu.JXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075996/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fmicrosoft-corporation-msft-bull-case-174225857.html%3ffr%3dsycsrp_catchall/RK=2/RS=SzegkjY0j2VRSJvwC0IW4cYXpTc-'}, {'headline': 'Here’s WhyMicrosoft(MSFT) Stock Returned 13% in Q4', 'url': 'https://r.search.yahoo.com/_ylt=Awrigcpbg8NnaQIAv.JXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075996/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fwhy-microsoft-msft-stock-returned-142857739.html%3ffr%3dsycsrp_catchall/RK=2/RS=ed.VdiSOkch7IxrKTdWrg337CsE-'}]}, 
        {'company': {'01. symbol': 'TSLA', '02. open': '279.5000', '03. high': '293.8800', '04. low': '273.6000', '05. price': '292.9800', '06. volume': '115696968', '07. latest trading day': '2025-02-28', '08. previous close': '281.9500', '09. change': '11.0300', '10. change percent': '3.9120%'}, 'headlines': [{'headline': 'Jim Cramer onTesla, Inc. (TSLA) CEO Elon Musk: ‘There’s A Changeover That He’s Doing On The Autos’', 'url': 'https://r.search.yahoo.com/_ylt=AwrNOJ1dg8NnkkIA511XNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075998/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fjim-cramer-tesla-inc-tsla-074529126.html%3ffr%3dsycsrp_catchall/RK=2/RS=T9Nw43jj.yLidFC3tJFMFn22hM8-'}, {'headline': 'WhyTesla(TSLA) Is Retreating Today', 'url': 'https://r.search.yahoo.com/_ylt=AwrNOJ1dg8NnkkIA611XNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075998/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fwhy-tesla-tsla-retreating-today-180436956.html%3ffr%3dsycsrp_catchall/RK=2/RS=FbuNAEQdSixSlSJ8eWG3k0lZw_g-'}, {'headline': 'TeslaInc. (TSLA) Among The Best Manufacturing Stock To Buy Now', 'url': 'https://r.search.yahoo.com/_ylt=AwrNOJ1dg8NnkkIA711XNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075998/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2ftesla-inc-tsla-among-best-185232061.html%3ffr%3dsycsrp_catchall/RK=2/RS=vWAFsmjrQ_1SVfbAE_AvUYvR0NM-'}]}, 
        {'company': {'01. symbol': 'GOOGL', '02. open': '168.6800', '03. high': '170.6100', '04. low': '166.7700', '05. price': '170.2800', '06. volume': '48130565', '07. latest trading day': '2025-02-28', '08. previous close': '168.5000', '09. change': '1.7800', '10. change percent': '1.0564%'}, 'headlines': [{'headline': 'Alphabet (GOOGL) Reliance on International Sales: What Investors Need to Know', 'url': 'https://r.search.yahoo.com/_ylt=AwrFFtBeg8NnB0MA7zJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075999/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2falphabet-googl-reliance-international-sales-141527238.html%3ffr%3dsycsrp_catchall/RK=2/RS=z1dGZHys.H4_T_1XSE7mPWVvFZo-'}, {'headline': 'Alphabet (GOOGL) Ascends But Remains Behind Market: Some Facts to Note', 'url': 'https://r.search.yahoo.com/_ylt=AwrFFtBeg8NnB0MA8zJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzIEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075999/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2falphabet-googl-ascends-remains-behind-224518632.html%3ffr%3dsycsrp_catchall/RK=2/RS=2bJpcm9E9K10WrK4mkFqGWv1oRs-'}, {'headline': "CanGOOGL's Cloud Investments Push the Stock Higher in 2025?", 'url': 'https://r.search.yahoo.com/_ylt=AwrFFtBeg8NnB0MA_DJXNyoA;_ylu=Y29sbwNiZjEEcG9zAzMEdnRpZAMEc2VjA3Nj/RV=2/RE=1742075999/RO=10/RU=https%3a%2f%2ffinance.yahoo.com%2fnews%2fgoogls-cloud-investments-push-stock-161300162.html%3ffr%3dsycsrp_catchall/RK=2/RS=LVhl3GVVorLa3cV.ClJhwjgmkDg-'}]}]

    return stock_data

def main():
    stock_data = fetch_data()

    print("Starting database update...")
    update_stock_db(stock_data) 
    # verify_db_contents()
    
if __name__ == "__main__":
    main()
    
    

  
    
