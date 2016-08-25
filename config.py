# -*- coding: utf-8  -*-
# from sys import version_info
# PYTHON_VERSION = version_info.major
# if PYTHON_VERSION == 3:
# 	from urllib.parse import urlencode, quote  # python 3
# else:
# 	from urllib import urlencode, quote  # python 2.7
# 	import codecs

# При запуске в Windows через AWB могут быть проблемы с кодировкой. Из-за кодовой страницы cmd.exe.
# Для починки сменить в ОС кодировку, на utf-8 командой консоли "chcp 65001".
# Или отключить в скрипте выводы типа print("Вывод не английских символв, не кодирвки ASCII cp866").

# Отладка

# Список включений sfn-шаблонов
# Иначе (read_list_from_file_JSON = False):
# 1 - взять из wikiAPI
# 2 - из файла (можно подставить уже отсканированный)
# 3 - указ. вручную
get_transcludes_from = 1
filename_tpls_transcludes = 'list_tpls_transcludes.txt'
filename_listpages_errref = 'listpages_err_ref.txt'
test_pages = [
	# 'Африканская_мифология',
	# 'Участник:Vladis13/статья',
	# '1991_год',
	'Гибридная_интеллектуальная_система',
	'Раскраска_графов',
	'Звёздчатый_октаэдр',
]  # тест отдельных страниц, связано с get_transcludes_from

# Взять полный список ошибок из файла JSON, без создания нового и сканирования
read_list_from_file_JSON = True
filename_listpages_errref_json = 'listpages_err_ref.json'

# ---
# edit_page_by_list = True  # Не редактировать страницы, только ссканировать и сделать список
# Внмание, включение записи в википедию
do_post_list = False  # Запись списков
do_post_list_simulate = True  # Симуляция записи

do_post_template = False  # Запись в статьи шаблона
do_post_template_simulate = True  # Симуляция записи

do_remove_template = True  # Удаление из статей ненужного шаблона
do_remove_template_simulate = True  # Симуляция записи

# ---
warning_tpl_name = 'Нет полных библиографических описаний'
warning_tpl_regexp = r'{{([Шш]аблон:)?[Нн]ет[ _]полных[ _]библиографических[ _]описаний'  # \{\{([Шш]аблон:)?[уУ]частник:[Vv]ladis13/[Оо]шибки[ _]сносок
filename_list_transcludes_of_warning_tpl = 'list_uses_warningtpl.txt'
filename_listpages_errref_where_no_yet_warning_tpl = 'listpages_without_warning_tpl.txt'
filename_list_to_remove_warning_tpl = 'list2remove_warning_tpl.txt'

# Список страниц где шаблон уже установлен. Взять с сайта - True, из файла - False.
transcludes_of_warning_tpl_get_from_site = True

# ---
# summary = 'Пометка сносок с неработающими ссылками в список литературы'  # комментарий к правкам страниц

# ---
# Создание вики-списков для автоподстановки в шаблон посредством {{#lst:}} и <section="" />
filename_part = 'wikisections'  # к имени добавляется № части и расширение '.txt'

# max_lines_per_file = 2000  # Отключено, список викиссылок делится на части по алфавиту

root_wikilists = warning_tpl_name + '/'  # где располагать списки секций, лучше в корне подстраницами шаблона-предупреждения
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
filename_error_log = 'error_log.txt'
print_log = True
print_log_full = False

names_sfn_templates = (['sfn', 'sfn0', 'Sfn-1',
						'Harvard citation', 'Harv',
						'Harvard citation no brackets', 'Harvnb', 'Harvsp',
						'Harvcol', 'Harvcoltxt', 'Harvcolnb', 'Harvrefcol'])
# names_of_tpls_like_sfns = 'Вершины Каменного Пояса'  # Отладка
# Не работает с шаблонами не создающими ссылки 'CITEREF', типа:  '-1'
