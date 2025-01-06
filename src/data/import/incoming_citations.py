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
    # min_year = df.publication_year.min()

    # for each paper
    tot_articles = len(df)
    for i,row in df.iterrows():
        
        # get all works that cite this paper
        citing_works = []
        ws = Works().filter(cites=row.id)
        for w in chain(*ws.paginate(per_page=200)):
            citing_works.append(w)
        
        # for each citing work, save the details
        # in
        for citing_work in citing_works:
            # citing_work=citing_works[1]
            # year_cited = 1947
            year_cited = citing_work.get('publication_year')
            
            yearly_out_dir = output_dir / str(year_cited)
            yearly_out_dir.mkdir(exist_ok=True)
            
            author_year_f = yearly_out_dir / f"{row.id.split('/')[-1]}.json"
            # author_year_f = yearly_out_dir / f"W1983591280.json"
            
            if author_year_f.exists():
                current_data = json.load(open(author_year_f))
                if isinstance(current_data, dict):
                    print(f"{row.id} is a dict. Deleting")
                    author_year_f.unlink()
                    current_data = []
                
                # We check if the citing work is already in the list
                # citing_work = Works()['W1983591280']
                done_ids = set([w['id'] for w in current_data])
                if citing_work.get('id') not in done_ids:
                    current_data.append(citing_work)
                    with open(author_year_f, "w") as f:
                        json.dump(current_data, f)

                else:
                    print(f"{citing_work.get('id')} already done")
            else:
                with open(author_year_f, "w") as f:
                    json.dump([citing_work], f)
                


        print(f"Processing {i+1}/{tot_articles}")
        

if __name__ == "__main__":
    main()
