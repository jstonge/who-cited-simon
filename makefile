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

ref-works-binary: 
	python $(DATA_DIR)/import/import.py -a $(author_id) -o $(DATA_DIR_BY_YEAR)
	python -c "import pandas as pd; from pathlib import Path; pd.concat([pd.read_parquet(_) for _ in Path('data/by_year/$(author_id)').glob('*')], axis=0).to_parquet('data/$(author_id).parquet')"
	python $(DATA_DIR)/import/binary_ref_works.py -i $(DATA_DIR) -o $(DATA_DIR_OBS)

clean:
	rm -rf docs/.observablehq/cache

import:
	python $(DATA_DIR)/import.py -a $(author_id) -o $(DATA_DIR_BY_YEAR)
	python -c "import pandas as pd; from pathlib import Path; pd.concat([pd.read_parquet(_) for _ in Path('data/by_year/$(author_id)').glob('*')], axis=0).to_parquet('data/$(author_id).parquet')"

get-ref-works:
	python $(DATA_DIR)/import/referenced_works.py -a $(author_id) -o $(DATA_DIR_REF_WORKS)
	python $(DATA_DIR)/preprocess/inwards.py -a $(author_id) -o $(DATA_DIR_REF_WORKS)

get-citation-works:
	python $(DATA_DIR)/import/referenced_works.py -a $(author_id) -o $(DATA_DIR_CIT_WORKS)
	python $(DATA_DIR)/preprocess/inwards.py -a $(author_id) -o $(DATA_DIR_CIT_WORKS)

concat:
	python -c "import pandas as pd; from pathlib import Path; pd.concat([pd.read_parquet(_) for _ in Path('data/by_year/$(author_id)').glob('*')], axis=0).to_parquet('data/$(author_id).parquet')"

preprocess:
	python $(DATA_DIR)/preprocess/preprocess.py -a $(author_id) -o $(DATA_DIR)
