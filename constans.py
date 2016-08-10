# -*- coding: utf-8  -*-
from sys import version_info
PYTHON_VERSION = version_info.major

if PYTHON_VERSION == 3:
	from urllib.parse import urlencode, quote  # python 3
else:
	from urllib import urlencode, quote  # python 2.7
	import codecs
import requests
