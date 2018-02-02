#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import asyncio
import aiohttp
from aiohttp import ClientSession
import requests
from lxml.html import fromstring
import socket
import time
from urllib.parse import quote
from config import *
from scripts.db import session, Page, Ref, Timecheck, queryDB
from scripts.scan_refs_of_page import ScanRefsOfPage


class MakeLists:

	def scan_pages_for_referrors(self):
		"""Сканирование страниц на ошибки"""
		list_pages_for_scan = self.db_get_list_pages_for_scan()

		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.asynchronous(list_pages_for_scan, loop))
		loop.close()

	async def asynchronous(self, list_pages, loop):
		headers = {'user-agent': 'user:textworkerBot'}
		sem = asyncio.Semaphore(limit_asynch_threads)
		conn = aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False)
		async with ClientSession(headers=headers, connector=conn, loop=loop) as session:
			tasks = [asyncio.ensure_future(self.scan_pagehtml_for_referrors(sem, p, session)) for p in list_pages]
			finished, unfinished = await asyncio.wait(tasks)
			if len(unfinished):
				print('have unfinished async tasks')

	async def db_works(self, p):
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

	async def scan_pagehtml_for_referrors(self, sem, p, session):
		"""Сканирование страницы на ошибки"""
		page_id, page_title = p[0], p[1]
		url = 'https://ru.wikipedia.org/wiki/' + quote(page_title)

		if page_title == 'None' or page_title is None:
			print('!!!!!!!!!!!!!')

		async with sem:
			retries = 0
			while retries <= 5:
				try:
					response = await session.request('GET', url, params={"action": "render"}, )  # timeout=30

					if response.status == 200:
						response_text = await response.text()
						parsed_html = fromstring(response_text)
						print(page_title)
						page = ScanRefsOfPage(parsed_html)
						errrefs = page.err_refs
						try:
							errrefs
						except:
							pass
						await self.db_works([page_id, page_title, errrefs])
						del page
					elif response.status == 429:
						# Too many requests
						retries += 1
						await asyncio.sleep(1)
					else:
						print(page_title + ' response.status != 200')
					response.close()
					break

				except (aiohttp.ClientOSError, aiohttp.ClientResponseError,
						aiohttp.ServerDisconnectedError, asyncio.TimeoutError) as e:
					print('!!! Error. Page title: "%s"; url: %s; error: %r. Can will work on a next request.' % (
						page_title, url, e))
					retries += 1
					await asyncio.sleep(1)

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
