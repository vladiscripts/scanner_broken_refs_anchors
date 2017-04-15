# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import re
from lxml.html import tostring
from config import *
from wikiapi import page_html_parse
from vladi_commons import file_savelines

tag_a = re.compile(r'<a [^>]*>(.*?)</a>', re.DOTALL)


class ScanRefsOfPage:
	def __init__(self, page_id, title):
		self.list_sfns = set()
		self.list_refs = set()
		self.all_sfn_info_of_page = []
		self.full_errrefs = []

		self.page_id = page_id
		self.title = title
		self.parsed_html = page_html_parse(self.title)  # html из url
		self.find_sfns_on_page()
		self.find_refs_on_page()
		self.compare_refs()

	def find_sfns_on_page(self):
		try:
			p_ref_list = self.parsed_html.xpath("//ol[@class='references']/li")
			for li in p_ref_list:
				span_list = li.xpath("./span[@class='reference-text']")
				for span in span_list:
					a_list = span.xpath("./descendant::a[contains(@href,'CITEREF')]")
					for a in a_list:
						a_text = tag_a.search(str(tostring(a, encoding='unicode'))).group(1)
						href_cut = self.cut_href(a.attrib['href'])
						self.list_sfns.add(href_cut)
						self.all_sfn_info_of_page.append(
							{'citeref': href_cut, 'text': a_text, 'link_to_sfn': str(li.attrib['id'])})

		except Exception as error:
			self.error_print(error)

	def find_refs_on_page(self):
		try:
			for xpath in ['//span[@class="citation"]/@id', '//cite/@id']:
				for href in self.parsed_html.xpath(xpath):
					self.list_refs.add(self.cut_href(href))

		except Exception as error:
			self.error_print(error)

	def compare_refs(self):
		# список сносок с битыми ссылками, из сравнения списков сносок и примечаний
		err_refs = self.list_sfns - self.list_refs
		# Если в статье есть некорректные сноски без целевых примечаний
		if err_refs:
			self.full_errrefs = []
			for citeref_bad in sorted(err_refs):
				it_sfn_double = False
				for sfn in self.all_sfn_info_of_page:
					if citeref_bad == sfn['citeref'] and not it_sfn_double:
						self.full_errrefs.append(sfn)
						# db.session.add(db.Ref(self.page_id, sfn['citeref'], sfn['link_to_sfn'], sfn['text']))
						it_sfn_double = True

	def error_print(self, error):
		error_text = 'Error "{}" on parsing footnotes of page "{}"'.format(error, self.title)
		print(error_text)
		file_savelines(filename_error_log, error_text)

	def cut_href(self, href):
		pos = href.find('CITEREF')
		if pos >= 0:
			return href[pos:]
		return False
