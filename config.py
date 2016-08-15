# -*- coding: utf-8  -*-
# from sys import version_info
# PYTHON_VERSION = version_info.major
from urllib.parse import urlencode, quote  # python 3
# if PYTHON_VERSION == 3:
# 	from urllib.parse import urlencode, quote  # python 3
# else:
# 	from urllib import urlencode, quote  # python 2.7
# 	import codecs
import requests
from vladi_commons import *

# Отладка
read_list_from_file_JSON = False  # Взять полный список с ошибками из файла JSON, без создания нового и сканирования, или:
filename_listpages_errref_json = 'listpages_errref_json.txt'
# ---
# 1 - брать список включений шаблонов из wiki базы данных
# 2 - из файла (можно подставить уже отсканированный)
# 3 - указ. вручную
get_transcludes_from = 2
filename_tpls_transcludes = 'list_tpls_transcludes.txt'
filename_listpages_errref = 'listpages_errref.txt'
test_pages = [
	'Участник:Vladis13/статья',
	'1991_год']  # , 'Гибридная_интеллектуальная_система', 'Раскраска_графов', 'Звёздчатый_октаэдр']  #    тест отдельных страниц, связано с get_transcludes_from
# ---
edit_page_by_list = False  # Не редактировать страницы, только ссканировать и сделать список
ask_save_prompts = False  # True
# ---
filename_error_log = 'error_log.txt'
print_log = True
print_log_full = False

# Обрабатывать только одну страницу, беря контент из файла. Например, для работы из бота AWB.
do_only_1_page_by_content_from_file = True
filename_page_wikicontent = r'../temp/AWBfile.txt'  # страница в вики-разметке

names_of_tpls_like_sfns = (['sfn', 'sfn0', 'Sfn-1',
							'Harvard citation', 'Harv',
							'Harvard citation no brackets', 'Harvnb', 'Harvsp',
							'Harvcol', 'Harvcoltxt', 'Harvcolnb', 'Harvrefcol'])
# names_of_tpls_like_sfns = 'Вершины Каменного Пояса'  # Отладка
# Не работает с шаблонами не создающими ссылки 'CITEREF', типа:  '-1'

name_of_warning_tpl = 'ошибки сносок'
list_transcludes_of_warningtemple = 'list_uses_warningtpl.txt'

summary = 'Пометка сносок с неработающими ссылками в список литературы'  # комментарий к правкам страниц

# filename = r"d:\home\scripts.my\4wiki\\" + filename
# filename = 'sfn0.txt'

URLapi = 'https://ru.wikipedia.org/w/api.php'
URLindex = 'https://ru.wikipedia.org/w/index.php'
URLhtml = 'https://ru.wikipedia.org/wiki/'
headers = {'user-agent': 'user:textworkerBot'}
file_password_to_api = 'password.txt'  # 2 string: 1 - user, 2 - password
