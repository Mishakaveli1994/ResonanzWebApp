import time
import datetime
from functools import wraps

from deep_translator import GoogleTranslator
from rapidfuzz import fuzz

translator = GoogleTranslator(source='auto', target='en')


def get_runtime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        started = time.time()
        dataset = func(*args, **kwargs)
        elapsed = time.time() - started
        print(f"\n{func.__name__} -> Time elapsed: {str(datetime.timedelta(seconds=int(elapsed)))}")
        return dataset

    return wrapper


def translate_address(address, translator=translator):
    if address.isascii():
        return address
    return translator.translate(address, dest='en')


def get_base_addresses(df_address):
    addresses = set()
    threshold = 65

    for address in df_address.unique():
        match_ratios = [fuzz.ratio(i, address) for i in addresses]

        if all(ratio < threshold for ratio in match_ratios):
            addresses.add(address)
    return addresses


def fuzzy_compare(row, addresses, threshold=65):
    best_match = None
    highest_score = 0
    for address in addresses:
        score = fuzz.ratio(row, address)

        if score > highest_score:
            highest_score = score
            best_match = address

    return best_match if highest_score >= threshold else None
