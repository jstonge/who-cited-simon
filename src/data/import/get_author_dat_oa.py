from itertools import chain
import pandas as pd
from pyalex import Works
import argparse
from pathlib import Path
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-t", "--author", type=str, help="output directory", required=True
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="output directory", required=True
    )
    return parser.parse_args()

def get_dat_from_oa(author_id: str, year: int) -> pd.DataFrame:
    ws = Works().filter(authorships={'author.id': author_id}, publication_year=year)
    out = []
    for w in chain(*ws.paginate(per_page=200)):
        out.append(w)
    return pd.DataFrame(out)

def main():
    args=parse_args()
    output = args.output / args.author
    # author_id = 'a5108357701' #Simon
    # output = Path('data') / 'by_year'
    author_id = args.author
    
    if output.exists() == False:
        output.mkdir()
        
    for year in tqdm(range(1940, 2024)):
        # year = 1994
        out_f = output / f"{author_id}_{year}.parquet"
        if out_f.exists():
            continue
        
        df_stat = get_dat_from_oa(author_id, year)
        df_stat.to_parquet(out_f)

if __name__ == "__main__":
    main()
