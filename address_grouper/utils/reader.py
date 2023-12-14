from typing import IO
import pandas as pd
import polars as pl
from polars import DataFrame as polarsDataFrame
from pandas import DataFrame as pandasDataFrame

from .helpers import get_runtime

pd.set_option('display.max_colwidth', None)
pl.Config.set_fmt_str_lengths(900)
pl.Config.set_tbl_width_chars(900)


@get_runtime
def standard_text_reader(file: IO[bytes]):
    addresses = {}
    for row in file:
        line = row.decode('utf-8')
        x_idx = line.find(',')
        person, address = line[:x_idx], line[x_idx + 1:]
        if address not in addresses:
            addresses[address] = []
        addresses[address].append(person)

    print(addresses)
    # sorted_addresses = sorted(addresses.items(), key=lambda x: [x[0], x[1]])
    #
    # print(sorted_addresses)


@get_runtime
def pandas_reader(file: IO[bytes]) -> pandasDataFrame:
    df = pd.read_csv(file, header='infer')
    return df


@get_runtime
def polars_reader(file: IO[bytes]) -> polarsDataFrame:
    return pl.read_csv(file)
