# -*- coding: utf-8  -*-
# PYTHON_VERSION = 3  # для версии 2 отключить эту строку или сменить
# import mwparserfromhell
# import pywikibot
# from pywikibot import pagegenerators
# from my import *

# import json
# if PYTHON_VERSION == 3:
# 	from urllib.parse import urlencode, quote  # python 3
# else:
# 	from urllib import urlencode, quote  # python 2.7
# 	import codecs
# from urllib.request import urlopen
# import mwparserfromhell
from lxml import html
import re
# from lxml.etree import fromstring
# from grab import Grab
from commons import *
import wikiapi

warning_tpl_name = 'ошибки сносок'

"""
получить список включений шаблонов сносок
сделать список
получить список включений шаблона
удалить шаблон из разницы = список включений шаблона - новый список страниц с проблемами
"""
list_transcludes_of_warningtemple = 'list_uses_warningtpl.txt'

# filename = r"d:\home\scripts.my\4wiki\\" + filename
# filename = 'sfn0.txt'
file_listpages = 'sfn1.txt'

list_pages_with_referrors = {}
err_refs = set()

# list_tpls = (['sfn', 'sfn0'])  # шаблоны
# list_tpls = (['Вершины Каменного Пояса'])


def remove_template(tpl, listpages):
	pass


def remove_tpl_from_changed_pages(warning_tpl_name, ):
	global err_refs
	list_transcludes = readlines_file_in_set('list_uses_warningtpl.txt')
	listpages_for_remove = list_transcludes - err_refs
	remove_template(warning_tpl_name, listpages_for_remove)


def collect_refs(title, parsed_html, pages_count_cur):
	global list_pages_with_referrors, err_refs
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

		# for undefined_ref in parsed_html.cssselect('li span.mw-ext-cite-error'):
		# for undefined_ref in parsed_html.cssselect('span.error'):
		# for undefined_ref in parsed_html.cssselect('span').text:
		# t = [undefined_ref for undefined_ref in parsed_html.xpath('//li[@id=cite_note-sol5_2_3-35]')]
		# t = parsed_html.cssselect('li')
		# t = [undefined_ref for undefined_ref in parsed_html.cssselect('li#cite_note-sol5_2_3-35')]
		# t = [undefined_ref for undefined_ref in parsed_html.xpath('//span/text')]
		# for undefined_ref in parsed_html.xpath('//span').text:
		# if 'Ошибка в сносках' in undefined_ref.text
		#
		# pos = ref.find('CITEREF')
		# if pos >= 0:
		# 	list_refs.add(ref[pos:])

		# < sup		id = "cite_ref-1"		class ="reference" >

	# print('list_sfns:')
	# print(list_sfns)
	# print('list_refs:')
	# print(list_refs)
	err_refs = list_sfns - list_refs
	# Если в статье есть некорректные сноски
	if err_refs:
		errrefs = {}
		for citeref in err_refs:
			errrefs[citeref] = ref_calls[citeref]
		list_pages_with_referrors[title] = errrefs
		print(u'Страница № {}: {}'.format(pages_count_cur, title))
		print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(list_pages_with_referrors[title]))


def make_list_pages_with_referrors(file_listpages):
	arr_listpages = readlines_file_in_set(file_listpages)
	# self.arr_listpages = ['Семёнов, Григорий Михайлович']   # тест отдельных страниц

	pages_count = len(arr_listpages)
	print('Всего страниц: {}.'.format(pages_count))
	pages_count_cur = pages_count

	for title in arr_listpages:
		# html из url
		# page = wikiapi.wikiapi_works(title)
		# page_wikicode = page.html_parsed()
		parsed_html = wikiapi.page_html_parsed(title)
		# # connect = wikiapi.wikiconnect()
		# page = wikiapi.wikiapi_works(self.title)
		# parsed_html = html.fromstring(page.get_html())

		# html из файла для тестов
		# htmlpage = open('test_html.html', encoding='utf-8').read()
		# parsed_html = html.fromstring(htmlpage)

		# self.list_pages_with_referrors[title] = self.collect_refs(title, pages_count_cur)
		collect_refs(title, parsed_html, pages_count_cur)
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



make_list_pages_with_referrors(file_listpages)

print('list_pages_with_referrors')
print(list_pages_with_referrors)
# {'страница':  {'CITEREF.D0.92.D0.B0.D1.81.D0.B8.D0.BB.D1.8C.D0.B5.D0.B22012': 'Васильев, 2012',  ... }}







summary = 'bot hello'
pagelist = [
	'Участник:Vladis13/статья',
]

list_pages_with_referrors = {'Участник:Vladis13/статья': {'CITEREFKiernan2003':            'Kiernan, 2003',
														  'CITEREFMarks':                  'Marks',
														  'CITEREFAditjondro1999':         'Aditjondro, 1999',
														  'CITEREFJean_Gelman_Taylor2003': 'Jean Gelman Taylor, 2003',
														  'CITEREFAditjondro1998':         'Aditjondro, 1998',
														  'CITEREFHorner2001':             'Horner, 2001',
														  'CITEREFFriend2003':             'Friend, 2003',
														  'CITEREFVickers2003':            'Vickers, 2003',
														  'CITEREFBudiardjo_and_Liong':    'Budiardjo and Liong',
														  'CITEREFBudiardjo1984':          'Budiardjo, 1984',
														  'CITEREFJean_Gelman_Taylor':     'Jean Gelman Taylor'
														  }}

# # connect_properties = login_and_token(baseurl, username, password)
# # r4_text = edit(baseurl, title, message, summary, connect_properties)
# r4_text = edit(title, message, summary)
# print(r4_text)
# connect = wikiconnect()
# if not connect
#
# for title in list_pages_with_referrors:
# 	replacetext_old = '== Описание герба =='
# 	refs_of_page = list_pages_with_referrors[title]
# 	refs_str = '|'.join([refs_of_page.get(ref) for ref in refs_of_page])
# 	replacetext_new = '\n' + '{{' + post_tpl_name + '|' + refs_str + '}}'
#
# 	page = wikiapi.wikiapi_works(title)
# 	# page.replace_text_page(replacetext_old, replacetext_new, summary)
# 	page.save_changed_text(replacetext_old, replacetext_new, summary)
# 	del page
# 	print(page)

regexp_compiled = re.compile(r'{{\s*' + warning_tpl_name + r'\s*(\|.*?)?}}', re.IGNORECASE)

for title in list_pages_with_referrors:
	refs_of_page = list_pages_with_referrors[title]
	refs_str = '|'.join([refs_of_page.get(ref) for ref in refs_of_page])
	repl = '{{' + warning_tpl_name + '|' + refs_str + '}}'
	repl = '<code><nowiki>' + repl + '</nowiki></code>'  # обёртка в <nowiki>
	repl = '\n' + repl

	page = wikiapi.wikiapi_works(title)

	# page.replace_or_add_text_regexp(regexp_compiled, repl, summary)
	# def replace_or_add_text_regexp(self, regexp_compiled, replace, summary=''):  #add_br_before=True,

	page_wikicode = page.get_wikicode()
	if page:  # text = get_wikicodet(title)
		searched = repl.find(page_wikicode)  # проверка на наличие этого шабона с дубликатными refs
		if searched >= 0:
			print('уже есть в тексте')
			pass
		else:
			searched = regexp_compiled.search(page_wikicode)  # проверка на наличие шаблона вообще
			if searched:
				print('replace_text')
				newtext = regexp_compiled.sub(repl, page_wikicode)
				result = page.save(newtext, 'replace', summary)
			else:
				print('appendtext')
				result = page.save(repl, 'appendtext', summary)
			print(result)
			print('ok')

	# page_wikicode = page.get_wikicode()
	# searched = regexp_compiled.search(page_wikicode)
	# if searched:
	# 	_regexp
	# 	print('replace_text')
	# 	newtext_page = regexp_compiled.sub(repl, page_wikicode)
	# 	page.replace_text(page_wikicode, newtext_page, summary)
	# else:
	# 	print('appendtext')
	# 	page.add_text(repl, 'appendtext', summary)
	print('ok')



#
# import add_different_text_2_per_listpages_pwb
#
#
# generator = ["Участник:Vladis13/капица"]
# addText = tpl
# summary = "tpl"
#
# for page in generator:
# 	(text, newtext, always) = add_text(page, addText, summary, regexSkip,
# 									   regexSkipUrl, always, up, True,
# 									   reorderEnabled=reorderEnabled,
# 									   create=talkPage)






# # запись списка в файл.
# filename = 'list_err_pages.txt'
# if python_version == 3:
# 	f = open(filename, 'w', encoding='utf-8')  # python 3
# else:
# 	f = codecs.open(filename, 'w', encoding='utf-8')  # python 2.7
# f.writelines("%s\n" % i for i in list_pages_with_referrors)
# f.close()
