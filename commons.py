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


def readlines_file_in_list(filename):
	if PYTHON_VERSION == 3:
		f = open(filename, encoding='utf-8')
	# arr_strings = set([line.rstrip() for line in f])  # python 3
	else:
		f = codecs.open(filename, 'r', encoding='utf-8')
	# with codecs.open(filename, 'r', encoding='utf-8') as f:  # python 2.7
	# 	arr_strings = [line.rstrip() for line in f]  # python 2.7
	arr_strings = [line.rstrip() for line in f]
	f.close()
	return arr_strings


def readlines_file_in_set(filename):
	# if PYTHON_VERSION == 3:
	# 	arr_strings = set([line.rstrip() for line in open(filename, encoding='utf-8')])  # python 3
	# else:
	# 	with codecs.open(filename, 'r', encoding='utf-8') as f:  # python 2.7
	# 		arr_strings = set([line.rstrip() for line in f])  # python 2.7
	if PYTHON_VERSION == 3:
		f = open(filename, encoding='utf-8')  # python 3
	else:
		f = codecs.open(filename, 'r', encoding='utf-8')  # python 2.7
	arr_strings = set([line.rstrip() for line in f])
	f.close()
	return arr_strings
