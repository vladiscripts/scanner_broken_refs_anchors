# -*- coding: utf-8  -*-
#
# author: https://github.com/vladiscripts
#
from config import *
from make_list_pages_with_referrors import *
# import add_warning_tpl
from vladi_commons import *

pages_with_referrors = {}

# Создание списков страниц с ошибками
if not read_list_from_file_JSON:
	# список включений sfn-like шаблонов
	list_transcludes = make_list_transcludes(names_of_tpls_like_sfns, filename_tpls_transcludes)

	# сканирование на ошибки
	referrors = MakeListpageReferrors(list_transcludes)
	pages_with_referrors = referrors.pages_with_referrors
	del referrors

	# Запись списка в файлы
	if len(pages_with_referrors) > 0:
		file_savelines(filename_listpages_errref, pages_with_referrors)  # просто перечень страниц
		json_store_to_file(filename_listpages_errref_json, pages_with_referrors)  # полные данные в JSON

# или читать готовый полный список ошибок из файла JSON
elif read_list_from_file_JSON:
	pages_with_referrors = json_data_from_file(filename_listpages_errref_json)

# Добавление предупреждающего шаблона на страницы списка
# if edit_page_by_list:

# Парсинг и замена плохих сносок в шаблонах в викикоде страниц
# Сложная операция, меющая уязвимости. Ибо параметры шаблонов могут править люди на тысячах страниц,
# и парсер может глючить на страницах с битым кодом (вставленными ии незакрытыми html-тэгами).
# Более простой и надёжный вариант:
# создание страниц-списков ошибок, и парсинг секций из них (для конкретных страниц) нативной функцией вики "{{#lst:}}".

# test = add_warning_tpl.Add_warning_tpl(name_of_warning_tpl, pages_with_referrors)

pwb_format = True
saved_filenames = MakeWikiList(pages_with_referrors, pwb_format)

# import subprocess
import os

python_and_path = r'python3 scripts/'

# Запись списков
if do_post_list:
	sim = ' -simulate' if do_post_list_simulate else ''  # "-simulate" параметр для тестирования записи pwb
	cmd = python_and_path + 'pagefromfile.py -force' + sim + ' -file:' + filename_part + '.txt' + ' -start:"{{-start-}}" -end:"{{-end-}}" -notitle -summary:"обновление списка" -maxlag:15'
	# subprocess.call(cmd, shell=True)
	os.system(cmd)

# Простановка в статьях шаблона про ошибки
if do_post_template:
	sim = ' -simulate' if do_post_template_simulate else ''
	cmd = python_and_path + 'add_text.py' + sim + ' -file:' + filename_listpages_errref + ' -text:"{{' + name_of_warning_tpl + '}}" -except:"' + exclude_regexp + '" -summary:"+шаблон: некорректные викиссылки в сносках" -maxlag:15'
	# subprocess.call(cmd, shell=True)
	os.system(cmd)
