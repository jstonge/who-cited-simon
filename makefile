# project also contains:
#  - publish.yml to push with github action
#  - requirements.txt to install python dependencies (venv recommended)
#  - index.md is the code for the observable framework data app

DATA_DIR=./src/data
DATA_DIR_BY_YEAR=$(DATA_DIR)/by_year
DATA_DIR_REF_WORKS=$(DATA_DIR)/ref_works_by_year
DATA_DIR_CIT_WORKS=$(DATA_DIR)/citations_by_year

######################
#                    #
#       SCRIPTS      #
#                    #
######################

.PHONY: ref-works-binary clean import get-ref-works concat preprocess


clean:
	rm -rf docs/.observablehq/cache

# get all works of target authors from openAlex
import:
	python $(DATA_DIR)/get_author_dat_oa.py -a $(author_id) -o $(DATA_DIR_BY_YEAR)
	python -c "import pandas as pd; from pathlib import Path; pd.concat([pd.read_parquet(_) for _ in Path('data/by_year/$(author_id)').glob('*')], axis=0).to_parquet('data/$(author_id).parquet')"

# Author work ➞ Other works
# https://docs.openalex.org/api-entities/works/work-object#referenced_works
get-ref-works:
	python $(DATA_DIR)/import/referenced_works.py -a $(author_id) -o $(DATA_DIR_REF_WORKS)
	python $(DATA_DIR)/preprocess/inwards.py -a $(author_id) -o $(DATA_DIR_REF_WORKS)

# Other works ➞ Author work
# https://docs.openalex.org/api-entities/works/filter-works#cites
get-citation-works: # output: timeseries.parquet
	python $(DATA_DIR)/import/referenced_works.py -a $(author_id) -o $(DATA_DIR_CIT_WORKS)
	python $(DATA_DIR)/preprocess/inwards.py -a $(author_id) -o $(DATA_DIR_CIT_WORKS)

# utility to concat data
concat: # output: f"{author_id}.parquet") (raw data of target author)
	python -c "import pandas as pd; from pathlib import Path; pd.concat([pd.read_parquet(_) for _ in Path('data/by_year/$(author_id)').glob('*')], axis=0).to_parquet('data/$(author_id).parquet')"

preprocess: # output: f"{author_id}_clean.parquet")
	python $(DATA_DIR)/preprocess/preprocess.py -a $(author_id) -o $(DATA_DIR)
