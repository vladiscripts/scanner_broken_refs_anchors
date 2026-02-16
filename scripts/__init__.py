from datetime import datetime, timezone
from .logger import logger


def _chunked(iterable, n):
    """Разбивает итерируемый объект на чанки по n элементов."""
    lst = list(iterable)
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


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
