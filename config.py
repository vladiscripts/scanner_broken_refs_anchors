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

# При запуске в Windows через AWB могут быть проблемы с кодировкой. Из-за кодовой страницы cmd.exe.
# Для починки сменить в ОС кодировку, на utf-8 командой консоли "chcp 65001".
# Или отключить в скрипте выводы типа print("Вывод не английских символв, не кодирвки ASCII cp866").

# Отладка
read_list_from_file_JSON = False  # Взять полный список ошибок из файла JSON, без создания нового и сканирования, или (jgwbb yb;t):
filename_listpages_errref_json = 'listpages_err_ref.json'
# ---
# Иначе (read_list_from_file_JSON = False):
# 1 - брать список включений шаблонов из wiki базы данных
# 2 - из файла (можно подставить уже отсканированный)
# 3 - указ. вручную
get_transcludes_from = 3
filename_tpls_transcludes = 'list_tpls_transcludes.txt'
filename_listpages_errref = 'listpages_err_ref.txt'
test_pages = [
	# 'Африканская_мифология',
	# 'Участник:Vladis13/статья',
	# '1991_год',
	'Гибридная_интеллектуальная_система',
	'Раскраска_графов',
	'Звёздчатый_октаэдр',
	# тест отдельных страниц, связано с get_transcludes_from
]
# ---
edit_page_by_list = False  # Не редактировать страницы, только ссканировать и сделать список
# ---
name_of_warning_tpl = 'Нет полных библиографических описаний'  # Участник:Vladis13/ошибки сносок
exclude_regexp = r'\{\{([Шш]аблон:)?[Нн]ет[ _]полных[ _]библиографических[ _]описаний'  # \{\{([Шш]аблон:)?[уУ]частник:[Vv]ladis13/[Оо]шибки[ _]сносок
list_transcludes_of_warningtemple = 'list_uses_warningtpl.txt'

summary = 'Пометка сносок с неработающими ссылками в список литературы'  # комментарий к правкам страниц

# Создание вики-списков для автоподстановки в шаблон посредством {{#lst:}} и <section="" />
max_lines_per_file = 2000
filename_part = 'wikisections'  # к имени добавляется № части и расширение '.txt'
root_wikilists = name_of_warning_tpl + '/'  # где располагать списки секций, лучше в корне подстраницами шаблона-предупреждения
marker_page_start = '{{-start-}}'
marker_page_end = '{{-end-}}'
header = """
Список статей, с перечнями их сносок, в которых указаны некорректные викиссылки.

Элементы списка автоподставляются в перечисленных статьях в шаблон {{t|Нет полных библиографических описаний}}.
(Это служебная таблица даных для подстановок, поэтому с этой страницы ссылки на сноски не работают.)

Список обновляется ботом.

"""  # в шапку шаблон {{координационный список}} не нужен, ибо это не список, а подстраница данных скрипта
bottom = '[[Категория:Википедия:Подстраницы шаблонов]][[Категория:Шаблоны:Подстраницы Нет полных библиографических описаний|{{SUBPAGENAME}}]]'

# ---
ask_save_prompts = True  # работает с wikiAPI
# ---
filename_error_log = 'error_log.txt'
print_log = True
print_log_full = False

# Обрабатывать только одну страницу, беря контент из файла. Например, для работы из бота AWB.
do_only_1_page_by_content_from_file = True  # работает с вики-парсером
filename_page_wikicontent = r'../temp/AWBfile.txt'  # страница в вики-разметке

names_of_tpls_like_sfns = (['sfn', 'sfn0', 'Sfn-1',
							'Harvard citation', 'Harv',
							'Harvard citation no brackets', 'Harvnb', 'Harvsp',
							'Harvcol', 'Harvcoltxt', 'Harvcolnb', 'Harvrefcol'])
# names_of_tpls_like_sfns = 'Вершины Каменного Пояса'  # Отладка
# Не работает с шаблонами не создающими ссылки 'CITEREF', типа:  '-1'

# filename = r"d:\home\scripts.my\4wiki\\" + filename
# filename = 'sfn0.txt'

URLapi = 'https://ru.wikipedia.org/w/api.php'
URLindex = 'https://ru.wikipedia.org/w/index.php'
URLhtml = 'https://ru.wikipedia.org/wiki/'
headers = {'user-agent': 'user:textworkerBot'}
file_password_to_api = 'password.txt'  # 2 string: 1 - user, 2 - password
