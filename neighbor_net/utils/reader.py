import logging
from typing import IO
import pandas as pd
import polars as pl
import functools
import operator
import time
import datetime
import dask.dataframe as dd

from .helpers import get_runtime, get_base_addresses, fuzzy_compare, translate_address, create_address_lower, \
    sort_and_format_names

from pandas_schema import Column, Schema
from pandas_schema.validation import LeadingWhitespaceValidation, TrailingWhitespaceValidation

logger = logging.getLogger('basic')

# Options so dataframes from different processors are displayed in full
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 200)
pl.Config.set_fmt_str_lengths(900)
pl.Config.set_tbl_width_chars(900)


@get_runtime
def dask_reader(file: IO[bytes]) -> str:
    """
    Read and process a stream of csv formatted using Dask
    Initial DataFrame created with Pandas as Dask does not support streaming read
    :param file: IO[bytes] stream of csv formatted text
    :return: String with sorted people
    """
    started = time.time()
    schema = Schema([
        Column('Name', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]),
        Column('Address', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]),
    ])

    df = pd.read_csv(file, header='infer').drop_duplicates()
    logger.debug(f"Dataframe created: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    errors = schema.validate(df)
    if errors:
        return '\n'.join([str(i) for i in errors])
    df = dd.from_pandas(df, npartitions=10)
    df['Address'] = df['Address'].apply(lambda x: translate_address(x), meta=('Address', 'string'))
    logger.debug(f"Addressed translated: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    df['AddressLower'] = df['Address'].apply(create_address_lower, meta=('AddressLower', 'string'))
    logger.debug(f"Lower created: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    df['closest_approximate_match'] = df['AddressLower'].apply(fuzzy_compare,
                                                               addresses=get_base_addresses(df['AddressLower']),
                                                               meta=('closest_approximate_match', 'string'))
    logger.debug(f"Fuzzy Match Done: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    name_list = list(df.groupby("closest_approximate_match")['Name'].apply(set).compute(scheduler='processes'))
    return sort_and_format_names(name_list)


@get_runtime
def pandas_reader(file: IO[bytes]) -> str:
    """
    Read and process a stream of csv formatted using Pandas
    :param file: IO[bytes] stream of csv formatted text
    :return: String with sorted people
    """
    started = time.time()
    schema = Schema([
        Column('Name', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]),
        Column('Address', [LeadingWhitespaceValidation(), TrailingWhitespaceValidation()]),
    ])

    df = pd.read_csv(file, header='infer').drop_duplicates()
    logger.debug(f"Dataframe created: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    errors = schema.validate(df)
    if errors:
        return '\n'.join([str(i) for i in errors])

    df['Address'] = df['Address'].apply(lambda x: translate_address(x))
    logger.debug(f"Addressed translated: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    df['AddressLower'] = df['Address'].apply(create_address_lower)
    logger.debug(f"Lower created: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    df['closest_approximate_match'] = df['AddressLower'].apply(fuzzy_compare,
                                                               addresses=get_base_addresses(df['AddressLower']))
    logger.debug(f"Fuzzy Match Done: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    name_list = df.groupby("closest_approximate_match")['Name'].apply(set).tolist()
    return sort_and_format_names(name_list)


@get_runtime
def polars_reader(file: IO[bytes]) -> str:
    """
    Read and process a stream of csv formatted using Polars
    :param file: IO[bytes] stream of csv formatted text
    :return: String with sorted people
    """
    started = time.time()
    df = pl.read_csv(file).unique()
    logger.debug(f"Dataframe created: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    df = df.with_columns(
        Address=pl.col("Address").map_elements(translate_address)
    )
    logger.debug(f"Addressed translated: {str(datetime.timedelta(seconds=int(time.time() - started)))}")
    df = df.with_columns(
        AddressLower=pl.col("Address").map_elements(create_address_lower)
    )
    logger.debug(f"Lower created: {str(datetime.timedelta(seconds=int(time.time() - started)))}")

    addresses = get_base_addresses(df["AddressLower"])

    df = df.with_columns(
        closest_approximate_match=pl.col("AddressLower").map_elements(lambda x: fuzzy_compare(x, addresses))
    )
    logger.debug(f"Fuzzy Match Done: {str(datetime.timedelta(seconds=int(time.time() - started)))}")

    df = df.group_by("closest_approximate_match").agg(pl.col('Name'))

    name_list = functools.reduce(operator.iconcat, df.select("Name").rows(named=False), [])
    return sort_and_format_names(name_list)


processors = {
    'pandas': pandas_reader,
    'polars': polars_reader,
    'dask': dask_reader,
}
