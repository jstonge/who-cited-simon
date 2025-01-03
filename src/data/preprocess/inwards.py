import pandas as pd
from collections import Counter
import json
from pathlib import Path
import argparse

def get_counts(x, tot_count, field='topic'):
    if field == 'topic':
        count = Counter([w['primary_topic']['display_name'] for w in x if w.get('primary_topic') is not None])
    else:
        count = Counter([w['primary_topic'][field]['display_name'] for w in x if w.get('primary_topic') is not None])
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
    input_dir = Path("data/ref_works_by_year")
    # input_dir = input_dir / 'a5108357701'
    input_dir = input_dir / args.author
    output_dir = args.output
    
    years = sorted([int(_.stem) for _ in input_dir.glob("*")])
    dfs = []
    for year in years:
        fnames = list(input_dir.joinpath(str(year)).glob("*json"))
        
        counts_topics = {}
        counts_subfields = {}
        counts_field = {}
        counts_domain = {}

        for fname in fnames:
            
            with open(fname) as f:
                out = json.load(f)
            
            if out is not None:
                counts = [counts_topics, counts_subfields, counts_field, counts_domain]
                fields  = ['topic', 'subfield', 'field', 'domain']
                [ get_counts(out, c, field=f) for c,f in zip(counts, fields) ]
                
        dfs.append(pd.concat([
            pd.DataFrame(counts_topics.items(), columns=['category', 'count']).assign(type='topic'),
            pd.DataFrame(counts_subfields.items(), columns=['category', 'count']).assign(type='subfield'),
            pd.DataFrame(counts_field.items(), columns=['category', 'count']).assign(type='field'),
            pd.DataFrame(counts_domain.items(), columns=['category', 'count']).assign(type='domain')
        ], axis=0).assign(year=year))

    pd.concat(dfs, axis=0).to_parquet(output_dir / "timeseries.parquet")

if __name__ == "__main__":
    main()