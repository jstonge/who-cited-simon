from itertools import chain
import pandas as pd
from pyalex import Works
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-a", "--author", type=str, help="output directory", required=True
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="output directory", required=True
    )
    return parser.parse_args()

def main():
    args=parse_args()
    output = args.output
    author_id = args.author
    output.mkdir(exist_ok=True)
    
    ws = Works().filter(authorships={'author.id': author_id})
    out = []
    for w in chain(*ws.paginate(per_page=200)):
        out.append(w)
    
    df = pd.DataFrame(out)
    df.primary_topic = df.primary_topic.map(lambda x: x['display_name'] if x is not None else None)
    cols2keep = ['id', 'doi', 'title', 'publication_year', 'primary_topic', 'topics', 'display_name', 'authorships', 'cited_by_count', 'keywords', 'grants']
    df = df[cols2keep]
    df = df[df.publication_year > 1937]
    df.to_parquet(output / f"{author_id}.parquet")

if __name__ == "__main__":
    main()
