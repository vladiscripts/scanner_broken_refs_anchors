# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from sqlalchemy.sql import update
from scripts.db import session, Page, Ref, WarningTps  # , Timecheck
import asyncio
import aiohttp
from aiohttp import ClientSession
import async_timeout
# from time import
import socket
import time
from urllib.parse import quote
from config import *
from scripts.scan_refs_of_page import ScanRefsOfPage, page_html_parse_a
import scripts.asyncio_exeptions
# from vladi_commons.vladi_commons import file_readlines
# from vladi_commons import file_readlines
from lxml.html import tostring, fromstring
from sqlalchemy.sql import null


class MakeLists:
	full_err_listpages = {}
	transcludes_sfntpls = set()
	transcludes_of_warning_tpl = set()
	errpages_without_warning_tpl = set()
	list_to_remove_warning_tpl = set()

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

		# # удаление старых ошибок в любом случае: если не обнаружены, или есть новые
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


	async def asynchronous(self, list_pages, loop):
		headers = {'user-agent': 'user:textworkerBot'}
		sem = asyncio.Semaphore(100)
		conn = aiohttp.TCPConnector(
			family=socket.AF_INET,
			verify_ssl=False,
		)
		async with ClientSession(headers=headers, connector=conn, loop=loop) as session:
			tasks = [asyncio.ensure_future(self.scan_pagehtml_for_referrors(sem, p, session)) for p in list_pages]
			# finished, unfinished = event_loop.run_until_complete(asyncio.wait(tasks))
			finished, unfinished = await asyncio.wait(tasks)
			# for task in finished:
				# if task.result() != 'None' or task.result() is not None:
				# 	print('!!!!!!!!!!!!!')
				# print(task.result())  # returns only None
				# pass
			print("unfinished2:", len(unfinished))

			# responses = asyncio.gather(*tasks)
			# await responses
			pass

	async def db_works(self, p):
		page_id = p[0]
		# page_title = p[1]
		errrefs = p[2]

		# удаление записей о старых ошибках
		session.query(Ref).filter(Ref.page_id == page_id).delete()
		# session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: null()})
		# обновление таблицы Refs
		for refs in errrefs:
			session.add(Ref(page_id, refs['citeref'], refs['link_to_sfn'], refs['text']))
		# обновление таблицы Pages
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

	async def scan_pagehtml_for_referrors(self, sem, p, session):
		"""Сканирование страницы на ошибки"""
		page_id = p[0]
		page_title = p[1]
		url = 'https://ru.wikipedia.org/wiki/' + quote(page_title)

		if page_title == 'None' or page_title is None:
			print('!!!!!!!!!!!!!')

		# print(page_title)
		# response_text = await fetch(url, session)
		# try:
		# 	r = await aiohttp.request('GET', url, params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
		# # r = requests.get(url, params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
		# except:
		# 	return '{}: http error'.format(page_title)
		# r.close()
		# text = await response.text

		# async with sem:
			# async with session.get(url, params={"action": "render"}) as response:
			# 	if response and response.status == 200:
			# 		# assert response.status == 200
			# 		response_text = await response.text()
			# 		parsed_html = fromstring(response_text)
			# 		page = ScanRefsOfPage(page_id, page_title, parsed_html)
			# 		errrefs = [page_id, page_title, page.full_errrefs]
			# 		del page
			# 		return errrefs

			# 	async with session.get(url, params={"action": "render"}) as response:
			# 		try:
			# 			if response.status == 200:
			# 				assert response.status == 200
			# 				response_text = await response.text()
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

		async with sem:
			# with async_timeout.timeout(5):
			retries = 0
			while retries <= 5:
				try:
					response = await session.request('get', url, params={"action": "render"},) # timeout=30
					# response = await scripts.asyncio_exeptions.send_http(session, 'get', url,
					# 													 retries=3,
					# 													 interval=0.9,
					# 													 backoff=3,
					# 													 read_timeout=30.9, )
					# await asyncio.sleep(1)
					# print(response)
					pass
					if response.status == 200:
						response_text = await response.text()
						# response.close()
						parsed_html = fromstring(response_text)
						print(page_title)
						page = ScanRefsOfPage(page_id, page_title, parsed_html)
						errrefs = page.full_errrefs
						try:
							errrefs
						except:
							pass
						errrefs = [page_id, page_title, errrefs]
						await self.db_works(errrefs)

						del page

						# try:
						# 	errrefs[0]
						# except:
						# 	pass
						# return errrefs
					elif response.status == 429:
						# Too many requests
						retries += 1
						await asyncio.sleep(1)
					else:
						# response.close()
						print(page_title + ' response.status != 200')
					response.close()
					break

				except (aiohttp.ClientOSError, aiohttp.ClientResponseError,
				aiohttp.ServerDisconnectedError, asyncio.TimeoutError) as e:
					print('!!! Error. url: %s; error: %r', url, e)
					retries += 1
					await asyncio.sleep(1)
				# except aiohttp.ClientOSError as e:
				# 	print(page_title + ' !!!!!!! ClientOSError')
				# 	retries += 1
				# 	await asyncio.sleep(1)
				# # Блокируем все таски на 30 секунд в случае ошибки 429.
				# # time.sleep(30)
				# except aiohttp.ServerDisconnectedError as e:
				# 	print(page_title + ' !!!!!!! ServerDisconnectedError')
				# 	retries += 1
				# 	await asyncio.sleep(1)
				# 	# await asyncio.sleep(1)
				# 	# await self.scan_pagehtml_for_referrors(sem, p, session)
				# # Блокируем все таски на 30 секунд в случае ошибки 429.
				# # time.sleep(30)
				# # time.sleep(1)
				# except Exception as e:
				# 	print(page_title + ' !!!!!!! Exception')
				# 	retries += 1
				# 	await asyncio.sleep(1)
				# # # Блокируем все таски на 30 секунд в случае ошибки 429.
				# # 	time.sleep(30)
				# # else:

	async def async_request(self, sem, url):
		async with sem:
			try:
				response = await session.request('get', url, params={"action": "render"})
			except aiohttp.ClientOSError as e:
				print(url + ' aiohttp.ClientOSError as e')
				print(e)
				# Блокируем все таски на 30 секунд в случае ошибки 429.
				time.sleep(30)
			except Exception as e:
				print(url + ' Exception as e')
				print(e)
				# Блокируем все таски на 30 секунд в случае ошибки 429.
				time.sleep(30)
			else:
				return response

	def db_get_list_pages_for_scan(self):
		# 	"""	может праильней так?
		# 	SELECT * FROM  pages LEFT JOIN timecheck
		# 	ON pages.page_id=timecheck.page_id
		# 	WHERE timecheck.page_id is null
		#
		# 	при объединении таблицы timecheck
		# 	SELECT * FROM  pages WHERE timecheck is null
		# 	"""
		q = session.query(Page.page_id, Page.title).select_from(Page).filter(
			(Page.timecheck.is_(None)) | (Page.timeedit > Page.timecheck))
		# q = session.query(Page.page_id, Page.title) \
		# 	.select_from(Page) \
		# 	.outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
		# 	.filter(
		# 	(Timecheck.timecheck.is_(None)) |
		# 	(Page.timeedit > Timecheck.timecheck)
		# )
		return session.execute(q).fetchall()

	def save_listpages_to_remove_warning_tpl(self):
		query = session.query(WarningTps.title) \
			.select_from(WarningTps) \
			.outerjoin(Ref, WarningTps.page_id == Ref.page_id) \
			.filter(Ref.page_id.is_(None))

		self.list_to_remove_warning_tpl = [str(title[0]) for title in session.execute(query).fetchall()]
		file_savelines(filename_list_to_remove_warning_tpl, sorted(self.list_to_remove_warning_tpl))

	def save_listpages_to_add_warning_tpl(self):
		"""Список куда предупреждение ещё не поставлено."""
		query = session.query(Page.title).select_from(Page) \
			.outerjoin(WarningTps) \
			.join(Ref, Page.page_id == Ref.page_id) \
			.filter(WarningTps.page_id.is_(None), Ref.page_id.isnot(None)) \
			.group_by(Page.title)

		self.errpages_without_warning_tpl = [str(title[0]) for title in session.execute(query).fetchall()]
		file_savelines(filename_listpages_errref_where_no_yet_warning_tpl, self.errpages_without_warning_tpl)

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
