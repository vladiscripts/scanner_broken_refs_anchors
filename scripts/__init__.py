from collections import namedtuple
from typing import Union, Optional, List, Tuple, Set
from datetime import datetime
# from urllib.parse import quote
from .logger import logger


def file_savelines(filename, strlist, append=False):
    mode = 'a' if append else 'w'
    text = '\n'.join(strlist)
    with open(filename, mode, encoding='utf-8') as f:
        f.write(text)


def file_savetext(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)


def file_readlines(filename: str):
    with open(filename, 'r', encoding='utf-8') as f:
        arr_strings = f.read().splitlines()
    return list_clean_empty_strs(arr_strings)


def list_clean_empty_strs(lst):
    """Чистка пустых строк в списке"""
    return [l.strip() for l in lst if l.strip() != '']


def pickle_save_to_file(filename: str, data):
    import pickle
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def pickle_load_from_file(filename: str):
    import pickle
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data
