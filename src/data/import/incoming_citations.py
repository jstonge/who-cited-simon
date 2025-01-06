"""
Takes a list of articles by an author and 
gets all the works that cite those articles 
aka incoming citations.
"""
from itertools import chain
from tqdm import tqdm
import argparse
import requests
import json
from pathlib import Path
import pandas as pd
from pyalex import Works

def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-a", "--author", type=Path, help="output directory", required=True
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="output directory", required=True
    )
    return parser.parse_args()

def main():  
    """
    API Calls = #articles * #citations_per_article
    The output directory is year/author_paper_id:List[IncomingCitations]
    """
    args = parse_args()      
    author_id = args.author
    input_dir = Path("src/data") 
    output_dir = args.output.joinpath(author_id)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # grab all articles by author
    df = pd.read_parquet(input_dir / f"{author_id}.parquet")
    
    for i,row in tqdm(df.iterrows()):
        out_f =  output_dir / f"{row.id.split("/")[-1]}.parquet"

        if row.title is None or out_f.exists():
            continue

        # get all works that cite this paper
        citing_works = []
        ws = Works().filter(cites=row.id)
        for w in chain(*ws.paginate(per_page=200)):
            citing_works.append(w)

        df_citing_works = pd.DataFrame(citing_works)    
        df_citing_works.to_parquet(out_f)

if __name__ == "__main__":
    main()
