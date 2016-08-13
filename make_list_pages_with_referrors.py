# -*- coding: utf-8  -*-
import wikiapi
from commons import *

class make_listpage_referrors:

	list_pages_transcludes_of_tpls = []
	list_pages_with_referrors = {}

	def __init__(self, tpls_like_sfns_names, filename_tpls_transcludes):
		get_from_file_only = True  # Брать список из файла, или из wiki базы данных
		self.make_listpages_tpls_transcludes(tpls_like_sfns_names, filename_tpls_transcludes, get_from_file_only)
		self.make_listpages_with_referrors()
		pass

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
				link_to_sfn = parsed_html.xpath("//li[@id]/span/a[@href='{href}']/ancestor::li[contains(@id,'{link_to_sfn}')][1]/@id".format(href=href, link_to_sfn='cite_note'))[0]
				ref_calls[href_cut] = {'text': eref.text, 'link_to_sfn': str(link_to_sfn)}
		# / parent::
		for ref in parsed_html.xpath('//span[@class="citation"]/@id'):
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

	def make_listpages_tpls_transcludes(self, tpls_like_sfns_names, filename_tpls_transcludes, get_from_file_only=False):
		from wikiapi import get_list_transcludes_of_tpls

		if not get_from_file_only:
			self.list_pages_transcludes_of_tpls = get_list_transcludes_of_tpls(tpls_like_sfns_names)
			file_savelines(filename_tpls_transcludes, self.list_pages_transcludes_of_tpls)
		else:
			self.list_pages_transcludes_of_tpls = file_readlines_in_set(filename_tpls_transcludes)
		# self.arr_listpages = ['Семёнов, Григорий Михайлович']   # тест отдельных страниц

	def make_listpages_with_referrors(self):
		pages_count = len(self.list_pages_transcludes_of_tpls)
		print('Всего страниц: {}.'.format(pages_count))
		pages_count_cur = pages_count

		for title in self.list_pages_transcludes_of_tpls:
			print(title)
			self.collect_refs(title, pages_count_cur)
			pages_count_cur -= 1
