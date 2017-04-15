#!/usr/bin/env python3
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import os
from config import *
from scripts.make_listspages import MakeLists
from scripts.make_wikilists import MakeWikiLists
from scripts.db_update import UpdateDB

# Сканирование и обновление базы данных
if do_generation_lists:
	m = MakeLists()

	if do_update_db_from_wiki:
		# Обновление списка страниц имеющих warning-шаблон, шаблоны сносок,
		# и очистка базы от устарелых данных
		db_update = UpdateDB()

	# Создание списков страниц с ошибками
	print('start scan pages')
	m.scan_pages_with_referrors()
	m.save_listpages_to_remove_warning_tpl()
	m.save_listpages_to_add_warning_tpl()

	if make_wikilist:
		w = MakeWikiLists()
		w.save_wikilist()

# Запись списков ----
python_and_path = r'python3 $PWBPATH/scripts/'
# python_and_path = r'python scripts/'
pwb_cfg = r' -dir:~/.pywikibot/'
family = 'wikipedia'

# логин
# os.system(python_and_path + 'login.py' + pwb_cfg)

if disable_all_post_to_wiki:
	do_post_list = do_post_template = do_remove_template = False

if do_post_list:
	sim = ' -simulate' if do_post_list_simulate else ''  # "-simulate" параметр для тестирования записи pwb
	params = [
		'-file:' + filename_wikilists + '.txt',
		'-begin:"' + marker_page_start + '"', '-end:"' + marker_page_end + '"', '-notitle',
		'-summary:"обновление списка"',
		'-pt:1', pwb_cfg, '-family:' + family,
		'-force', sim,
	]
	os.system(python_and_path + 'pagefromfile.py' + ' ' + ' '.join(params))

# Простановка в статьях шаблона про ошибки
if do_post_template:
	sim = ' -simulate' if do_post_template_simulate else ''
	params = [
		'-file:' + filename_listpages_errref_where_no_yet_warning_tpl,
		'-text:"{{' + warning_tpl_name + '}}"',
		# '-except:"' + warning_tpl_regexp + '"',
		u'-summary:"+шаблон: некорректные викиссылки в сносках"',
		'-pt:1', pwb_cfg, '-family:' + family,
		'-always', sim,
	]
	os.system(python_and_path + 'add_text.py' + ' ' + ' '.join(params))

# Удаление шаблона из статей
if do_remove_template:
	sim = '-simulate' if do_remove_template_simulate else ''
	params = [
		'-regex "' + warning_tpl_regexp + '.*?}}" ""', '-nocase', '-dotall',
		'-file:' + filename_list_to_remove_warning_tpl, '-ns:0',
		'-summary:"-шаблон: ошибочных викиссылок в сносках не найдено"',
		'-pt:1', pwb_cfg, '-family:' + family,
		'-always', sim,
	]
	os.system(python_and_path + 'replace.py' + ' ' + ' '.join(params))
