#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import time
import requests
from urllib.parse import quote
from scripts.db import session, Page, Ref, Timecheck, queryDB
from scripts.scan_refs_of_page import ScanRefsOfPage


def do_scan():
	"""Сканирование страниц на ошибки"""
	s = requests.Session()

	for p in db_get_list_pages_for_scan():
		page_id, page_title = p[0], p[1]
		session.rollback()

		# if page_id != 273920:	continue  # For tests

		# Очистка db от списка старых ошибок
		session.query(Ref).filter(Ref.page_id == page_id).delete()
		session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()

		# Сканирование страниц на ошибки
		# page = ScanRefsOfPage(page_id, page_title)
		htmltree = s.get('https://ru.wikipedia.org/wiki/' + quote(page_title), params={"action": "render"},
						 headers={'user-agent': 'user:textworkerBot'})
		print(page_title)
		page = ScanRefsOfPage(htmltree)
		for ref in page.err_refs:
			session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))

		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
		session.add(Timecheck(page_id, time_current))
		session.commit()


def db_get_list_pages_for_scan():
	return queryDB(session.query(Page.page_id, Page.title) \
				   .select_from(Page) \
				   .outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
				   .filter((Timecheck.timecheck.is_(None)) | (Page.timeedit > Timecheck.timecheck)))

# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
