# project also contains:
#  - publish.yml to push with github action
#  - requirements.txt to install python dependencies (venv recommended)
#  - index.md is the code for the observable framework data app

DATA_DIR=./src/data
IMPORT_DIR=$(DATA_DIR)/import
PREPRO_DIR=$(DATA_DIR)/preprocess
DATA_DIR_CIT_WORKS=$(DATA_DIR)/incoming_citations

######################
#                    #
#       SCRIPTS      #
#                    #
######################

.PHONY: clean import wrangle-edge-data get-ref-works get-citation-works concat

clean:
	rm -rf docs/.observablehq/cache

# get all works of target authors from openAlex
import:
	python $(IMPORT_DIR)/get_author_dat_oa.py -a $(author_id) -o $(DATA_DIR)

wrangle-edge-data: # output: f"{author_id}_topic_net.parquet")
	python $(PREPRO_DIR)/get_edge_data.py -a $(author_id) -o $(DATA_DIR)

# Other works ➞ Author work
# `incoming citations.py` creates a dir of the same name, with author id as subdir.
# Within subdir, for each year, we get JSON lines of target author works, with incoming citations, e.g.
# 1945/W2124317547 is a list of works citing that paper (W2124317547) in 1945..
# https://docs.openalex.org/api-entities/works/filter-works#cites
get-citation-works: # output: timeseries.parquet
	python $(IMPORT_DIR)/incoming_citations.py -a $(author_id) -o $(DATA_DIR_CIT_WORKS)

# python $(PREPRO_DIR)/timeseries_citations.py -a $(author_id) -o $(DATA_DIR)