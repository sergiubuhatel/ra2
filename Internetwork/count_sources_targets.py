import pandas as pd
import sys

def count_unique_sources_and_targets(file_path):
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)

        # Count unique Source and Target values
        unique_sources = df['Source'].nunique()
        unique_targets = df['Target'].nunique()

        print(f"🔢 Distinct Source entries: {unique_sources}")
        print(f"🎯 Distinct Target entries: {unique_targets}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nUsage:")
        print("  python count_sources_targets.py <csv_file>\n")
        sys.exit(1)

    csv_file = sys.argv[1]
    count_unique_sources_and_targets(csv_file)
