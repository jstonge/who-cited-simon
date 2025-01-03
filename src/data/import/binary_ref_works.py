import pandas as pd
from tqdm import tqdm
from pathlib import Path
import argparse

def parse_args():
    parser = argparse.ArgumentParser("Data Downloader")
    parser.add_argument(
        "-i", "--input", type=Path, help="output directory", required=True
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="output directory", required=True
    )
    return parser.parse_args()

def main():  
    args=parse_args()      
    
    # input_dir = Path('../../data')
    input_dir = args.input
    # output_dir = Path('../../docs/data/')
    output_dir = args.output
    
    outward_prop = []    
    for file in tqdm(input_dir.glob("*")):
        # break
        if file.stem.startswith("t") and file.suffix == '.parquet':
            df = pd.read_parquet(file)
            topic = df.primary_topic.iloc[0]['display_name']
            df = df[df.language == 'en']
            all_topic_ids = set(df.id)

            for year in sorted(df.publication_year.unique()):
                # break
                df_year = df[df.publication_year == year]
                referenced_works_yr = df_year['referenced_works'].explode().dropna()
                nb_inward_ref_works = len([_ for _ in referenced_works_yr if _ in all_topic_ids])
                tot_ref_works_yr = len(referenced_works_yr)
                if tot_ref_works_yr == 0 or nb_inward_ref_works == 0:
                    outward_prop_yr = None
                else:
                    outward_prop_yr = 1 - (nb_inward_ref_works / tot_ref_works_yr)
                
                outward_prop.append((topic,year,outward_prop_yr,nb_inward_ref_works,tot_ref_works_yr,len(df_year)))

    pd.DataFrame(outward_prop, columns=['topic', 'year','outward_prop', 'nb_inward_ref_works','tot_ref_works_yr','tot_works'])\
      .to_parquet(output_dir / f"inwards_refs_binary_ts.parquet")
                


if __name__ == "__main__":
    main()
