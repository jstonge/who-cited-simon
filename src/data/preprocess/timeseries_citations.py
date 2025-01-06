"""Wrangle timeseries citations data: papers citing target authors work, by year"""

import pandas as pd
from collections import Counter
import json
from pathlib import Path
import argparse

def get_counts(df, tot_count, field='topic'):
    if field == 'topic':
        count = Counter(df.primary_topic.map(lambda x: x['display_name'] if x is not None else None))
    else:
        # field='field'
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
    # input_dir = input_dir / args.author
    # output_dir = Path("src/data")
    author_id = args.author
    input_dir = Path("src/data/incoming_citations").joinpath(author_id)
    output_dir = args.output
    
    fnames = input_dir.glob("*parquet")
    df = pd.concat([pd.read_parquet(fname) for fname in fnames], axis=0)

    df['field'] = df.primary_topic.map(lambda x: x['field']['display_name'] if x is not None else None)
    df['subfield'] = df.primary_topic.map(lambda x: x['subfield']['display_name'] if x is not None else None)
    df['domain'] = df.primary_topic.map(lambda x: x['domain']['display_name'] if x is not None else None)
    df['primary_topic'] = df.primary_topic.map(lambda x: x['display_name'] if x is not None else None)
        
    # Select the columns for counting
    fields_to_count = ['field', 'subfield', 'domain', 'primary_topic']

    # Create a list to store the results
    long_df_list = []

    # Iterate through each field and calculate counts
    for field in fields_to_count:
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
    long_df.to_parquet(output_dir / f"{author_id}_timeseries.parquet")

if __name__ == "__main__":
    main()