#
#  Example Usage:
# python prepare_edges.py \
#   --network ./frontend/public/data/2017/2017_Network.csv \
#   --top ./frontend/public/data/2017/Top100_2017.csv \
#   --output ./frontend/public/data/2017/edgesBtwTop100_2017.csv
#

import csv
import argparse

def load_top100_tickers(top_file):
    """Load tickers from Top100_2017.csv into a set"""
    with open(top_file, 'r') as f:
        return set(line.strip().upper() for line in f if line.strip())


def extract_edges(network_file, top_tickers, output_file):
    """Extract edges between top 100 tickers and write to CSV"""
    with open(network_file, newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=["Source", "Target", "Weight"])
        writer.writeheader()

        count = 0
        for row in reader:
            source = row['firma'].strip().upper()
            target = row['firmb'].strip().upper()
            weight = int(row['numconnections'])

            if source in top_tickers and target in top_tickers:
                writer.writerow({"Source": source, "Target": target, "Weight": weight})
                count += 1

    print(f"✅ Saved {count} edges to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Filter and export edges between Top 100 tickers to CSV.")
    parser.add_argument('--network', required=True, help='Path to 2017_Network.csv')
    parser.add_argument('--top', required=True, help='Path to Top100_2017.csv')
    parser.add_argument('--output', required=True, help='Output CSV file (e.g., edgesBtwTop100_2017.csv)')

    args = parser.parse_args()

    top_tickers = load_top100_tickers(args.top)
    extract_edges(args.network, top_tickers, args.output)


if __name__ == "__main__":
    main()
