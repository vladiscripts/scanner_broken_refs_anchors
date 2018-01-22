# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from lxml.html import tostring
import re

tag_a = re.compile(r'<a [^>]*>(.*?)</a>', re.DOTALL)


class ScanRefsOfPage:
	def __init__(self, parsed_html):
		self.list_sfns = set()
		self.list_citations = set()
		self.all_sfn_info_of_page = []
		self.err_refs = []

		self.parsed_html = parsed_html
		self.find_sfns_on_page()
		self.find_citations_on_page()
		self.compare_refs()

	def find_sfns_on_page(self):
		""" Список сносок из раздела 'Примечания' """
		try:
			for li in self.parsed_html.cssselect("ol.references li[id^='cite']"):
				for a in li.cssselect("span.reference-text a[href^='#CITEREF']"):
					aText = tag_a.search(str(tostring(a, encoding='unicode'))).group(1)
					idRef = a.attrib['href'].lstrip('#')
					self.list_sfns.add(idRef)
					self.all_sfn_info_of_page.append(
						{'citeref': idRef, 'text': aText, 'link_to_sfn': str(li.attrib['id'])})

		except Exception as error:
			# self.error_print(error)
			pass

	def find_citations_on_page(self):
		""" Список id библиографии """
		try:
			for cite in ['span.citation[id^="CITEREF"]', 'cite[id^="CITEREF"]', 'span[id^="CITEREF"]']:
				for e in self.parsed_html.cssselect(cite):
					self.list_citations.add(e.attrib['id'])

		except Exception as error:
			# self.error_print(error)
			pass

	def compare_refs(self):
		""" Разница списков сносок с имеющейся библиографией. Возращает: self.full_errrefs """
		# Список сносок с битыми ссылками, из сравнения списков сносок и примечаний
		err_refs = self.list_sfns - self.list_citations
		if err_refs:
			self.err_refs = []
			for citeref_bad in sorted(err_refs):
				it_sfn_double = False
				for sfn in self.all_sfn_info_of_page:
					if citeref_bad == sfn['citeref'] and not it_sfn_double:
						self.err_refs.append(sfn)
						# session.add(Ref(self.page_id, sfn['citeref'], sfn['link_to_sfn'], sfn['text']))
						it_sfn_double = True

# def error_print(self, error):
# 	error_text = 'Error "{}" on parsing footnotes of page "{}"'.format(error
# 																	   # , self.title
# 																	   )
# 	print(error_text)
# 	file_savelines(filename_error_log, error_text)
