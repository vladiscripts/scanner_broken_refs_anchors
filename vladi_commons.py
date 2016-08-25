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


def file_savetext(filename, text):
	with open(filename, 'w', encoding='utf-8') as f:
		text = f.write(text)


def file_readtext(filename):
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


def str2list(string):
	"""Строку в список"""
	return [string] if isinstance(string, str) else string


def split_list_per_line_count(lst, chunk_size):
	"""Разделение списка на части по числу строк."""
	return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def re_compile_list(re_groups):
	"""Регулярных выражений по списку компиляция.

	Список типа: letter_groups = ['[АБВГДЕЁЖЗ]', '[ИКЛМНО]', '[ПH]', '[СТУФХЦЧШЩЪЫЬЭЮЯ]', r'[.]']
	"""
	import re
	groups = []
	for g in re_groups:
		c = re.compile(g, re.I + re.U)
		groups.append(c)
	return groups


def re_compile_dict(re_groups, flags=False):
	"""Регулярных выражений по словарю компиляция.

	Принимает словарь типа:
	{'АБВГДЕЁЖЗ': '[АБВГДЕЁЖЗ]', 'other': r'.'}

	Возващает типа:
		groups = [
		{'name': 'АБВГДЕЁЖЗ', 're': '[АБВГДЕЁЖЗ]', 'c': re.compiled},
		{'name': 'other', 're': r'.', 'c': re.compiled},
	]
	"""
	import re
	flags = re.I + re.U if not flags else flags
	groups = []
	for g in re_groups:
		string = {}
		string['name'] = g
		string['re'] = re_groups[g]
		string['c'] = re.compile(re_groups[g], flags)
		groups.append(string)
	return groups


# ---
def send_email_toollabs(subject, text, email='tools.vltools@tools.wmflabs.org'):
	# Не работает из скрипа, из консоли - да
	# https://wikitech.wikimedia.org/wiki/Help:Tool_Labs#Mail_from_tools
	#
	import subprocess
	cmd = 'echo -e "Subject: ' + subject + r'\n\n' + text + '" | /usr/sbin/exim -odf -i ' + email
	subprocess.call(cmd, shell=True)
