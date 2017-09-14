#!/usr/bin/env python3
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from config import *
from scripts import post_to_wiki
from scripts.db_update import UpdateDB
from scripts.make_listspages import MakeLists
from scripts.make_wikilists import MakeWikiLists

if __name__ == '__main__':

	# сброс меток проверки
	if clear_check_pages_with_warnings:
		UpdateDB.drop_check_pages_with_warnings()
	if clear_all_check_pages:
		UpdateDB.drop_all_check_pages()

	# Сканирование и обновление базы данных
	if do_generation_lists:
		m = MakeLists()

		if do_update_db_from_wiki:
			# Обновление списка страниц имеющих warning-шаблон, шаблоны сносок,
			# и очистка базы от устарелых данных
			db_update = UpdateDB()

		# Создание списков страниц с ошибками
		print('start scan pages')
		m.scan_pages_for_referrors()
		m.save_listpages_to_remove_warning_tpl()
		m.save_listpages_to_add_warning_tpl()

		if make_wikilist:
			w = MakeWikiLists()
			w.save_wikilist()

	# Запись списков и установка шаблонов в wiki
	if not do_all_post_to_wiki:
		do_post_list = do_post_template = do_remove_template = False
	if do_post_list:
		post_to_wiki.posting_list()
	if do_post_template:
		post_to_wiki.posting_template()
	if do_remove_template:
		post_to_wiki.remove_template()
