# -*- coding: utf-8  -*-
# import wikiapi
from commons import *

class make_listpage_referrors:

	list_transcludes = []
	list_pages_with_referrors = {}
	# Тесты
	get_from_file_only = True  # Брать список из файла, или из wiki базы данных
	test_one_page = False  # True

	def __init__(self, tpls_like_sfns_names, filename_tpls_transcludes):
		if not self.test_one_page:
			self.make_listpages_tpls_transcludes(tpls_like_sfns_names, filename_tpls_transcludes)
		else:
			self.list_transcludes = ['Раскраска_графов']  # тест отдельных страниц
		self.make_listpages_with_referrors()

	def collect_refs(self, title, pages_count_cur):
		list_sfns = set()
		list_refs = set()
		ref_calls = {}

		parsed_html = wikiapi.page_html_parse(title)  # html из url
		# parsed_html = html.fromstring(file_textread('test_html.html'))  # html из файла для тестов

		# for li in parsed_html.cssselect('li[href*="CITEREF"]'):
		for eref in parsed_html.cssselect('span.reference-text a[href*="CITEREF"]'):
			href = eref.get('href')
			pos = href.find('CITEREF')
			if pos >= 0:
				href_cut = href[pos:]
				list_sfns.add(href_cut)
				# link_to_sfn ссылка на sfn-сноску
				# print(href)
				try:
					link_to_sfn = parsed_html.xpath("//li[@id]/span/a[@href='{href}']/ancestor::li[contains(@id,'{link_to_sfn}')][1]/@id".format(href=href, link_to_sfn='cite_note'))[0]
				except IndexError:
					try:
						link_to_sfn = parsed_html.xpath(
						"//li[@id]/span/cite/a[@href='{href}']/ancestor::li[contains(@id,'{link_to_sfn}')][1]/@id".format(
							href=href, link_to_sfn='cite_note'))[0]
					except IndexError:
						link_to_sfn = '#Примечания'

				ref_calls[href_cut] = {'text': eref.text, 'link_to_sfn': str(link_to_sfn)}

		for ref in parsed_html.xpath('//span[@class="citation"]/@id'):
			pos = ref.find('CITEREF')
			if pos >= 0:
				list_refs.add(ref[pos:])

		for ref in parsed_html.xpath('//cite/@id'):
			pos = ref.find('CITEREF')
			if pos >= 0:
				list_refs.add(ref[pos:])

			# Отлов красных ошибок как в ст.  "Казаки" не получается
			# for undefined_ref in parsed_html.cssselect('li span.mw-ext-cite-error'):
			# for undefined_ref in parsed_html.cssselect('span.error'):
			# for undefined_ref in parsed_html.cssselect('span').text:
			# t = [undefined_ref for undefined_ref in parsed_html.xpath('//li[@id=cite_note-sol5_2_3-35]')]
			# t = parsed_html.cssselect('li')
			# t = [undefined_ref for undefined_ref in parsed_html.cssselect('li#cite_note-sol5_2_3-35')]
			# t = [undefined_ref for undefined_ref in parsed_html.xpath('//span/text')]
			# for undefined_ref in parsed_html.xpath('//span').text:
			# if 'Ошибка в сносках' in undefined_ref.text

		# сравнение списков сносок и примечаний
		err_refs = list_sfns - list_refs
		# Если в статье есть некорректные сноски без целевых примечаний
		if err_refs:
			errrefs = {}
			for citeref in err_refs:
				errrefs[citeref] = ref_calls[citeref]
			self.list_pages_with_referrors[title] = errrefs
			print(u'Страница № {}: {}'.format(pages_count_cur, title))
			print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(self.list_pages_with_referrors[title]))


	def make_listpages_tpls_transcludes(self, tpls_like_sfns_names, filename_tpls_transcludes):
		from wikiapi import get_list_transcludes_of_tpls

		if not self.get_from_file_only:
			self.list_transcludes = get_list_transcludes_of_tpls(tpls_like_sfns_names)
			file_savelines(filename_tpls_transcludes, self.list_transcludes)
		else:
			self.list_transcludes = file_readlines_in_set(filename_tpls_transcludes)

	def make_listpages_with_referrors(self):
		pages_count = len(self.list_transcludes)
		print('Всего страниц: {}.'.format(pages_count))
		pages_count_cur = pages_count

		for title in self.list_transcludes:
			print(title)
			page = find_cites_on_page(title, pages_count_cur)
			self.list_pages_with_referrors[title] = page.full_errrefs
			# self.collect_refs(title, pages_count_cur)
			pages_count_cur -= 1


class find_cites_on_page:

	title = ''
	parsed_html = ''
	pages_count_cur = 0
	list_sfns = set()
	list_refs = set()
	ref_calls = {}
	full_errrefs = {}

	def __init__(self, title, pages_count_cur):
		# from wikiapi import page_html_parse
		self.parsed_html = page_html_parse(title)  # html из url
		# parsed_html = html.fromstring(file_textread('test_html.html'))  # html из файла для тестов
		self.pages_count_cur = pages_count_cur

	def find_sfns_on_page(self):
		# for li in parsed_html.cssselect('li[href*="CITEREF"]'):
		for eref in self.parsed_html.cssselect('span.reference-text a[href*="CITEREF"]'):
			href = eref.get('href')
			pos = href.find('CITEREF')
			if pos >= 0:
				href_cut = href[pos:]
				self.list_sfns.add(href_cut)
				# link_to_sfn ссылка на sfn-сноску
				# print(href)
				try:
					link_to_sfn = self.parsed_html.xpath(
						"//li[@id]/span/a[@href='{href}']/ancestor::li[contains(@id,'{link_to_sfn}')][1]/@id".format(
							href=href, link_to_sfn='cite_note'))[0]
				except IndexError:
					try:
						link_to_sfn = self.parsed_html.xpath(
								"//li[@id]/span/cite/a[@href='{href}']/ancestor::li[contains(@id,'{link_to_sfn}')][1]/@id".format(
										href=href, link_to_sfn='cite_note'))[0]
					except IndexError:
						link_to_sfn = '#Примечания'

				self.ref_calls[href_cut] = {'text': eref.text, 'link_to_sfn': str(link_to_sfn)}

	def find_refs_on_page(self):
		for xpath in ['//span[@class="citation"]/@id', '//cite/@id']:
			find_refs_on_page_(xpath)

	def find_refs_on_page_(self, xpath):
		for ref in self.parsed_html.xpath(xpath):
			pos = ref.find('CITEREF')
			if pos >= 0:
				self.list_refs.add(ref[pos:])

	def compare_refs(self):
		# Отлов красных ошибок как в ст.  "Казаки" не получается
		# for undefined_ref in parsed_html.cssselect('li span.mw-ext-cite-error'):
		# for undefined_ref in parsed_html.cssselect('span.error'):
		# for undefined_ref in parsed_html.cssselect('span').text:
		# t = [undefined_ref for undefined_ref in parsed_html.xpath('//li[@id=cite_note-sol5_2_3-35]')]
		# t = parsed_html.cssselect('li')
		# t = [undefined_ref for undefined_ref in parsed_html.cssselect('li#cite_note-sol5_2_3-35')]
		# t = [undefined_ref for undefined_ref in parsed_html.xpath('//span/text')]
		# for undefined_ref in parsed_html.xpath('//span').text:
		# if 'Ошибка в сносках' in undefined_ref.text

		# сравнение списков сносок и примечаний
		err_refs = self.list_sfns - self.list_refs
		# Если в статье есть некорректные сноски без целевых примечаний
		if err_refs:
			self.full_errrefs = {}
			for citeref in err_refs:
				self.full_errrefs[citeref] = self.ref_calls[citeref]
			# self.list_pages_with_referrors[self.title] = self.full_errrefs
			print(u'Страница № {}: {}'.format(self.pages_count_cur, self.title))
			# print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(self.list_pages_with_referrors[self.title]))
			print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(self.full_errrefs))
