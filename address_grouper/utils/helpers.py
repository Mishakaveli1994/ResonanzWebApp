import logging
import time
import datetime
from functools import wraps, lru_cache

from deep_translator import GoogleTranslator
from pandas import DataFrame
from rapidfuzz import fuzz

translator = GoogleTranslator(source='auto', target='en')

logger = logging.getLogger('basic')


def get_runtime(func):
    """
    Decorator that returns the runtime of the Processor functions
    :param func: Processor function. Either Pandas, Polars or Dask
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        started = time.time()
        dataset = func(*args, **kwargs)
        elapsed = time.time() - started
        str_elapsed = str(datetime.timedelta(seconds=int(elapsed)))
        logger.info(f"{func.__name__} -> Time elapsed: {str_elapsed}")
        return {'output': dataset, 'elapsed': str_elapsed}

    return wrapper


@lru_cache
def translate_address(address: str, g_translator: GoogleTranslator = translator) -> str:
    """
    A function that translates a given address if it contains non-ascii characters.
    :param address: Address string
    :param g_translator: Passed from above, as it is not hashable and lru_cache will not owrk
    :return:
    """
    if address.isascii():
        return address
    return g_translator.translate(address, dest='en')


def get_base_addresses(df_address: DataFrame) -> set:
    """
    Get the base addresses, by basically eliminates ones that are too similar
    :param df_address: DataFrame containing addresses
    :return:
    """
    addresses = set()
    threshold = 65

    for address in df_address.unique():
        match_ratios = [fuzz.token_set_ratio(i, address) for i in addresses]

        if all(ratio < threshold for ratio in match_ratios):
            addresses.add(address)
    return addresses


def fuzzy_compare(row: str, addresses: set, threshold=65) -> str | None:
    """
    Fuzzy Compare all addresses with the base ones and groups them if their similarity is larger than the threshold.
    Using fuzz.token_set_ratio as it behaves best if strings are out of order or there are different words mixed in
    :param row: Row to be compared
    :param addresses: Base addresses
    :param threshold: Matching threshold
    :return: Matched address, or None
    """
    best_match = None
    highest_score = 0
    for address in addresses:
        score = fuzz.token_set_ratio(row, address)
        if score > highest_score:
            highest_score = score
            best_match = address

    return best_match if highest_score >= threshold else None


def create_address_lower(address: str) -> str:
    """
    Creates a lower case version of an address abd removes spaces
    Used to simplify strings and optimize fuzz-matching
    :param address: Address string
    :return: Lower case, no space version of address
    """
    return address.lower().replace(" ", '')


def sort_and_format_names(name_list: list[list[str]]):
    """
    Sorts and formats a list of names
    First sorts internal lists and then the outer one
    :param name_list: List of lists of names
    :return: Sorted list
    """
    return '\n'.join(sorted([", ".join(sorted(set(i))) for i in name_list]))
