import csv
from typing import IO
import pandas as pd
import polars as pl

pd.set_option('display.max_colwidth', None)
pl.Config.set_fmt_str_lengths(900)
pl.Config.set_tbl_width_chars(900)


def standard_text_reader(file: IO[bytes]):
    pass


def pandas_reader(file: IO[bytes]):
    print(pd.read_csv(file, header='infer'))


def polars_reader(file: IO[bytes]):
    print(pl.read_csv(file, ))
