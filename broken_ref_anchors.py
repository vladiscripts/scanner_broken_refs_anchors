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
from make_list_pages_with_referrors import *


name_of_warning_tpl_ = 'ошибки сносок'

names_of_tpls_like_sfns = (['sfn', 'sfn0', 'Sfn-1',
 'Harvard citation', 'Harv',
'Harvard citation no brackets', 'Harvnb', 'Harvsp',
'Harvcol', 'Harvcoltxt', 'Harvcolnb', 'Harvrefcol'])
# не работает с шаблонами не создающими ссылки 'CITEREF':  '-1'
# names_of_tpls_like_sfns = 'Вершины Каменного Пояса'

list_transcludes_of_warningtemple = 'list_uses_warningtpl.txt'

# filename = r"d:\home\scripts.my\4wiki\\" + filename
# filename = 'sfn0.txt'
filename_listpages_errref = 'file_listpages_errref.txt'
filename_tpls_transcludes = 'list_tpls_transcludes.txt'

# list_pages_with_referrors = {}


def remove_tpl_from_changed_pages(tplname, list_with_err):
	global list_pages_with_referrors
	list_transcludes = file_readlines_in_set('list_uses_warningtpl.txt')
	list_with_err = set([title for title in list_pages_with_referrors])
	listpages_for_remove = list_transcludes - list_with_err
	remove_tpl_from_pages(tplname, listpages_for_remove)



referrors = make_listpage_referrors(names_of_tpls_like_sfns, filename_tpls_transcludes)
list_transcludes = referrors.list_transcludes
list_pages_with_referrors = referrors.list_pages_with_referrors
pass

if len(list_pages_with_referrors) > 0:
	file_savelines(filename_listpages_errref, list_pages_with_referrors)

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
