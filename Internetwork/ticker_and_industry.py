import requests
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf

def get_sp500_tickers():
    """
    Scrapes Wikipedia for the current list of S&P 500 tickers.
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})

    tickers = []

    for row in table.findAll('tr')[1:]:
        cols = row.findAll('td')
        ticker = cols[0].text.strip()
        tickers.append(ticker)
    
    return tickers

def get_industry_for_ticker(ticker):
    """
    Uses Yahoo Finance to get industry info for a given ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('industry', 'N/A')
    except Exception:
        return 'N/A'

def main():
    tickers = get_sp500_tickers()
    data = []

    print("Fetching industry info from Yahoo Finance (this may take a while)...")

    for ticker in tickers:
        industry = get_industry_for_ticker(ticker)
        print(f"{ticker}: {industry}")
        data.append({
            'Label': ticker,
            'Industry': industry
        })

    df = pd.DataFrame(data)
    df.to_csv('sp500_label_industry.csv', index=False)
    print("✅ Data saved to 'sp500_label_industry.csv'")

if __name__ == "__main__":
    main()
