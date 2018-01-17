#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from sqlalchemy.sql import update
from scripts.db import session, Page, Ref, WarningTpls  # , Timecheck
import asyncio
import aiohttp
from aiohttp import ClientSession
import async_timeout
# from time import
import socket
import time
from urllib.parse import quote
from config import *
from scripts.scan_refs_of_page import ScanRefsOfPage
import scripts.asyncio_exeptions
# from vladi_commons.vladi_commons import file_readlines
# from vladi_commons import file_readlines
from lxml.html import tostring, fromstring
from sqlalchemy.sql import null
import requests
import asyncio
import aiohttp


class MakeLists:
	# full_err_listpages = {}
	# transcludes_sfntpls = set()
	# transcludes_of_warning_tpl = set()
	# errpages_without_warning_tpl = set()
	# list_to_remove_warning_tpl = set()

	# self.sfns_like_names = vladi_commons.str2list(names_sfn_templates)

	# def scan_pages_with_referrors_old(self):
	# 	"""Сканирование страниц на ошибки"""
	# 	for p in self.db_get_list_pages_for_scan():
	# 		page_id = p[0]
	# 		page_title = p[1]
	#
	# 		# удаление старых ошибок в любом случае: если не обнаружены, или есть новые
	# 		session.query(Ref).filter(Ref.page_id == page_id).delete()
	# 		# session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()
	#
	# 		# сканирование страниц на ошибки
	# 		page = ScanRefsOfPage(page_id, page_title)
	# 		for ref in page.full_errrefs:
	# 			session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
	# 		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
	# 		session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
	# 		# session.add(Timecheck(page_id, time_current))
	# 		session.commit()

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

	# page = ScanRefsOfPage(page_id, page_title)
	# # for ref in page.full_errrefs:
	# # 	session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
	# # errs = [(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']) for ref in page.full_errrefs]
	# # session.add(Ref).values(errs)

	#
	# errs = [(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']) for ref in page.full_errrefs]
	# session.Refs.add_all(errs)

	# time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
	# session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
	# # session.add(Timecheck(page_id, time_current))
	# session.commit()
	# return

	@asyncio.coroutine
	def asynchronous(self, list_pages, loop):
		headers = {'user-agent': 'user:textworkerBot'}
		sem = asyncio.Semaphore(100)
		conn = aiohttp.TCPConnector(
			family=socket.AF_INET,
			verify_ssl=False,
		)
		with ClientSession(headers=headers, connector=conn, loop=loop) as session:
			tasks = [asyncio.ensure_future(self.scan_pagehtml_for_referrors(sem, p, session)) for p in list_pages]
			# finished, unfinished = event_loop.run_until_complete(asyncio.wait(tasks))
			result = yield from asyncio.wait(tasks)
			# for task in finished:
			# if task.result() != 'None' or task.result() is not None:
			# 	print('!!!!!!!!!!!!!')
			# print(task.result())  # returns only None
			# pass
			# print("unfinished2:", len(unfinished))

			# responses = asyncio.gather(*tasks)
			# yield from responses
			pass

	@asyncio.coroutine
	def db_works(self, p):
		page_id = p[0]
		# page_title = p[1]
		errrefs = p[2]

		# очистка db от списка старых ошибок
		session.query(Ref).filter(Ref.page_id == page_id).delete()

		for refs in errrefs:
			session.add(Ref(page_id, refs['citeref'], refs['link_to_sfn'], refs['text']))
		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
		session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
		session.commit()

	# async def db_works(self, all_errefs):
	# 	for p in all_errefs:
	# 		try:
	# 			page_id = p[0]
	# 		except:
	# 		    pass
	#
	# 		# page_title = p[1]
	# 		page_errefs = p[2]
	#
	# 		# удаление старых ошибок в любом случае: если не обнаружены, или есть новые
	# 		# session.query(Ref).filter(Ref.page_id == page_id).delete()
	# 		# session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: null()})
	#
	# 		for refs in page_errefs:
	# 			session.add(Ref(page_id, refs['citeref'], refs['link_to_sfn'], refs['text']))
	#
	# 		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
	# 		session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
	# 		session.commit()

	@asyncio.coroutine
	def scan_pagehtml_for_referrors(self, sem, p, session):
		"""Сканирование страницы на ошибки"""
		page_id = p[0]
		page_title = p[1]
		url = 'https://ru.wikipedia.org/wiki/' + quote(page_title)

		if page_title == 'None' or page_title is None:
			print('!!!!!!!!!!!!!')

		# print(page_title)
		# response_text = yield from fetch(url, session)
		# try:
		# 	r = yield from aiohttp.request('GET', url, params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
		# # r = requests.get(url, params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
		# except:
		# 	return '{}: http error'.format(page_title)
		# r.close()
		# text = yield from response.text

		# async with sem:
		# async with session.get(url, params={"action": "render"}) as response:
		# 	if response and response.status == 200:
		# 		# assert response.status == 200
		# 		response_text = yield from response.text()
		# 		parsed_html = fromstring(response_text)
		# 		page = ScanRefsOfPage(page_id, page_title, parsed_html)
		# 		errrefs = [page_id, page_title, page.full_errrefs]
		# 		del page
		# 		return errrefs

		# 	async with session.get(url, params={"action": "render"}) as response:
		# 		try:
		# 			if response.status == 200:
		# 				assert response.status == 200
		# 				response_text = yield from response.text()
		# 				parsed_html = fromstring(response_text)
		# 				# print(page_title)
		# 				page = ScanRefsOfPage(page_id, page_title, parsed_html)
		# 				errrefs = [page_id, page_title, page.full_errrefs]
		# 				del page
		# 				return errrefs
		# 			if response.status != 200:
		# 				print(page_title + ' response.status != 200:')
		# 		except Exception as e:
		# 			print(page_title)
		# 			# print(e)
		# 			# Блокируем все таски на 30 секунд в случае ошибки 429.
		# 			# time.sleep(30)

		with (yield from sem):
			# with async_timeout.timeout(5):
			retries = 0
			while retries <= 5:
				try:
					response = yield from session.request('GET', url, params={"action": "render"}, )  # timeout=30
					# response = yield from scripts.asyncio_exeptions.send_http(session, 'get', url,
					# 													 retries=3,
					# 													 interval=0.9,
					# 													 backoff=3,
					# 													 read_timeout=30.9, )
					# yield from asyncio.sleep(1)
					# print(response)
					pass
					if response.status == 200:
						response_text = yield from response.text()
						# response.close()
						parsed_html = fromstring(response_text)
						print(page_title)
						page = ScanRefsOfPage(parsed_html)
						errrefs = page.full_errrefs
						try:
							errrefs
						except:
							pass
						errrefs = [page_id, page_title, errrefs]
						yield from self.db_works(errrefs)

						del page

					# try:
					# 	errrefs[0]
					# except:
					# 	pass
					# return errrefs
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
					print('!!! Error. url: %s; error: %r', url, e)
					retries += 1
					yield from asyncio.sleep(1)

	# except aiohttp.ClientOSError as e:
	# 	print(page_title + ' !!!!!!! ClientOSError')
	# 	retries += 1
	# 	yield from asyncio.sleep(1)
	# # Блокируем все таски на 30 секунд в случае ошибки 429.
	# # time.sleep(30)
	# except aiohttp.ServerDisconnectedError as e:
	# 	print(page_title + ' !!!!!!! ServerDisconnectedError')
	# 	retries += 1
	# 	yield from asyncio.sleep(1)
	# 	# yield from asyncio.sleep(1)
	# 	# yield from self.scan_pagehtml_for_referrors(sem, p, session)
	# # Блокируем все таски на 30 секунд в случае ошибки 429.
	# # time.sleep(30)
	# # time.sleep(1)
	# except Exception as e:
	# 	print(page_title + ' !!!!!!! Exception')
	# 	retries += 1
	# 	yield from asyncio.sleep(1)
	# # # Блокируем все таски на 30 секунд в случае ошибки 429.
	# # 	time.sleep(30)
	# # else:

	# async def async_request(self, sem, url):
	# 	async with sem:
	# 		try:
	# 			response = yield from session.request('get', url, params={"action": "render"})
	# 		except aiohttp.ClientOSError as e:
	# 			print(url + ' aiohttp.ClientOSError as e')
	# 			print(e)
	# 			# Блокируем все таски на 30 секунд в случае ошибки 429.
	# 			time.sleep(30)
	# 		except Exception as e:
	# 			print(url + ' Exception as e')
	# 			print(e)
	# 			# Блокируем все таски на 30 секунд в случае ошибки 429.
	# 			time.sleep(30)
	# 		else:
	# 			return response

	def db_get_list_pages_for_scan(self):
		# 	"""	может правильней так?
		# 	SELECT * FROM  pages LEFT JOIN timecheck
		# 	ON pages.page_id=timecheck.page_id
		# 	WHERE timecheck.page_id is null
		#
		# 	при объединении таблицы timecheck
		# 	SELECT * FROM  pages WHERE timecheck is null
		# 	"""

		# q = session.query(Page.page_id, Page.title) \
		# 	.select_from(Page) \
		# 	.outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
		# 	.filter(
		# 	(Timecheck.timecheck.is_(None)) |
		# 	(Page.timeedit > Timecheck.timecheck)
		# )
		q = session.query(Page.page_id, Page.title).select_from(Page).filter(
			(Page.timecheck.is_(None)) | (Page.timeedit > Page.timecheck))
		return session.execute(q).fetchall()


def db_get_list_pages_for_scan():
	q = session.query(Page.page_id, Page.title).select_from(Page).filter(
		(Page.timecheck.is_(None)) | (Page.timeedit > Page.timecheck))
	return session.execute(q).fetchall()

# def make_list_transcludes_of_warning_tpl(self):
# 	"""Список страниц где шаблон уже установлен."""
# 	# Взять с сайта - True, или из файла - False.
# 	if transcludes_of_warning_tpl_get_from_site:
# 		db.make_list_transcludes_from_wdb_to_sqlite()
# 		vladi_commons.file_savelines(filename_list_transcludes_of_warning_tpl,
# 									 sorted(self.transcludes_of_warning_tpl))
# 	else:
# 		self.transcludes_of_warning_tpl = vladi_commons.file_readlines_in_set(
# 				filename_list_transcludes_of_warning_tpl)
#
# def make_list_transcludes_sfns(self):
# 	"""Список включений sfn-шаблонов. С сайта, из файла, или указанные вручную."""
# 	global get_transcludes_from
#
# 	if get_transcludes_from == 1:  # from wikiAPI
# 		self.transcludes_sfntpls = self.get_list_transcludes_of_tpls_from_site(self.sfns_like_names)
# 		vladi_commons.file_savelines(filename_tpls_transcludes, self.transcludes_sfntpls)
#
# 	# Тесты
# 	elif get_transcludes_from == 2:  # from file
# 		self.transcludes_sfntpls = vladi_commons.file_readlines_in_set(filename_tpls_transcludes)
#
# 	elif get_transcludes_from == 3:  # from manual
# 		global test_pages
# 		self.transcludes_sfntpls = test_pages

# async def page_html_parse_a(title):
# 	try:
# 		r = yield from aiohttp.request('GET', 'https://ru.wikipedia.org/wiki/' + quote(title),
# 								  params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
# 	except:
# 		return '{}: http error'.format(title)
# 	parsed_html = yield from fromstring(r.text)
# 	return parsed_html

def page_html_parse(title):
	r = requests.get('https://ru.wikipedia.org/wiki/' + quote(title), params={"action": "render"},
					 headers={'user-agent': 'user:textworkerBot'})
	return fromstring(r.text)


# def do_scan():
# 	"""Сканирование страниц на ошибки"""
# 	q = session.query(Page.page_id, Page.title).select_from(Page).filter(
# 		(Page.timecheck.is_(None)) |
# 		(Page.timeedit > Page.timecheck))
# 	list_pages_for_scan = session.execute(q).fetchall()
#
# 	for p in list_pages_for_scan:
# 		page_id = p[0]
# 		page_title = p[1]
#
# 		# очистка db от списка старых ошибок
# 		session.query(Ref).filter(Ref.page_id == page_id).delete()
# 		# session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()
#
# 		# сканирование страниц на ошибки
# 		page = ScanRefsOfPage(page_html_parse(page_title))
# 		for ref in page.full_errrefs:
# 			session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
# 		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
# 		session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
# 		# session.add(Timecheck(page_id, time_current))
# 		session.commit()


# def db_get_list_pages_for_scan(self):
# 	# 	"""	может праильней так?
# 	# 	SELECT * FROM  pages LEFT JOIN timecheck
# 	# 	ON pages.page_id=timecheck.page_id
# 	# 	WHERE timecheck.page_id is null
# 	#
# 	# 	при объединении таблицы timecheck
# 	# 	SELECT * FROM  pages WHERE timecheck is null
# 	# 	"""
# 	q = session.query(Page.page_id, Page.title).select_from(Page).filter(
# 		(Page.timecheck.is_(None)) |
# 		(Page.timeedit > Page.timecheck))
# 	# q = session.query(Page.page_id, Page.title) \
# 	# 	.select_from(Page) \
# 	# 	.outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
# 	# 	.filter(
# 	# 	(Timecheck.timecheck.is_(None)) |
# 	# 	(Page.timeedit > Timecheck.timecheck)
# 	# )
# 	return session.execute(q).fetchall()


# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# import traceback
# from time import sleep
# from aiohttp import ClientSession
#
#
# # page = ScanRefsOfPage('2416978', 'Ячменное')
#
# async def fetch(url, session):
# 	async with session.get(url, params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'}, ) \
# 			as response:
# 		return yield from response.text()
#
#
# async def db_work(data):
# 	for i in data:
# 		print('{}: data'.format(i))
#
#
# async def scan_pagehtml_for_referrors(sem, p, session):
# 	"""Сканирование страницы на ошибки"""
# 	page_id = p[0]
# 	page_title = p[2].strip('"')
# 	url = 'https://ru.wikipedia.org/wiki/' + quote(page_title)
# 	# response_text = yield from fetch(url, session)
# 	# try:
# 	# 	r = yield from aiohttp.request('GET', url, params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
# 	# # r = requests.get(url, params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
# 	# except:
# 	# 	return '{}: http error'.format(page_title)
# 	# r.close()
# 	# text = yield from response.text
# 	async with sem:
# 		async with session.get(url, params={"action": "render"}) as response:
# 			try:
# 				if response.status != 200:
# 					pass
# 				assert response.status == 200
# 				response_text = yield from response.text()
# 				parsed_html = fromstring(response_text)
# 				print(page_title)
# 				page = ScanRefsOfPage(page_id, page_title, parsed_html)
# 				errrefs = [page_id, page_title, page.full_errrefs]
# 				del page
# 				return errrefs
# 			except Exception as e:
# 				# print(e)
# 				# Блокируем все таски на 30 секунд в случае ошибки 429.
# 				sleep(30)
#
#
# async def asynchronous():
# 	headers = {'user-agent': 'user:textworkerBot'}
# 	listpages = file_readlines('/tmp/refs-warning-pages.txt')    # [:10]
# 	sem = asyncio.Semaphore(500)
# 	async with ClientSession(headers=headers) as session:
# 		tasks = [asyncio.ensure_future(scan_pagehtml_for_referrors(sem, p.partition(','), session)) for p in listpages]
# 		# tasks.extend(asyncio.ensure_future(db_work(data))
# 		# tasks = [scan_pagehtml_for_referrors(p.partition(','), session) for p in listpages]
# 		responses = yield from asyncio.gather(*tasks)
# 		# yield from responses
# 		pass
# 		# print(responses)
# 	yield from db_work(responses)
# 		# asyncio.ensure_future(db_work(data))
#
# 		# # done, pending = yield from asyncio.wait(futures_htmls, return_when=FIRST_COMPLETED)
# 		# done, pending = yield from asyncio.wait(tasks)
# 		# # print(done.pop().result())
# 		# # for future in pending:
# 		# # 	future.cancel()
# 		# for future in done:
# 		# 	try:
# 		# 		print(future.result())
# 		# 	except:
# 		# 		print("Unexpected error: {}".format(traceback.format_exc()))
# 		# 	# for i, future in enumerate(asyncio.as_completed(futures_htmls)):
# 		# 	# 	result = yield from future
# 		# 	# 	print('{} {}'.format(">>" * (i + 1), result))
#
#
# def scan_pages_for_referrors():
# 	# listpages = file_readlines('/tmp/refs-warning-pages.txt')
# 	# list_pages_for_scan = self.db_get_list_pages_for_scan()
# 	# futures_htmls = [page_html_parse_a(p[1]) for p in listpages]
# 	# futures = [self.scan_page_for_referrors(p) for p in list_pages_for_scan]
# 	event_loop = asyncio.get_event_loop()
# 		# event_loop.run_until_complete(asyncio.wait(asynchronous))
# 		# event_loop.run_until_complete(asyncio.wait(futures))
# 		# tasks = [event_loop.create_task(scan_pagehtml_for_referrors()), event_loop.create_task(bar())]
# 	event_loop.run_until_complete(asynchronous())
# 	event_loop.close()
#
#
# import timeit
#
# # без asyncio эти ~3500 requests занимают ~1.5 часа
# # print(timeit.timeit('scan_pages_for_referrors()', number=1000))
# # print(timeit.timeit('scan_pages_for_referrors()', number=1))
# scan_pages_for_referrors()
# pass




import os
import urllib.request
from threading import Thread
import threading


class WorkerThread(threading.Thread):
	def __init__(self, url_list, url_list_lock):
		super(WorkerThread, self).__init__()
		self.url_list = url_list
		self.url_list_lock = url_list_lock

	def run(self):
		while (1):
			nexturl = self.grab_next_url()
			if nexturl == None: break
			self.retrieve_url(nexturl)
			pass

	def grab_next_url(self):
		self.url_list_lock.acquire(1)
		if len(self.url_list) < 1:
			nexturl = None
		else:
			nexturl = self.url_list[0]
			del self.url_list[0]
		self.url_list_lock.release()
		return nexturl

	def retrieve_url(self, nexturl):
		p = nexturl
		# page_id = p[0]
		# page_title = p[1]
		# url = 'https://ru.wikipedia.org/wiki/' + quote(page_title)
		scan_page(p)



def do_work_threading():
	list_pages_for_scan = db_get_list_pages_for_scan()
	url_list = list_pages_for_scan
	url_list_lock = threading.Lock()
	workerthreadlist = []
	for x in range(0, 3):
		newthread = WorkerThread(url_list, url_list_lock)
		workerthreadlist.append(newthread)
		newthread.start()
	for x in range(0, 3):
		workerthreadlist[x].join()



def do_scan():
	"""Сканирование страниц на ошибки"""
	q = session.query(Page.page_id, Page.title).select_from(Page).filter(
		(Page.timecheck.is_(None)) |
		(Page.timeedit > Page.timecheck))
	list_pages_for_scan = session.execute(q).fetchall()

	for p in list_pages_for_scan:
		page_id = p[0]
		page_title = p[1]

		# очистка db от списка старых ошибок
		session.query(Ref).filter(Ref.page_id == page_id).delete()
		# session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()

		# сканирование страниц на ошибки
		page = ScanRefsOfPage(page_html_parse(page_title))
		for ref in page.full_errrefs:
			session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
		session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
		# session.add(Timecheck(page_id, time_current))
		session.commit()


def scan_page(p):
	"""Сканирование страниц на ошибки"""
	page_id = p[0]
	page_title = p[1]

	# очистка db от списка старых ошибок
	session.query(Ref).filter(Ref.page_id == page_id).delete()
	# session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()

	# сканирование страниц на ошибки
	page = ScanRefsOfPage(page_html_parse(page_title))
	for ref in page.full_errrefs:
		session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
	time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
	session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
	# session.add(Timecheck(page_id, time_current))
	session.commit()
