import requests
import pandas as pd
from bs4 import BeautifulSoup
import yfinance as yf

def get_sp500_tickers():
    """
    Scrapes Wikipedia for the current list of S&P 500 tickers and company names.
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})

    tickers = []
    companies = []

    for row in table.findAll('tr')[1:]:
        cols = row.findAll('td')
        ticker = cols[0].text.strip()
        company = cols[1].text.strip()
        tickers.append(ticker)
        companies.append(company)
    
    return tickers, companies

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
    tickers, companies = get_sp500_tickers()
    data = []

    print("Fetching industry info from Yahoo Finance (this may take a minute)...")

    for ticker, company in zip(tickers, companies):
        industry = get_industry_for_ticker(ticker)
        print(f"{ticker}: {industry}")
        data.append({
            'Ticker': ticker,
            'Company': company,
            'Industry': industry
        })

    df = pd.DataFrame(data)
    df.to_csv('sp500_tickers_and_industries.csv', index=False)
    print("✅ Data saved to 'sp500_tickers_and_industries.csv'")

if __name__ == "__main__":
    main()
