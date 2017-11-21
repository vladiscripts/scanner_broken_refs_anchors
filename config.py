# coding: utf-8
# При запуске в Windows через AWB могут быть проблемы с кодировкой. Из-за кодовой страницы cmd.exe.
# Для починки сменить в ОС кодировку, на utf-8 командой консоли "chcp 65001".
# Или отключить в скрипте выводы типа print("не английские символы").


filename_tpls_transcludes = 'list_tpls_transcludes.txt'
filename_listpages_errref = 'listpages_err_ref.txt'
# переключатель доступа к базе данных, запускается на ПК или сервере wmflabs
run_local_not_from_wmflabs = True

# ---
# True - сканировать и генерировать новые списки.
# False - только запись списков в файлы и постинг в wiki
do_generation_lists = True

# скачать данные из wiki и сканировать, или работать с тем что есть в файле базы
# отключено при do_generation_lists = False
do_update_db_from_wiki = False
make_wikilist = True

# --- Внмание, включение записи в википедию
do_all_post_to_wiki = False  # Отключение всех опции ниже в этой секции

do_post_list = True  # Запись списков
do_post_list_simulate = True  # Симуляция записи

do_post_template = True  # Запись в статьи шаблона
do_post_template_simulate = True  # Симуляция записи

do_remove_template = True  # Удаление из статей ненужного шаблона
do_remove_template_simulate = True  # Симуляция записи

# ---
warning_tpl_name = 'Нет полных библиографических описаний'
warning_tpl_regexp = r'{{([Шш]аблон:)?([Нн]ет[ _]полных[ _]библиографических[ _]описаний|НПБО)'

# Список страниц где шаблон уже установлен. Взять с сайта - True, из файла - False.
transcludes_of_warning_tpl_get_from_site = True
filename_list_transcludes_of_warning_tpl = 'list_uses_warningtpl.txt'
filename_listpages_errref_where_no_yet_warning_tpl = 'listpages_without_warning_tpl.txt'
filename_list_to_remove_warning_tpl = 'list2remove_warning_tpl.txt'

# ---
# summary = 'Пометка сносок с неработающими ссылками в список литературы'  # комментарий к правкам страниц

# ---
# Создание вики-списков для автоподстановки в шаблон посредством {{#lst:}} и <section="" />
filename_wikilists = 'wikisections'  # к имени добавляется № части и расширение '.txt'

root_wikilists = warning_tpl_name + '/'  # где располагать списки секций, лучше в корне подстраницами шаблона-предупреждения
marker_page_start = '{{-start-}}'
marker_page_end = '{{-end-}}'
header = """
Список статей, с перечнями их сносок, в которых указаны некорректные викиссылки.

Элементы списка автоподставляются в перечисленных статьях в шаблон {{t|Нет полных библиографических описаний}}.
(Это служебная таблица даных для подстановок, поэтому с этой страницы ссылки на сноски не работают.)

Список обновляется ботом.

"""  # в шапку шаблон {{координационный список}} не нужен, ибо это не список, а подстраница данных скрипта
footer = '[[Категория:Википедия:Подстраницы шаблонов]][[Категория:Шаблоны:Подстраницы Нет полных библиографических описаний|{{SUBPAGENAME}}]]'

# ---
print_log = True
filename_error_log = 'errors_log.txt'

# удаление метки проверки у страниц имеющих warning-шаблон
clear_check_pages_with_warnings = False
clear_all_check_pages = False

names_sfn_templates = ((
	'sfn', 'sfn0', 'Sfn-1',
	'Harvard citation', 'Harv',
	'Harvard citation no brackets', 'Harvnb', 'Harvsp',
	'Harvcol', 'Harvcoltxt', 'Harvcolnb', 'Harvrefcol',
))
# Не работает с шаблонами не создающими ссылки 'CITEREF', типа:  '-1'


# --- Общие функции

def file_savelines(filename, strlist, append=False):
	mode = 'a' if append else 'w'
	text = '\n'.join(strlist)
	with open(filename, mode, encoding='utf-8') as f:
		f.write(text)

def file_savetext(filename, text):
	with open(filename, 'w', encoding='utf-8') as f:
		f.write(text)