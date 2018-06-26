#!/usr/bin/env python3
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from config import *
from scripts import post_to_wiki
from scripts.db_update import UpdateDB
from scripts.make_listspages import save_listpages_to_add_warning_tpl, save_listpages_to_remove_warning_tpl
from scripts.make_wikilists import MakeWikiLists
# from scripts.scan_pages_asyncio import Scanner
from scripts import scan_pages

if __name__ == '__main__':

	# сброс меток проверки
	if clear_check_pages_with_warnings:
		UpdateDB.drop_check_pages_with_warnings()
	if clear_all_check_pages:
		UpdateDB.drop_all_check_pages()
		UpdateDB.drop_all_refs()

	# Сканирование и обновление базы данных
	if do_generation_lists:
		if do_update_db_from_wiki:
			# Обновление списка страниц имеющих warning-шаблон, шаблоны сносок,
			# и очистка базы от устарелых данных
			db_update = UpdateDB()

		# старт сканирования
		print('start scan pages')
		# Run asyncio have problem on this server
		# if scan_asyncio:
		# 	scaner = Scanner()
		# 	scaner.do_scan()
		# else:
		# 	scan_pages.do_scan()
		scan_pages.do_scan()

		# Запись списков
		save_listpages_to_remove_warning_tpl()
		save_listpages_to_add_warning_tpl()
		if make_wikilist:
			w = MakeWikiLists()
			w.save_wikilist()

	# Постинг списков и установка шаблонов в wiki
	if do_all_post_to_wiki:
		if do_post_wikilist:
			post_to_wiki.posting_list()
		if do_post_template:
			post_to_wiki.posting_template()
		if do_remove_template:
			post_to_wiki.remove_template()
