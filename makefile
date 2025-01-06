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

.PHONY: clean import wrangle-edge-data get-citation-works wrangle-timeseries

clean:
	rm -rf docs/.observablehq/cache

# get all works of target authors from openAlex
import: # output: f"{author_id}.parquet"
	python $(IMPORT_DIR)/get_author_dat_oa.py -a $(author_id) -o $(DATA_DIR)

get-citation-works: # output: f"{author_id}_timeseries.parquet"
	python $(IMPORT_DIR)/incoming_citations.py -a $(author_id) -o $(DATA_DIR_CIT_WORKS)

wrangle-edge-data: # output: f"{author_id}_topic_net.parquet"
	python $(PREPRO_DIR)/get_edge_data.py -a $(author_id) -o $(DATA_DIR)

# Other works ➞ Author work
# https://docs.openalex.org/api-entities/works/filter-works#cites
wrangle-timeseries: # output: f"{author_id}_timeseries.parquet"
	python $(PREPRO_DIR)/timeseries_citations.py -a $(author_id) -o $(DATA_DIR)