# -*- coding: utf-8  -*-
from sys import version_info
PYTHON_VERSION = version_info.major
if PYTHON_VERSION == 3:
	from urllib.parse import urlencode, quote  # python 3
else:
	from urllib import urlencode, quote  # python 2.7
	import codecs
import requests
from vladi_commons import *

# Отладка
edit_page_by_list = False  # Только ссканировать и сделать список, без редактирования страниц
get_transcludes_from = 3  # 1 - брать список wiki базы данных, 2 - из файла, 3 - указ. вручную
test_pages = ['Участник:Vladis13/статья', 'Раскраска_графов', 'Звёздчатый_октаэдр']  #    тест отдельных страниц, связано с get_transcludes_from
print_log = True

ask_save_prompts = False  # True

names_of_tpls_like_sfns = (['sfn', 'sfn0', 'Sfn-1',
							'Harvard citation', 'Harv',
							'Harvard citation no brackets', 'Harvnb', 'Harvsp',
							'Harvcol', 'Harvcoltxt', 'Harvcolnb', 'Harvrefcol'])
# names_of_tpls_like_sfns = 'Вершины Каменного Пояса'
# Не работает с шаблонами не создающими ссылки 'CITEREF', типа:  '-1'

name_of_warning_tpl_ = 'ошибки сносок'
list_transcludes_of_warningtemple = 'list_uses_warningtpl.txt'

# filename = r"d:\home\scripts.my\4wiki\\" + filename
# filename = 'sfn0.txt'
filename_tpls_transcludes = 'list_tpls_transcludes.txt'
filename_listpages_errref = 'listpages_errref.txt'
filename_listpages_errref_json = 'listpages_errref_json.txt'

URLapi = 'https://ru.wikipedia.org/w/api.php'
URLindex = 'https://ru.wikipedia.org/w/index.php'
URLhtml = 'https://ru.wikipedia.org/wiki/'
headers = {'user-agent': 'user:textworkerBot'}

