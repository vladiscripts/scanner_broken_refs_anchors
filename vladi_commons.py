# -*- coding: utf-8  -*-#
# author: https://github.com/vladiscripts
#
# Библиотека общих функций:
# работа с файлами в utf-8
#
from sys import version_info
PYTHON_VERSION = version_info.major
if PYTHON_VERSION == 3:
	from urllib.parse import urlencode, quote  # python 3
else:
	from urllib import urlencode, quote  # python 2.7
	import codecs
# ----------


def file_savelines(filename, text, append=False):
	mode = 'a' if append else 'w'
	text = '\n'.join(text)
	with open(filename, mode, encoding='utf-8') as f:
		f.write(text)


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

def json_store_to_file(filename, data):
	import json
	with open(filename, 'w', encoding='utf-8') as f:
		f.write(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))
	pass


def json_data_from_file(filename):
	import json
	with open(filename, 'r', encoding='utf-8') as f:
		data = json.load(f)
	return data


def save_error_log(filename, text):
	import datetime
	now = datetime.datetime.now()
	time = now.strftime("%d-%m-%Y %H:%M")
	file_savelines(filename, text, True)


def pickle_store_to_file(filename, data):
	import pickle
	with open(filename, 'wb') as f:
		pickle.dump(data, f)


def pickle_data_from_file(filename):
	import pickle
	with open(filename, 'rb') as f:
		data = pickle.load(f)
	return data