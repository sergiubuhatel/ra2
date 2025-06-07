import pandas as pd
import yfinance as yf
import argparse

def get_industry_for_ticker(ticker):
    """
    Uses Yahoo Finance to get industry info for a given ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('industry', 'Unclassified')
    except Exception:
        return 'N/A'

def main():
    parser = argparse.ArgumentParser(description='Fetch industry info for tickers from input CSV.')
    parser.add_argument('input_file', help='Input CSV file (no header, one column with ticker symbols)')
    parser.add_argument('output_file', help='Output CSV file with Label and Industry columns')
    args = parser.parse_args()

    try:
        tickers_df = pd.read_csv(args.input_file, header=None)
        tickers = tickers_df[0].tolist()
    except Exception as e:
        print(f"❌ Failed to read input file: {e}")
        return

    data = []

    print("Fetching industry info from Yahoo Finance...")

    for ticker in tickers:
        industry = get_industry_for_ticker(ticker)
        print(f"{ticker}: {industry}")
        data.append({
            'Label': ticker,
            'Industry': industry
        })

    df = pd.DataFrame(data)
    df.to_csv(args.output_file, index=False)
    print(f"✅ Data saved to '{args.output_file}'")

if __name__ == "__main__":
    main()
