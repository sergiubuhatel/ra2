import pandas as pd
import sys

def fill_industry(reference_file, target_file, output_file):
    try:
        # Load the reference CSV (Label, Industry)
        ref_df = pd.read_csv(reference_file)

        # Load the target CSV (ID, Label, Industry)
        target_df = pd.read_csv(target_file)

        # Merge on the Label column
        merged_df = target_df.drop(columns=['Industry'], errors='ignore').merge(
            ref_df, on='Label', how='left'
        )

        # Save to output file
        merged_df.to_csv(output_file, index=False)
        print(f"✅ Output saved to {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python fill_industry_cli.py <reference_file.csv> <target_file.csv> <output_file.csv>")
        sys.exit(1)

    ref_file = sys.argv[1]
    target_file = sys.argv[2]
    out_file = sys.argv[3]

    fill_industry(ref_file, target_file, out_file)
