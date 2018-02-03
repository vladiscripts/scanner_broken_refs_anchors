# coding: utf-8
# author: https://github.com/vladiscripts
#
from config import *
from scripts.db import db_session, Page, Ref, Wikilists, queryDB
from scripts.make_listspages import file_savetext


class MakeWikiLists:
	def __init__(self):
		self.wikilists = ''
		self.make_wikilist_titles()
		self.make_wikilists()
		self.save_wikilist()

	def make_wikilist_titles(self):
		wikilists = [
			['А', 'А'],
			['Б', 'Б'],
			['В', 'ВГ'], ['Г', 'ВГ'],
			['Д', 'Д'],
			['Е', 'ЕЁЖЗИЙ'], ['Ё', 'ЕЁЖЗИЙ'], ['Ж', 'ЕЁЖЗИЙ'], ['З', 'ЕЁЖЗИЙ'], ['И', 'ЕЁЖЗИЙ'], ['Й', 'ЕЁЖЗИЙ'],
			['К', 'К'],
			['Л', 'ЛМ'], ['М', 'ЛМ'],
			['Н', 'НО'], ['О', 'НО'],
			['П', 'П'],
			['Р', 'Р'],
			['С', 'С'],
			['Т', 'Т'],
			['У', 'УФХ'], ['Ф', 'УФХ'], ['Х', 'УФХ'],
			['Ц', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ч', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ш', 'ЦЧШЩЪЫЬЭЮЯ'], ['Щ', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ъ', 'ЦЧШЩЪЫЬЭЮЯ'],
			['Ы', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ь', 'ЦЧШЩЪЫЬЭЮЯ'], ['Э', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ю', 'ЦЧШЩЪЫЬЭЮЯ'], ['Я', 'ЦЧШЩЪЫЬЭЮЯ'],
			['*', 'Не русские буквы'],
		]
		for r in wikilists:
			db_session.merge(Wikilists(r[0], r[1]))
		db_session.commit()

	def make_wikilists(self):
		wikilists_sql = queryDB(db_session.query(Wikilists.title).group_by(Wikilists.title))
		for wikilist_sql in wikilists_sql:
			wikilist_title = wikilist_sql[0]
			list_refs_entries = ''
			pq = db_session.query(Page.page_id, Page.title, Ref.link_to_sfn, Ref.text).select_from(Page) \
				.join(Ref, Page.page_id == Ref.page_id) \
				.join(Wikilists, Wikilists.letter == Page.wikilist) \
				.filter(Ref.page_id.isnot(None), Wikilists.title == wikilist_title) \
				.order_by(Page.title, Ref.citeref)
			refs_pages4check = queryDB(pq)

			for page_title in sorted({p[1] for p in refs_pages4check}):
				page_refs = [r for r in refs_pages4check if r[1] == page_title]
				refs_wikilinks = [r"[[#%s|%s]]" % (ref[2], ref[3]) for ref in page_refs]
				refs_entry = '* [[{t}]]:<br><section begin="{t}" />{all_wikilinks}<section end="{t}" />\n' \
					.format(t=page_title.replace('_', ' '), all_wikilinks=', '.join(refs_wikilinks))
				list_refs_entries += refs_entry
				pass

			# Fill wikilists page
			if list_refs_entries != '':
				pagename = u'Шаблон:' + root_wikilists + wikilist_title
				self.wikilists += self.formated_wikilist(pagename, list_refs_entries)

	def formated_wikilist(self, pagename, wiki_refs_entries):
		return "{start}\n'''{pagename}'''\n{header}\n{refs_entries}\n{footer}\n{end}\n\n".format(
			start=marker_page_start, end=marker_page_end,
			pagename=pagename, header=header, footer=footer,
			refs_entries=wiki_refs_entries)

	def save_wikilist(self):
		file_savetext(filename_wikilists + '.txt', self.wikilists)
