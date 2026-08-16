
from .url_structural_features import *
import pandas as pd
import numpy as np

TRAINING_DATA = "data/Training.parquet"
FULL_DATA_FRAME = pd.read_parquet(TRAINING_DATA, engine='pyarrow')

def describe_feature(feature_name: str):
    NUM_UNIQUE_VALS = FULL_DATA_FRAME[feature_name].nunique()
    IS_BOOL = FULL_DATA_FRAME[feature_name].nunique() == 2
    MAX_VAL = FULL_DATA_FRAME[feature_name].max()

    print("Num Unique Values:", NUM_UNIQUE_VALS)
    print("Is Boolean?:", IS_BOOL)

    if not IS_BOOL:
        print("Max Value:", MAX_VAL)


def validate_helper_func(feature_name: str, funct: callable, *args):
    num_conflicts = 0
    conflicts_dict = {}

    for idx in range(0, len(FULL_DATA_FRAME)):
        URL = FULL_DATA_FRAME["url"][idx]
        RECEIVED_VALUE = funct(URL, *args)
        EXPECTED_VALUE = FULL_DATA_FRAME[feature_name][idx]
        
        if type(EXPECTED_VALUE) is np.float64:
            RECEIVED_VALUE = round(RECEIVED_VALUE, 9)
            EXPECTED_VALUE = round(EXPECTED_VALUE, 9)

        if RECEIVED_VALUE != EXPECTED_VALUE:
            num_conflicts += 1
            conflicts_dict[idx] = {
                "URL": URL,
                "Received": RECEIVED_VALUE,
                "Expected": EXPECTED_VALUE
            }

    if num_conflicts >= 1:
        print(f'\nNumber of Conflicts detected for "{funct.__name__}": {num_conflicts}')
        describe_feature(feature_name)

        conflict_values = iter(conflicts_dict.values())

        try:
            print(next(conflict_values))
            print(next(conflict_values))
            print(next(conflict_values))
            print(next(conflict_values))
        except StopIteration:
            pass

    else:
        print(f'\nThe function "{funct.__name__}" passed without issue')



if __name__ == "__main__":
    feature_function_pairings = {
        'nb_dots': (get_nb_symbol, '.'),
        'length_url': get_url_length,
        'length_hostname': get_hostname_length,
        # 'nb_subdomains': get_nb_subdomains,
        'ratio_digits_url': get_ratio_digits_url,
        # 'ratio_digits_host': get_ratio_digits_host,
        # 'port': contains_port,
        'longest_word_host': get_longest_word_host
    }
    
    for feature_name, funct in feature_function_pairings.items():
        if isinstance(funct, tuple):
            funct, args = funct
            validate_helper_func(feature_name, funct, args)
        else:
            validate_helper_func(feature_name, funct)
