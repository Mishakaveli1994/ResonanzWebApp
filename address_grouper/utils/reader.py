from typing import IO
import pandas as pd
import polars as pl

from .helpers import get_runtime, get_base_addresses, fuzzy_compare, translate_address

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 200)
pl.Config.set_fmt_str_lengths(900)
pl.Config.set_tbl_width_chars(900)


@get_runtime
def pandas_reader(file: IO[bytes]) -> str:
    df = pd.read_csv(file, header='infer')
    df['Address'] = df['Address'].apply(lambda x: translate_address(x))

    df['AddressLower'] = df['Address'].str.lower()
    df['AddressLower'] = df['Address'].str.replace(" ", "")
    df['closest_approximate_match'] = df['AddressLower'].apply(fuzzy_compare,
                                                               addresses=get_base_addresses(df['AddressLower']))
    name_list = df.groupby("closest_approximate_match")['Name'].apply(sorted).sort_values().tolist()
    return "\n".join(sorted(sorted([', '.join(set(i)) for i in name_list], key=lambda x: x), key=lambda x: x[0]))


@get_runtime
def polars_reader(file: IO[bytes]) -> str:
    df = pl.read_csv(file)
    df = df.with_columns(
        Address=pl.col("Address").map_elements(translate_address)
    )
    df = df.with_columns(
        AddressLower=pl.col("Address").map_elements(str.lower)
    )
    df = df.with_columns(
        AddressLower=pl.col("AddressLower").str.replace_all(" ", "")
    )
    addresses = get_base_addresses(df["AddressLower"])
    df = df.with_columns(
        closest_approximate_match=pl.col("AddressLower").map_elements(lambda x: fuzzy_compare(x, addresses))
    )

    df = df.group_by("closest_approximate_match").agg(pl.col('Name'))
    df = df.with_columns(
        Name=pl.col("Name").map_elements(sorted)
    )
    df = df.with_columns(
        FirstPerson=pl.col("Name").map_elements(lambda x: x[0])
    )
    df = df.sort('FirstPerson')
    print("\n".join(sorted([', '.join(set(i)) for i in [b[1] for b in df.rows(named=False)]], key=lambda x: x[0])))

    #return "\n".join(sorted(sorted([', '.join(set(i)) for i in name_list], key=lambda x: x), key=lambda x: x[0]))
    # return "\n".join(
    #     sorted(sorted(([', '.join(set(i)) for i in [i[1] for i in df.rows(named=False)]]), key=lambda x: x),
    #            key=lambda x: x[0]))


processors = {
    'pandas-df': pandas_reader,
    'polars-df': polars_reader,
}
