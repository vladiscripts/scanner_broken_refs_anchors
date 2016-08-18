# -*- coding: utf-8  -*-
#
# author: https://github.com/vladiscripts
#
# from urllib.request import urlopen
# import mwparserfromhell
from lxml import html
import re
# from lxml.etree import fromstring
# from grab import Grab
from config import *
import wikiapi, add_warning_tpl
from make_list_pages_with_referrors import *
import add_warning_tpl
from vladi_commons import *

pages_with_referrors = {}

# Создание списков страниц с ошибками
# Читать готовый список из файла
if read_list_from_file_JSON:
	pages_with_referrors = json_data_from_file(filename_listpages_errref_json)

# или создать новый
else:
	# список включений sfn-like шаблонов
	list_transcludes = make_list_transcludes(names_of_tpls_like_sfns, filename_tpls_transcludes)

	# сканирование на ошибки
	referrors = MakeListpageReferrors(list_transcludes)
	pages_with_referrors = referrors.pages_with_referrors
	del referrors

	# Запись списков в файл
	if len(pages_with_referrors) > 0:
		file_savelines(filename_listpages_errref, pages_with_referrors)
		json_store_to_file(filename_listpages_errref_json, pages_with_referrors)

# Добавление предупреждающего шаблона на страницы списка
if edit_page_by_list:
	# Парсинг и замена плохих сносок в шаблонах в викикоде страниц
	# Сложная операция, меющая уязвимости. Ибо параметры шаблонов могут править люди на тысячах страниц,
	# и парсер может глючить на страницах с битым кодом (вставленными ии незакрытыми html-тэгами).
	# Более простой и надёжный вариант:
	# создание страниц-списков ошибок, и парсинг секций из них (для конкретных страниц) нативной функцией вики "{{#lst:}}".

	# test = add_warning_tpl.Add_warning_tpl(name_of_warning_tpl, pages_with_referrors)

	# filename = 'listpages_errref_json17-1325.txt'
	pages_with_referrors = vladi_commons.json_data_from_file(filename_listpages_errref_json)

	pwb_format = True
	# saved_filenames = make_wikilists(pages_with_referrors, pwb_format)
	saved_filenames = MakeWikiList(pages_with_referrors, pwb_format)

	import subprocess

	python_and_path = r'python3 scripts/'

	# Запись списков
	cmd = python_and_path + 'pagefromfile.py -simulate -force -file:' + filename_part + '.txt' + ' -start:"{{-start-}}" -end:"{{-end-}}" -summary:"обновление списка"'
	# subprocess.call(cmd, shell=True)

	# Простановка в статьях шаблона про ошибки
	cmd = python_and_path + 'add_text.py -simulate -file:' + filename_listpages_errref + ' -text:"{{' + name_of_warning_tpl + '}}" -except:"' + exclude_regexp + '" -summary:"Шаблон: некорректные ссылки в сносках"'
	# subprocess.call(cmd, shell=True)
