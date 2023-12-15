from typing import IO
import pandas as pd
import polars as pl
import functools
import operator

from .helpers import get_runtime, get_base_addresses, fuzzy_compare, translate_address, create_address_lower, \
    sort_and_format_names

from pandas_schema import Column, Schema
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 200)
pl.Config.set_fmt_str_lengths(900)
pl.Config.set_tbl_width_chars(900)

import time
import datetime


@get_runtime
def pandas_reader(file: IO[bytes]) -> str:
    started = time.time()
    schema = Schema([
        Column('Name', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]),
        Column('Address', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]),
    ])

    df = pd.read_csv(file, header='infer').drop_duplicates()
    errors = schema.validate(df)
    if errors:
        return '\n'.join([str(i) for i in errors])

    print(f"Dataframe created: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    df['Address'] = df['Address'].apply(lambda x: translate_address(x))
    print(f"Addressed translated: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    df['AddressLower'] = df['Address'].apply(create_address_lower)
    print(f"Lower created: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    df['closest_approximate_match'] = df['AddressLower'].apply(fuzzy_compare,
                                                               addresses=get_base_addresses(df['AddressLower']))
    print(f"Fuzzy Match Done: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    name_list = df.groupby("closest_approximate_match")['Name'].apply(set).tolist()
    print(f"Dataframe grouped: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    return sort_and_format_names(name_list)


@get_runtime
def polars_reader(file: IO[bytes]) -> str:
    df = pl.read_csv(file).unique()
    df = df.with_columns(
        Address=pl.col("Address").map_elements(translate_address)
    )
    df = df.with_columns(
        AddressLower=pl.col("Address").map_elements(create_address_lower)
    )

    addresses = get_base_addresses(df["AddressLower"])

    df = df.with_columns(
        closest_approximate_match=pl.col("AddressLower").map_elements(lambda x: fuzzy_compare(x, addresses))
    )

    df = df.group_by("closest_approximate_match").agg(pl.col('Name'))

    name_list = functools.reduce(operator.iconcat, df.select("Name").rows(named=False), [])
    return sort_and_format_names(name_list)


processors = {
    'pandas-df': pandas_reader,
    'polars-df': polars_reader,
}
