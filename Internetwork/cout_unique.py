import pandas as pd
import sys

def count_unique_sources(file_path):
    try:
        # Load the CSV
        df = pd.read_csv(file_path)

        # Count unique Source values
        unique_sources = df['Source'].nunique()

        print(f"🔢 Number of distinct Source entries: {unique_sources}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nUsage:")
        print("  python count_sources.py <csv_file>\n")
        sys.exit(1)

    csv_file = sys.argv[1]
    count_unique_sources(csv_file)
