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
# from lxml.etree import fromstring
# from grab import Grab
from constans import *
import wikiapi

category_bad_sfn = '[[Категория:Имеются нерабочие якоря в сносках]]'
post_tpl_name = 'ошибки сносок'

# filename = r"d:\home\scripts.my\4wiki\\" + filename
# filename = 'sfn0.txt'
filename = 'sfn1.txt'

list_pages_with_referrors = {}


def collect_refs(parsed_html, title):
	list_sfns = set()
	list_refs = set()
	ref_calls = {}

	# for li in parsed_html.cssselect('li[href*="CITEREF"]'):
	for eref in parsed_html.cssselect('span.reference-text a[href*="CITEREF"]'):
		href = eref.get('href')
		pos = href.find('CITEREF')
		if pos >= 0:
			cut_href = href[pos:]
			list_sfns.add(cut_href)
			ref_calls[cut_href] = eref.text

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

	# print('list_sfns:')
	# print(list_sfns)
	# print('list_refs:')
	# print(list_refs)
	global list_pages_with_referrors
	err_refs = list_sfns - list_refs
	if err_refs:
		errrefs = {}
		for citeref in err_refs:
			errrefs[citeref] = ref_calls[citeref]
		list_pages_with_referrors[title] = errrefs
		print(u'Страница № {}: {}'.format(pages_count + 1, title))
		print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(list_pages_with_referrors[title]))
	return errrefs


if PYTHON_VERSION == 3:
	arr_listpages = set([line.rstrip() for line in open(filename, encoding='utf-8')])  # python 3
else:
	with codecs.open(filename, 'r', encoding='utf-8') as f:  # python 2.7
		arr_listpages = [line.rstrip() for line in f]  # python 2.7
# arr_listpages = ['Семёнов, Григорий Михайлович']   # тест отдельных страниц

# list_tpls = (['sfn', 'sfn0'])  # шаблоны
# list_tpls = (['Вершины Каменного Пояса'])

pages_count = len(arr_listpages)
print('Всего страниц: {}.'.format(pages_count))

for title in arr_listpages:
	pages_count = pages_count - 1

	pagehtml = """<html><body>
<h2><span class="mw-headline" id=".D0.9B.D0.B8.D1.82.D0.B5.D1.80.D0.B0.D1.82.D1.83.D1.80.D0.B0">Литература</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=%D0%9F%D0%B8%D1%80%D0%B0%D0%B7%D0%B8%D0%B4%D0%BE%D0%BB&amp;action=edit&amp;section=3" title="Редактировать раздел «Литература»">править</a><span class="mw-editsection-bracket">]</span></span></h2>
<p><span class="citation" id="CITEREF.D0.9C.D0.B0.D1.88.D0.BA.D0.BE.D0.B2.D1.81.D0.BA.D0.B8.D0.B92005"><i><a href="/wiki/%D0%9C%D0%B0%D1%88%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%B8%D0%B9,_%D0%9C%D0%B8%D1%85%D0%B0%D0%B8%D0%BB_%D0%94%D0%B0%D0%B2%D1%8B%D0%B4%D0%BE%D0%B2%D0%B8%D1%87" title="Машковский, Михаил Давыдович">Машковский М. Д.</a></i> Лекарственные средства.&#160;— 15-е изд.&#160;— <span style="border-bottom:1px dotted gray; cursor:default" title="Москва">М</span>.: Новая Волна, 2005.&#160;— 1200&#160;с.&#160;— <a href="/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%98%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%D0%B8_%D0%BA%D0%BD%D0%B8%D0%B3/5786402037" class="internal mw-magiclink-isbn">ISBN 5-7864-0203-7</a>.</span></p>
<h2><span class="mw-headline" id=".D0.A1.D1.81.D1.8B.D0.BB.D0.BA.D0.B8">Ссылки</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=%D0%9F%D0%B8%D1%80%D0%B0%D0%B7%D0%B8%D0%B4%D0%BE%D0%BB&amp;action=edit&amp;section=4" title="Редактировать раздел «Ссылки»">править</a><span class="mw-editsection-bracket">]</span></span></h2>
<ul>
<li><span class="citation" id="CITEREF.D0.9C.D0.B0.D1.88.D0.BA.D0.BE.D0.B2.D1.81.D0.BA.D0.B8.D0.B92010"><a rel="nofollow" class="external text" href="http://mashkovsky.ru/tiki-index.php?page=Пиразидол">Пиразидол</a>&#160;// Лекарственные средства&#160;/ <a href="/wiki/%D0%9C%D0%B0%D1%88%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%B8%D0%B9,_%D0%9C%D0%B8%D1%85%D0%B0%D0%B8%D0%BB_%D0%94%D0%B0%D0%B2%D1%8B%D0%B4%D0%BE%D0%B2%D0%B8%D1%87" title="Машковский, Михаил Давыдович">М. Д. Машковский</a>.&#160;— <a rel="nofollow" class="external text" href="http://mashkovsky.ru/">Справочник Машковского on-line</a>.</span></li>
<li><span class="citation" id="CITEREF.D0.94.D1.83.D0.B1.D0.BD.D0.B8.D1.86.D0.BA.D0.B0.D1.8F.2C_.D0.92.D0.BE.D0.BB.D0.B5.D0.BB.D1.8C2003"><i>Дубницкая Э. Б., Волель Б. А.</i>&#160;<a rel="nofollow" class="external text" href="http://www.consilium-medicum.com/media/psycho/03_03/106.shtml">Терапия депрессий непсихотического уровня (опыт применения пиразидола: эффективность и безопасность)</a>&#160;// Психиатрия и психофармакотерапия.&#160;— 2003.&#160;— <span style="white-space: nowrap;">Т. 05</span>, <span style="white-space: nowrap;">№ 3</span>.</span></li>
<li><span class="citation" id="CITEREF.D0.9C.D0.BE.D1.80.D0.BE.D0.B7.D0.BE.D0.B22002"><i>Морозов П. В.</i>&#160;<a rel="nofollow" class="external text" href="http://www.consilium-medicum.com/media/psycho/02_06/250.shtml">Пиразидол&#160;— эффективный отечественный антидепрессант</a>&#160;// Психиатрия и психофармакотерапия.&#160;— 2002.&#160;— <span style="white-space: nowrap;">Т. 04</span>, <span style="white-space: nowrap;">№ 6</span>.</span></li>
</ul>
<h2><span class="mw-headline" id=".D0.9F.D1.80.D0.B8.D0.BC.D0.B5.D1.87.D0.B0.D0.BD.D0.B8.D1.8F">Примечания</span><span class="mw-editsection"><span class="mw-editsection-bracket">[</span><a href="/w/index.php?title=%D0%9F%D0%B8%D1%80%D0%B0%D0%B7%D0%B8%D0%B4%D0%BE%D0%BB&amp;action=edit&amp;section=5" title="Редактировать раздел «Примечания»">править</a><span class="mw-editsection-bracket">]</span></span></h2>
<div class="references-small" style="">
<ol class="references">
<li id="cite_note-moroz-1"><b><a href="#CITEREFmistaketest">CITEREFmistaketest</a><a href="#cite_ref-moroz_1-0">↑</a></b> <span class="reference-text"><a href="#CITEREF.D0.9C.D0.BE.D1.80.D0.BE.D0.B7.D0.BE.D0.B22002">Морозов, 2002</a>.</span></li>
<li id="cite_note-m94-2"><b><a href="#cite_ref-m94_2-0">↑</a></b> <span class="reference-text"><a href="#CITEREF.D0.9C.D0.B0.D1.88.D0.BA.D0.BE.D0.B2.D1.81.D0.BA.D0.B8.D0.B92005">Машковский, 2005</a>, с. 94.</span></li>
<li id="cite_note-3"><b><a href="#cite_ref-3">↑</a></b> <span class="reference-text"><span class="citation"><i>Андреева Н.И. и др.</i>&#160;Отечественные антидепрессанты: II. Пиразидол (Пирлиндол)&#160;// Хим.-фарм. журн.&#160;— 2000.&#160;— <span style="white-space: nowrap;">№ 9</span>.&#160;— <span style="white-space: nowrap;">С. 12</span>.</span></span></li>
<li id="cite_note-.D0.91.D1.8B.D0.BA.D0.BE.D0.B2.2C_.D0.91.D0.B5.D0.BA.D0.BA.D0.B5.D1.80-4"><span class="mw-cite-backlink">↑ <a href="#cite_ref-.D0.91.D1.8B.D0.BA.D0.BE.D0.B2.2C_.D0.91.D0.B5.D0.BA.D0.BA.D0.B5.D1.80_4-0"><sup><i><b>1</b></i></sup></a> <a href="#cite_ref-.D0.91.D1.8B.D0.BA.D0.BE.D0.B2.2C_.D0.91.D0.B5.D0.BA.D0.BA.D0.B5.D1.80_4-1"><sup><i><b>2</b></i></sup></a></span> <span class="reference-text"><span class="citation"><i>Быков Ю. В., Беккер Р. А., Резников М. К.</i> Резистентные депрессии. Практическое руководство.&#160;— Киев: Медкнига, 2013.&#160;— 400&#160;с.&#160;— <a href="/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%98%D1%81%D1%82%D0%BE%D1%87%D0%BD%D0%B8%D0%BA%D0%B8_%D0%BA%D0%BD%D0%B8%D0%B3/9789661597142" class="internal mw-magiclink-isbn">ISBN 978-966-1597-14-2</a>.</span></span></li>
</ol>
</div>


<!--  иные примечания с {{sfn0}} -->
<h2 id="mwxQ"> Примечания </h2>
<div class="small" id="mwxg"><div class="references-small " style="column-count:2;-moz-column-count:2;-webkit-column-count:2;" about="#mwt55" typeof="mw:Transclusion" data-mw="{&quot;parts&quot;:[{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;примечания&quot;,&quot;href&quot;:&quot;./Шаблон:примечания&quot;},&quot;params&quot;:{&quot;1&quot;:{&quot;wt&quot;:&quot;2&quot;}},&quot;i&quot;:0}}]}" id="mwxw">
<ol class="mw-references" typeof="mw:Extension/references" about="#mwt68" data-mw="{&quot;name&quot;:&quot;references&quot;,&quot;attrs&quot;:{}}">
<li about="#cite_note-1" id="cite_note-1"><a href="#cite_ref-1" rel="mw:referencedBy"><span class="mw-linkback-text">↑ </span></a> <span id="mw-reference-text-cite_note-1" class="mw-reference-text">Рисунок из книги: <i id="mwyA"><a rel="mw:WikiLink" href="./Науман,_Иоганн_Фридрих" title="Науман, Иоганн Фридрих" id="mwyQ">Naumann J. F.</a></i> Naturgeschichte der Vögel Mitteleuropas.&nbsp;— 1905.<span typeof="mw:Entity" id="mwyg">&nbsp;</span><span class="ref-info" title="на немецком языке " style="font-size:85%; cursor:help; color:#888;" id="mwyw">(нем.)</span> [Естественная история птиц Средней Европы.]</span></li><li about="#cite_note-2" id="cite_note-2"><a href="#cite_ref-2" rel="mw:referencedBy"><span class="mw-linkback-text">↑ </span></a> <span id="mw-reference-text-cite_note-2" class="mw-reference-text">Рисунок <span class="iw" data-title="Райт, Вильгельм фон" id="mwzA"><a rel="mw:WikiLink" href="./Райт,_Вильгельм_фон" title="Райт, Вильгельм фон" id="mwzQ">Вильгельма фон Райта</a><sup class="noprint" id="mwzg"><a rel="mw:ExtLink" href="https://en.wikipedia.org/wiki/Wilhelm von Wright" title="en:Wilhelm von Wright" id="mwzw"><span style="font-style:normal; font-weight:normal;" title="Wilhelm von Wright — версия статьи «Райт, Вильгельм фон» на английском языке" id="mw0A">[en]</span></a></sup></span>, 1810—1887) из книги:
<a rel="mw:WikiLink" href="./Воробьиные#CITEREFWright_et_al.1927.E2.80.941929" id="mw0Q">Wright <i id="mw0g">et al.</i>, 1927—1929</a>.</span></li>
<li about="#cite_note-3" id="cite_note-3"><a href="#cite_ref-3" rel="mw:referencedBy"><span class="mw-linkback-text">↑ </span></a> <span id="mw-reference-text-cite_note-3" class="mw-reference-text">Рисунок <span class="iw" data-title="Райт, Магнус фон" id="mw0w"><a rel="mw:WikiLink" href="./Райт,_Магнус_фон" title="Райт, Магнус фон" id="mw1A">Магнуса фон Райта</a><sup class="noprint" id="mw1Q"><a rel="mw:ExtLink" href="https://en.wikipedia.org/wiki/Magnus von Wright" title="en:Magnus von Wright" id="mw1g"><span style="font-style:normal; font-weight:normal;" title="Magnus von Wright — версия статьи «Райт, Магнус фон» на английском языке" id="mw1w">[en]</span></a></sup></span>, 1805—1868) из книги: <a rel="mw:WikiLink" href="./Воробьиные#CITEREFWright_et_al.1927.E2.80.941929" id="mw2A">Wright <i id="mw2Q">et al.</i>, 1927—1929</a>.</span></li>
<li about="#cite_note-4" id="cite_note-4"><a href="#cite_ref-4" rel="mw:referencedBy"><span class="mw-linkback-text">↑ </span></a> <span id="mw-reference-text-cite_note-4" class="mw-reference-text">Процесс приспособления организмов к обитанию вблизи человека; см., например:
<dl id="mw2g"><dd id="mw2w"> <span class="citation" about="#mwt25" typeof="mw:Transclusion" data-mw="{&quot;parts&quot;:[{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;cite web&quot;,&quot;href&quot;:&quot;./Шаблон:cite_web&quot;},&quot;params&quot;:{&quot;url&quot;:{&quot;wt&quot;:&quot;http://www.glossary.ru/cgi-bin/gl_find.cgi?ph=%D1%E8%ED%E0%ED%F2%F0%EE%EF%E8%E7%E0%F6%E8%FF&amp;action=%CF%EE%E8%F1%EA&quot;},&quot;title&quot;:{&quot;wt&quot;:&quot;Синантропизация&quot;},&quot;work&quot;:{&quot;wt&quot;:&quot;Входы: Антропогенное воздействие на природу&quot;},&quot;publisher&quot;:{&quot;wt&quot;:&quot;Глоссарий.ru; Web-and-Press&quot;},&quot;accessdate&quot;:{&quot;wt&quot;:&quot;2016-06-19&quot;},&quot;archiveurl&quot;:{&quot;wt&quot;:&quot;https://web.archive.org/web/20160619111042/http://www.glossary.ru/cgi-bin/gl_find.cgi?ph=%D1%E8%ED%E0%ED%F2%F0%EE%EF%E8%E7%E0%F6%E8%FF&amp;action=%CF%EE%E8%F1%EA&quot;},&quot;archivedate&quot;:{&quot;wt&quot;:&quot;2016-06-19&quot;}},&quot;i&quot;:0}}]}" id="mw3A"><a rel="mw:ExtLink" href="http://www.glossary.ru/cgi-bin/gl_find.cgi?ph=%D1%E8%ED%E0%ED%F2%F0%EE%EF%E8%E7%E0%F6%E8%FF&amp;action=%CF%EE%E8%F1%EA" id="mw3Q">Синантропизация</a>.<span typeof="mw:Entity" id="mw3g"> </span><i id="mw3w">Входы: Антропогенное воздействие на природу</i>.<span typeof="mw:Entity" id="mw4A"> </span> Глоссарий.ru; Web-and-Press.<span typeof="mw:Entity" id="mw4Q"> </span><small id="mw4g">Проверено 19 июня 2016.</small><span typeof="mw:Entity" id="mw4w"> </span><small id="mw5A"><a rel="mw:ExtLink" href="https://web.archive.org/web/20160619111042/http://www.glossary.ru/cgi-bin/gl_find.cgi?ph=%D1%E8%ED%E0%ED%F2%F0%EE%EF%E8%E7%E0%F6%E8%FF&amp;action=%CF%EE%E8%F1%EA" id="mw5Q">Архивировано из первоисточника 19 июня 2016</a>.</small></span></dd></dl></span></li>
<li about="#cite_note-5" id="cite_note-5"><a href="#cite_ref-5" rel="mw:referencedBy"><span class="mw-linkback-text">↑ </span></a> <span id="mw-reference-text-cite_note-5" class="mw-reference-text"><i id="mw5g">Иваницкий В. В.</i> Воробьи и родственные им группы зерноядных птиц: поведение, экология, эволюция.&nbsp;— <span style="border-bottom:1px dotted gray; cursor:default" title="Москва" about="#mwt33" typeof="mw:Transclusion" data-mw="{&quot;parts&quot;:[{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;М.&quot;,&quot;href&quot;:&quot;./Шаблон:М.&quot;},&quot;params&quot;:{},&quot;i&quot;:0}}]}" id="mw5w">М</span><span about="#mwt33" id="mw6A">.</span>: КМК Scientific Press, 1997.&nbsp;— С. 1—148.</span></li><li about="#cite_note-Balatsky-6" id="cite_note-Balatsky-6"><span rel="mw:referencedBy"><a href="#cite_ref-Balatsky_6-0"><span class="mw-linkback-text">1 </span></a><a href="#cite_ref-Balatsky_6-1"><span class="mw-linkback-text">2 </span></a></span> <span id="mw-reference-text-cite_note-Balatsky-6" class="mw-reference-text"><i id="mw6Q"><a rel="mw:WikiLink" href="./Балацкий,_Николай_Николаевич" title="Балацкий, Николай Николаевич" id="mw6g">Балацкий Н. Н.</a></i> <a rel="mw:ExtLink" href="http://www.balatsky.ru/Publications/70_p.htm" id="mw6w">Ревизия видов семейства Passeridae (Passeriformes, Aves) в Северной Палеарктике</a> // Русский орнитологический журнал.&nbsp;— 2001.&nbsp;— Экспресс-вып. 144.&nbsp;— С. 417—422.</span></li><li about="#cite_note-7" id="cite_note-7"><a href="#cite_ref-7" rel="mw:referencedBy"><span class="mw-linkback-text">↑ </span></a> <span id="mw-reference-text-cite_note-7" class="mw-reference-text"><a rel="mw:ExtLink" href="http://virt-collection.mypage.ru/unusual_monument/pamyatniki_vorobyam.html" id="mw7A">Памятники воробьям</a> // Клуб виртуальных коллекционеров</span></li>
</ol></div></div>

<h2 id="mw7Q"> Литература </h2>
<ul id="mw7g">
<li id="mw7w"> <i id="mw8A"><a rel="mw:WikiLink" href="./Второв,_Пётр_Петрович" title="Второв, Пётр Петрович" id="mw8Q">Второв П. П.</a>, <a rel="mw:WikiLink" href="./Дроздов,_Николай_Николаевич" title="Дроздов, Николай Николаевич" id="mw8g">Дроздов Н. Н.</a></i> <a rel="mw:ExtLink" href="http://zoomet.ru/vtor/vtorov_Fringillidae.html" id="mw8w">Семейства вьюрковые (Fringillidae) и воробьиные, или ткачиковые (Passeridae)</a> // <a rel="mw:ExtLink" href="http://zoomet.ru/vtor/vtorov_oglav.html" id="mw9A">Определитель птиц фауны СССР</a> / П.&nbsp;П.&nbsp;Второв, Н.&nbsp;Н.&nbsp;Дроздов.&nbsp;— <span style="border-bottom:1px dotted gray; cursor:default" title="Москва" about="#mwt56" typeof="mw:Transclusion" data-mw="{&quot;parts&quot;:[{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;М.&quot;,&quot;href&quot;:&quot;./Шаблон:М.&quot;},&quot;params&quot;:{},&quot;i&quot;:0}}]}" id="mw9Q">М</span><span about="#mwt56">.</span>: Просвещение, 1980. (Выложено на сайте <a rel="mw:ExtLink" href="http://zoomet.ru/" id="mw9g">«Методы изучения животных и среды их обитания».</a>)</li>
<li id="mw9w"> <i id="mw-A">Иванов А. И., Штегман Б. К.</i> 1978. <a rel="mw:ExtLink" href="http://birds.krasu.ru/txt/ord/ord_passer.shtml" id="mw-Q">Краткий определитель птиц СССР.</a>&nbsp;— Изд. 2-е, испр. и доп.&nbsp;— <span style="border-bottom:1px dotted gray; cursor:default;" title="Ленинград" about="#mwt58" typeof="mw:Transclusion" data-mw="{&quot;parts&quot;:[{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;Л.&quot;,&quot;href&quot;:&quot;./Шаблон:Л.&quot;},&quot;params&quot;:{},&quot;i&quot;:0}}]}" id="mw-g">Л.</span>: Наука, 1978.&nbsp;— 560 с.&nbsp;— (Определители по фауне СССР, издаваемые Зоологическим институтом АН СССР, 115).</li>
<li id="mw-w"> <i id="mw_A">Коблик Е. А.</i> <a rel="mw:ExtLink" href="http://www.apus.ru/site.xp/051057055124.html" id="mw_Q">Разнообразие птиц (по материалам экспозиции Зоологического музея МГУ).</a>&nbsp;— <span style="border-bottom:1px dotted gray; cursor:default" title="Москва" about="#mwt60" typeof="mw:Transclusion" data-mw="{&quot;parts&quot;:[{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;М.&quot;,&quot;href&quot;:&quot;./Шаблон:М.&quot;},&quot;params&quot;:{},&quot;i&quot;:0}}]}" id="mw_g">М</span><span about="#mwt60">.</span>: Издательство МГУ, 2001.&nbsp;— Ч. 4.</li>
<li id="mw_w"> <span class="citation" id="CITEREFWright_et_al.1927.E2.80.941929" about="#mwt61" typeof="mw:Transclusion" data-mw="{&quot;parts&quot;:[{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;h&quot;,&quot;href&quot;:&quot;./Шаблон:h&quot;},&quot;params&quot;:{&quot;1&quot;:{&quot;wt&quot;:&quot;Wright ''et al.''&quot;},&quot;2&quot;:{&quot;wt&quot;:&quot;1927—1929&quot;}},&quot;i&quot;:0}},&quot; ''&quot;,{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;iw&quot;,&quot;href&quot;:&quot;./Шаблон:iw&quot;},&quot;params&quot;:{&quot;1&quot;:{&quot;wt&quot;:&quot;Райт, Магнус фон&quot;},&quot;2&quot;:{&quot;wt&quot;:&quot;Wright M. von&quot;},&quot;3&quot;:{&quot;wt&quot;:&quot;&quot;},&quot;4&quot;:{&quot;wt&quot;:&quot;Magnus von Wright&quot;}},&quot;i&quot;:1}},&quot;, &quot;,{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;iw&quot;,&quot;href&quot;:&quot;./Шаблон:iw&quot;},&quot;params&quot;:{&quot;1&quot;:{&quot;wt&quot;:&quot;Райт, Фердинанд фон&quot;},&quot;2&quot;:{&quot;wt&quot;:&quot;Wright F. von&quot;},&quot;3&quot;:{&quot;wt&quot;:&quot;&quot;},&quot;4&quot;:{&quot;wt&quot;:&quot;Ferdinand von Wright&quot;}},&quot;i&quot;:2}},&quot;, &quot;,{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;iw&quot;,&quot;href&quot;:&quot;./Шаблон:iw&quot;},&quot;params&quot;:{&quot;1&quot;:{&quot;wt&quot;:&quot;Райт, Вильгельм фон&quot;},&quot;2&quot;:{&quot;wt&quot;:&quot;Wright W. von&quot;},&quot;3&quot;:{&quot;wt&quot;:&quot;&quot;},&quot;4&quot;:{&quot;wt&quot;:&quot;Wilhelm von Wright&quot;}},&quot;i&quot;:3}},&quot;, [[Лённберг, Эйнар|Lönnberg E.]]'' Svenska fåglar, efter naturen och på sten ritade: tre volymer.&nbsp;— 2:a upplagan.&nbsp;— 1927—1929.&quot;,{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;ref-sv&quot;,&quot;href&quot;:&quot;./Шаблон:ref-sv&quot;},&quot;params&quot;:{},&quot;i&quot;:4}}]}"> <i><span class="iw" data-title="Райт, Магнус фон"><a rel="mw:WikiLink" href="./Райт,_Магнус_фон" title="Райт, Магнус фон">Wright M. von</a><sup class="noprint"><a rel="mw:ExtLink" href="https://en.wikipedia.org/wiki/Magnus von Wright" title="en:Magnus von Wright"><span style="font-style:normal; font-weight:normal;" title="Magnus von Wright — версия статьи «Райт, Магнус фон» на английском языке">[en]</span></a></sup></span>, <span class="iw" data-title="Райт, Фердинанд фон"><a rel="mw:WikiLink" href="./Райт,_Фердинанд_фон" title="Райт, Фердинанд фон">Wright F. von</a><sup class="noprint"><a rel="mw:ExtLink" href="https://en.wikipedia.org/wiki/Ferdinand von Wright" title="en:Ferdinand von Wright"><span style="font-style:normal; font-weight:normal;" title="Ferdinand von Wright — версия статьи «Райт, Фердинанд фон» на английском языке">[en]</span></a></sup></span>, <span class="iw" data-title="Райт, Вильгельм фон"><a rel="mw:WikiLink" href="./Райт,_Вильгельм_фон" title="Райт, Вильгельм фон">Wright W. von</a><sup class="noprint"><a rel="mw:ExtLink" href="https://en.wikipedia.org/wiki/Wilhelm von Wright" title="en:Wilhelm von Wright"><span style="font-style:normal; font-weight:normal;" title="Wilhelm von Wright — версия статьи «Райт, Вильгельм фон» на английском языке">[en]</span></a></sup></span>, <a rel="mw:WikiLink" href="./Лённберг,_Эйнар" title="Лённберг, Эйнар">Lönnberg E.</a></i> Svenska fåglar, efter naturen och på sten ritade: tre volymer.&nbsp;— 2:a upplagan.&nbsp;— 1927—1929.<span typeof="mw:Entity">&nbsp;</span><span class="ref-info" title="на шведском языке " style="font-size:85%; cursor:help; color:#888;">(швед.)</span></span></li>
</ul>
</body></html>
"""

	# connect = wikiapi.wikiconnect()
	page = wikiapi.wikiapi_works(title)
	parsed_html = html.fromstring(page.get_html())

	list_pages_with_referrors[title] = collect_refs(parsed_html, title)
# for ref in ref_calls:
# parsed_html.xpath('//a/@href=' + ref_call)
# print('Ошибочные сноски: <a href={}>{}</a>)'.format(ref[0], ref[1]))


# запись исходной страниц из url в файл. urlopen берёт в byte-формате, request в str-формате
# filename = 'pagecontent.txt'
# f = open(filename, 'w', encoding='utf-8')
# # f = open(filename, 'bw')
# f.write(pagecontent)
# f.close()

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

for title in list_pages_with_referrors:
	replacetext_old = '== Описание герба =='
	refs_page = list_pages_with_referrors[title]
	refs_str = '|'.join([refs_page.get(ref) for ref in refs_page])
	replacetext_new = '{{' + post_tpl_name + '|' + refs_str + '}}'

	page = wikiapi.wikiapi_works(title)
	# title.edit(text, summary, mode='')
	page.replace_text_page(replacetext_old, replacetext_new, summary)
	del page
	print(page)





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
