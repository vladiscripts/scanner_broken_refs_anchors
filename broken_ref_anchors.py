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
	test = Add_warning_tpl(name_of_warning_tpl, pages_with_referrors)
	pass
