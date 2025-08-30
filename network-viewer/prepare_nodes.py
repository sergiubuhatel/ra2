#
# Example Usage:
#
# python prepare_nodes.py 
#   --industries ./frontend/public/data/2017/2017_industries.csv 
#   --top ./frontend/public/data/2017/Top100_2017.csv 
#   --output ./frontend/public/data/2017/Top100_tickers.csv
#

import csv
import argparse

# ff_48 → short industry code mapping
ff48_to_shortname = {
    1: 'Agric', 2: 'Food', 3: 'Soda', 4: 'Beer', 5: 'Smoke', 6: 'Toys', 7: 'Fun',
    8: 'Books', 9: 'Hshld', 10: 'Clths', 11: 'Hlth', 12: 'MedEq', 13: 'Drugs',
    14: 'Chems', 15: 'Rubbr', 16: 'Txtls', 17: 'BldMt', 18: 'Cnstr', 19: 'Steel',
    20: 'FabPr', 21: 'Mach', 22: 'ElcEq', 23: 'Autos', 24: 'Aero', 25: 'Ships',
    26: 'Guns', 27: 'Gold', 28: 'Mines', 29: 'Coal', 30: 'Oil', 31: 'Util',
    32: 'Telcm', 33: 'PerSv', 34: 'BusSv', 35: 'Comps', 36: 'Chips', 37: 'LabEq',
    38: 'Paper', 39: 'Boxes', 40: 'Trans', 41: 'Whlsl', 42: 'Rtail', 43: 'Meals',
    44: 'Banks', 45: 'Insur', 46: 'RlEst', 47: 'Fin', 48: 'Other'
}

def main(industries_file, top_file, output_file):
    # Step 1: Load industry mapping
    industry_map = {}
    with open(industries_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ticker = row['ticker'].strip()
            ff_48 = row['ff_48'].strip()
            industry_map[ticker] = int(ff_48) if ff_48 else None

    # Step 2: Read top tickers and map to short industry name
    output_rows = []
    with open(top_file, newline='') as file:
        for line in file:
            ticker = line.strip()
            ff_48 = industry_map.get(ticker)
            industry_short = ff48_to_shortname.get(ff_48, 'Unclassified')
            output_rows.append({'ID': ticker, 'Label': ticker, 'Industry': industry_short})

    # Step 3: Write to output CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['ID', 'Label', 'Industry'])
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"✅ Saved: {output_file} with short industry codes.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map tickers to short industry codes.")
    parser.add_argument("--industries", required=True, help="Input CSV file with industry codes (e.g., 2017_industries.csv)")
    parser.add_argument("--top", required=True, help="Input text file with top tickers (one ticker per line)")
    parser.add_argument("--output", required=True, help="Output CSV file for tickers with industry codes")

    args = parser.parse_args()
    main(args.industries, args.top, args.output)
