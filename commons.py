# -*- coding: utf-8  -*-
from sys import version_info

PYTHON_VERSION = version_info.major

if PYTHON_VERSION == 3:
	from urllib.parse import urlencode, quote  # python 3
else:
	from urllib import urlencode, quote  # python 2.7
	import codecs
import requests

ask_save_prompts = False  # True

URLapi = 'https://ru.wikipedia.org/w/api.php'
URLindex = 'https://ru.wikipedia.org/w/index.php'
URLhtml = 'https://ru.wikipedia.org/wiki/'
headers = {'user-agent': 'user:textworkerBot'}


def file_savelines(filename, list):
	list = '\n'.join(list)
	with open(filename, 'w', encoding='utf-8') as f:
		f.write(list)


def file_textread(filename):
	with open(filename, 'r', encoding='utf-8') as f:
		text = f.read()
	return text


def file_readlines_in_list(filename):
	if PYTHON_VERSION == 3:
		f = open(filename, encoding='utf-8')
	# arr_strings = set([line.rstrip() for line in f])  # python 3
	else:
		f = codecs.open(filename, 'r', encoding='utf-8')
	# with codecs.open(filename, 'r', encoding='utf-8') as f:  # python 2.7
	# 	arr_strings = [line.rstrip() for line in f]  # python 2.7
	arr_strings = f.read().splitlines()
	# arr_strings = [line.rstrip() for line in f]
	f.close()
	return arr_strings


def file_readlines_in_set(filename):
	arr_strings = set(file_readlines_in_list(filename))
	return arr_strings


def pickle_store_to_file(data, filename):
	import pickle
	with open(filename, 'wb') as f:
		pickle.dump(data, f)


def pickle_data_from_file(filename):
	import pickle
	with open(filename, 'rb') as f:
		data = pickle.load(f)
	return data
