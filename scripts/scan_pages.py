#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
# from sqlalchemy.sql import update
# from sqlalchemy.sql import null
import asyncio
import aiohttp
from aiohttp import ClientSession
# import async_timeout
# import scripts.asyncio_exeptions
import requests
from lxml.html import tostring, fromstring
import socket
import time
from urllib.parse import quote
from config import *
from scripts.db import session, Page, Ref, WarningTpls, Timecheck, queryDB
from scripts.scan_refs_of_page import ScanRefsOfPage


# from vladi_commons.vladi_commons import file_readlines
# from vladi_commons import file_readlines


class MakeLists:
	# full_err_listpages = {}
	# transcludes_sfntpls = set()
	# transcludes_of_warning_tpl = set()
	# errpages_without_warning_tpl = set()
	# list_to_remove_warning_tpl = set()

	def scan_pages_for_referrors(self):
		"""Сканирование страниц на ошибки"""

		# # очистка удаление старых ошибок в любом случае: если не обнаружены, или есть новые
		# session.query(Ref).filter(Ref.page_id == page_id).delete()
		# # session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()
		#

		# сканирование страниц на ошибки
		list_pages_for_scan = self.db_get_list_pages_for_scan()
		# futures_htmls = [page_html_parse_a(p[1]) for p in list_pages_for_scan]
		# futures = [self.scan_page_for_referrors(p) for p in list_pages_for_scan]
		# list_pages_for_scan = []
		# for p in file_readlines('/tmp/refs-warning-pages.txt')[:10]:
		# 	i = p.partition(',')
		# 	list_pages_for_scan.append((i[0], i[2].strip('"')))

		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.asynchronous(list_pages_for_scan, loop))
		loop.close()


	@asyncio.coroutine
	def asynchronous(self, list_pages, loop):
		headers = {'user-agent': 'user:textworkerBot'}
		sem = asyncio.Semaphore(limit_asynch_threads)
		conn = aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False)
		with ClientSession(headers=headers, connector=conn, loop=loop) as session:
			tasks = [asyncio.async(self.scan_pagehtml_for_referrors(sem, p, session)) for p in list_pages]
			finished, unfinished = yield from asyncio.wait(tasks)
			if len(unfinished):
				print('have unfinished async tasks')
				pass
			# finished, unfinished = event_loop.run_until_complete(asyncio.wait(tasks))
			# result = yield from asyncio.wait(tasks)
			# for task in finished:
			# 	if task.result() != 'None' or task.result() is not None:
			# 		print('!!!!!!!!!!!!!')
			# 	print(task.result())  # returns only None
			# pass
			# print("unfinished2:", len(unfinished))
			# responses = asyncio.gather(*tasks)
			# yield from responses
			pass

	@asyncio.coroutine
	def db_works(self, p):
		page_id, page_title, err_refs = p[0], p[1], p[2]
		session.rollback()

		# For tests
		# if page_id != 17492: return

		# очистка db от списка старых ошибок
		session.query(Ref).filter(Ref.page_id == page_id).delete()
		session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()

		for refs in err_refs:
			session.add(Ref(page_id, refs['citeref'], refs['link_to_sfn'], refs['text']))
		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
		session.add(Timecheck(page_id, time_current))
		session.commit()

	@asyncio.coroutine
	def scan_pagehtml_for_referrors(self, sem, p, session):
		"""Сканирование страницы на ошибки"""
		page_id, page_title = p[0], p[1]
		url = 'https://ru.wikipedia.org/wiki/' + quote(page_title)

		if page_title == 'None' or page_title is None:
			print('!!!!!!!!!!!!!')

		with (yield from sem):
			retries = 0
			while retries <= 5:
				try:
					response = yield from session.request('GET', url, params={"action": "render"}, )  # timeout=30
					pass

					if response.status == 200:
						response_text = yield from response.text()
						parsed_html = fromstring(response_text)
						print(page_title)
						page = ScanRefsOfPage(parsed_html)
						errrefs = page.err_refs
						try:
							errrefs
						except:
							pass
						yield from self.db_works([page_id, page_title, errrefs])
						del page
					elif response.status == 429:
						# Too many requests
						retries += 1
						yield from asyncio.sleep(1)
					else:
						# response.close()
						print(page_title + ' response.status != 200')
					response.close()
					break

				except (aiohttp.ClientOSError, aiohttp.ClientResponseError,
						aiohttp.ServerDisconnectedError, asyncio.TimeoutError) as e:
					print('!!! Error. Page title: "%s"; url: %s; error: %r. Can will work on a next request.' % (
					page_title, url, e))
					retries += 1
					yield from asyncio.sleep(1)

	def db_get_list_pages_for_scan(self):
		return queryDB(session.query(Page.page_id, Page.title) \
					   .select_from(Page) \
					   .outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
					   .filter((Timecheck.timecheck.is_(None)) | (Page.timeedit > Timecheck.timecheck)))


def page_html_parse(title):
	r = requests.get('https://ru.wikipedia.org/wiki/' + quote(title), params={"action": "render"},
					 headers={'user-agent': 'user:textworkerBot'})
	return fromstring(r.text)

# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass



