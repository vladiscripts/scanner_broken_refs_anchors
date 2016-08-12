# -*- coding: utf-8  -*-


def collect_refs(title, parsed_html, pages_count_cur, list_pages_with_referrors):
	list_sfns = set()
	list_refs = set()
	ref_calls = {}

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
		list_pages_with_referrors[title] = errrefs
		print(u'Страница № {}: {}'.format(pages_count_cur, title))
		print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(list_pages_with_referrors[title]))


def make_list_pages_with_referrors(tpls_like_sfns_names):
	from wikiapi import get_list_transcludes_of_tpls

	list_pages_with_referrors = {}

	get_list_transcludes_of_tpls(tpls_like_sfns_names)
	# arr_listpages = readlines_file_in_set(file_listpages_transcludes_of_sfntpls)
	# self.arr_listpages = ['Семёнов, Григорий Михайлович']   # тест отдельных страниц

	pages_count = len(arr_listpages)
	print('Всего страниц: {}.'.format(pages_count))
	pages_count_cur = pages_count

	for title in arr_listpages:
		# html из url
		# page = wikiapi.wikiapi_works(title)
		# page_wikicode = page.html_parsed()
		parsed_html = wikiapi.page_html_parse(title)
		# # connect = wikiapi.wikiconnect()
		# page = wikiapi.wikiapi_works(self.title)
		# parsed_html = html.fromstring(page.get_html())

		# html из файла для тестов
		# htmlpage = open('test_html.html', encoding='utf-8').read()
		# parsed_html = html.fromstring(htmlpage)

		# self.list_pages_with_referrors[title] = self.collect_refs(title, pages_count_cur)
		collect_refs(title, parsed_html, pages_count_cur, list_pages_with_referrors)
		pages_count_cur = pages_count_cur - 1

	# for ref in ref_calls:
	# parsed_html.xpath('//a/@href=' + ref_call)
	# print('Ошибочные сноски: <a href={}>{}</a>)'.format(ref[0], ref[1]))


	# запись исходной страниц из url в файл. urlopen берёт в byte-формате, request в str-формате
	# filename = 'pagecontent.txt'
	# f = open(filename, 'w', encoding='utf-8')
	# # f = open(filename, 'bw')
	# f.write(pagecontent)
	# f.close()

	return list_pages_with_referrors
