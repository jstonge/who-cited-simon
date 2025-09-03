#!/usr/bin/myenv python3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import sys


df = pd.read_parquet("./5108357701_timeseries.parquet")

# Write DataFrame to a temporary file-like object
buf = pa.BufferOutputStream()
table = pa.Table.from_pandas(df)
pq.write_table(table, buf, compression="snappy")

# Get the buffer as a bytes object
buf_bytes = buf.getvalue().to_pybytes()

# Write the bytes to standard output
sys.stdout.buffer.write(buf_bytes)