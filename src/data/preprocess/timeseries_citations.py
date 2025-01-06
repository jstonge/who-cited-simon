"""Wrangle timeseries citations data: papers citing target authors work, by year"""
import pandas as pd
from collections import Counter
from pathlib import Path
import argparse
from tqdm import tqdm

def get_counts(df, tot_count, field='topic'):
    if field == 'topic':
        count = Counter(df.primary_topic.map(lambda x: x['display_name'] if x is not None else None))
    else:
        count = Counter(df.primary_topic.map(lambda x: x[field]['display_name'] if x is not None else None))
    for k in count.keys():
        tot_count[k] = tot_count.get(k, 0) + count[k]  

def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-a", "--author", type=str, help="author id", required=True
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="output directory", required=True
    )
    return parser.parse_args()

def main():
    args = parse_args()
    # author_id = 'a5108357701'
    # output_dir = Path("src/data")
    author_id = args.author
    input_dir = Path("src/data/incoming_citations").joinpath(author_id)
    output_dir = args.output
    fnames = input_dir.glob("*parquet")
    
    #!TODO: could probably be much better. Make sure this is doing what you think it is doing. Output is dubious
    long_df_list = []
    for fname in tqdm(fnames):
        df = pd.read_parquet(fname)

        if df.empty:
            continue

        # Select the columns for counting
        fields_to_count = ['field', 'subfield', 'domain', 'primary_topic']

        # Iterate through each field and calculate counts
        for field in fields_to_count:
            if field == 'primary_topic':
                df[field] = df.primary_topic.map(lambda x: x['display_name'] if x is not None else None)
            else:
                df[field] = df.primary_topic.map(lambda x: x[field]['display_name'] if x is not None else None)
            
            temp = (
                df.groupby(['publication_year', field])
                .size()
                .reset_index(name='count')  # Create a column named 'count'
                .rename(columns={field: 'category'})  # Rename the field column to 'category'
            )
            temp['type'] = field  # Add a column to indicate the type of category
            long_df_list.append(temp)  # Append to the list

    # Combine all the counts into a single DataFrame
    long_df = pd.concat(long_df_list, ignore_index=True)
    long_df = long_df.groupby(['publication_year', 'category', 'type']).sum().reset_index()
    long_df.to_parquet(output_dir / f"{author_id}_timeseries.parquet")

if __name__ == "__main__":
    main()