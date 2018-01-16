# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import requests
import asyncio
import aiohttp
from urllib.parse import quote
from lxml.html import tostring, fromstring
import re
import time
from config import *
from scripts.db import session, Page, Ref, WarningTpls  # , Timecheck


async def page_html_parse_a(title):
	try:
		r = await aiohttp.request('GET', 'https://ru.wikipedia.org/wiki/' + quote(title),
								  params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
	except:
		return '{}: http error'.format(title)
	parsed_html = await fromstring(r.text)
	return parsed_html


def page_html_parse(title):
	r = requests.get('https://ru.wikipedia.org/wiki/' + quote(title), params={"action": "render"},
					 headers={'user-agent': 'user:textworkerBot'})
	return fromstring(r.text)


tag_a = re.compile(r'<a [^>]*>(.*?)</a>', re.DOTALL)


class ScanRefsOfPage:
	def __init__(self, page_id, title, parsed_html):
		self.list_sfns = set()
		self.list_citations = set()
		self.all_sfn_info_of_page = []
		self.full_errrefs = []

		# self.page_id = page_id
		self.title = title
		# self.parsed_html = page_html_parse(self.title)
		# self.parsed_html = await page_html_parse_a(self.title)
		self.parsed_html = parsed_html
		self.find_sfns_on_page()
		self.find_citations_on_page()
		self.compare_refs()

	def find_sfns_on_page(self):
		""" Список сносок из раздела 'Примечания'.
		Возвращает:
		self.list_sfns - список только sfn-id
		self.all_sfn_info_of_page - полный список
		"""
		try:
			# page_references = self.parsed_html.xpath("//ol[@class='references']/li")
			for li in self.parsed_html.cssselect("ol.references li[id^='cite']"):
				# for span in li.xpath("./span[@class='reference-text']"):
				# a_list = span.xpath("./descendant::a[contains(@href,'CITEREF')]")
				# for a in a_list:
				for a in li.cssselect("span.reference-text a[href^='#CITEREF']"):
					aText = tag_a.search(str(tostring(a, encoding='unicode'))).group(1)
					idRef = a.attrib['href'].lstrip('#')
					self.list_sfns.add(idRef)
					self.all_sfn_info_of_page.append(
						{'citeref': idRef, 'text': aText, 'link_to_sfn': str(li.attrib['id'])})

		except Exception as error:
			self.error_print(error)

	def find_citations_on_page(self):
		""" Список id библиографии. Возвращает: self.list_refs """
		try:
			# for xpath in ['//span[@class="citation"]/@id', '//cite/@id']:
			# 	# for href in self.parsed_html.xpath(xpath):
			# for refId in [e.attrib['id'] for e in self.parsed_html.cssselect(css) if 'CITEREF' in e.attrib['id']]:
			# 	# self.list_refs.add(self.cut_refIds(refId))
			# 	self.list_refs.add(refId.lstrip('#'))
			# 	pass
			# cssselect использован для надёжности. В xpath сложней выбор по классу, когда в атрибутах их несколько через пробел
			self.list_citations = {e.attrib['id'] for css in ['span.citation[id^="CITEREF"]', 'cite[id^="CITEREF"]'] for
								   e in self.parsed_html.cssselect(css)}

		except Exception as error:
			self.error_print(error)

	def compare_refs(self):
		""" Разница списков сносок с имеющейся библиографией. Возращает: self.full_errrefs """
		# список сносок с битыми ссылками, из сравнения списков сносок и примечаний
		err_refs = self.list_sfns - self.list_citations
		# Если в статье есть некорректные сноски без целевых примечаний
		if err_refs:
			self.full_errrefs = []
			for citeref_bad in sorted(err_refs):
				it_sfn_double = False
				for sfn in self.all_sfn_info_of_page:
					if citeref_bad == sfn['citeref'] and not it_sfn_double:
						self.full_errrefs.append(sfn)
						# session.add(Ref(self.page_id, sfn['citeref'], sfn['link_to_sfn'], sfn['text']))
						it_sfn_double = True

	def error_print(self, error):
		error_text = 'Error "{}" on parsing footnotes of page "{}"'.format(error, self.title)
		print(error_text)
		file_savelines(filename_error_log, error_text)


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
		page = ScanRefsOfPage(page_id, page_title)
		for ref in page.full_errrefs:
			session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
		session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
		# session.add(Timecheck(page_id, time_current))
		session.commit()

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
# 		return await response.text()
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
# 	# response_text = await fetch(url, session)
# 	# try:
# 	# 	r = await aiohttp.request('GET', url, params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
# 	# # r = requests.get(url, params={"action": "render"}, headers={'user-agent': 'user:textworkerBot'})
# 	# except:
# 	# 	return '{}: http error'.format(page_title)
# 	# r.close()
# 	# text = await response.text
# 	async with sem:
# 		async with session.get(url, params={"action": "render"}) as response:
# 			try:
# 				if response.status != 200:
# 					pass
# 				assert response.status == 200
# 				response_text = await response.text()
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
# 		responses = await asyncio.gather(*tasks)
# 		# await responses
# 		pass
# 		# print(responses)
# 	await db_work(responses)
# 		# asyncio.ensure_future(db_work(data))
#
# 		# # done, pending = await asyncio.wait(futures_htmls, return_when=FIRST_COMPLETED)
# 		# done, pending = await asyncio.wait(tasks)
# 		# # print(done.pop().result())
# 		# # for future in pending:
# 		# # 	future.cancel()
# 		# for future in done:
# 		# 	try:
# 		# 		print(future.result())
# 		# 	except:
# 		# 		print("Unexpected error: {}".format(traceback.format_exc()))
# 		# 	# for i, future in enumerate(asyncio.as_completed(futures_htmls)):
# 		# 	# 	result = await future
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
