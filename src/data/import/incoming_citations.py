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

    # author_id = 'a5108357701'
    input_dir = Path("src/data") 
    # output_dir = Path('data/citations_by_year')
    output_dir = args.output
    
    output_dir = output_dir / author_id
    output_dir.mkdir(exist_ok=True)

    # grab all articles by author
    df = pd.read_parquet(input_dir / f"{author_id}.parquet")
    df = df[~df.title.isna()]
    df.sort_values("publication_year", inplace=True)
    min_year = df.publication_year.min()

    # for each paper
    tot_articles = len(df)
    for i,row in df.iterrows():
        print(f"Processing {i+1}/{tot_articles}")
        
        for year in range(min_year, 2024):

            yearly_out_dir = output_dir / str(year)
            yearly_out_dir.mkdir(exist_ok=True)
            
            # if the paper was published before the year we are looking at
            if year >= row.publication_year:

                out_f = yearly_out_dir / f"{row.id.split('/')[-1]}.json"
                    
                # check if already done. 
                if out_f.exists():
                    print(f"Skip id {row.id}")
                    continue

                # get citing works for a given year (works that cite this work paper)
                ws = Works().filter(cites=row.id,  publication_year=year)
                citing_works = []
                for w in chain(*ws.paginate(per_page=200)):
                    citing_works.append(w)
            
                if not citing_works:
                    out = {}
                else:
                    # get details of each referenced work
                    citing_works_details = []
                    for work in tqdm(citing_works, total=len(citing_works)):
                        
                        try:
                            details = Works()[work.get('id')]
                            citing_works_details.append(details)
                        except requests.exceptions.HTTPError:
                            print(f"Error fetching {work}")
                            continue
                    out = citing_works_details
                # save details of all referenced works, if cited
                if len(out) > 0:
                    with open(out_f, "w") as f:
                        json.dump(out, f)


if __name__ == "__main__":
    main()
