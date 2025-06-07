import pandas as pd
import sys

def filter_edges_by_source_and_target_id(edges_file, top50_file, output_file):
    try:
        # Load Top 50 tickers from 'ID' column
        top50_df = pd.read_csv(top50_file)
        top50_ids = top50_df['ID'].astype(str).tolist()

        # Load edges file
        edges_df = pd.read_csv(edges_file)

        # Filter rows: keep only if both Source AND Target are in the Top 50 IDs
        filtered_df = edges_df[
            edges_df['Source'].isin(top50_ids) & edges_df['Target'].isin(top50_ids)
        ]

        # Save filtered result
        filtered_df.to_csv(output_file, index=False)
        print(f"✅ Output saved to: {output_file}")
        print(f"🔢 Kept {len(filtered_df)} of {len(edges_df)} rows.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("\nUsage:")
        print("  python filter_edges_by_source_and_target_id.py <edges_file.csv> <top50_file.csv> <output_file.csv>\n")
        sys.exit(1)

    edges_file = sys.argv[1]
    top50_file = sys.argv[2]
    output_file = sys.argv[3]

    filter_edges_by_source_and_target_id(edges_file, top50_file, output_file)
