# coding: utf-8
# author: https://github.com/vladiscripts
#
from config import *
from scripts.db import session, Page, Ref, Wikilists, queryDB


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
			session.merge(Wikilists(r[0], r[1]))
		session.commit()

	def make_wikilists(self):
		wikilists_sql = queryDB(session.query(Wikilists.title).group_by(Wikilists.title))
		for wikilist_sql in wikilists_sql:
			wikilist_title = wikilist_sql[0]
			list_refs_entries = ''
			pq = session.query(Page.page_id, Page.title).select_from(Page) \
				.join(Ref, Page.page_id == Ref.page_id) \
				.join(Wikilists, Wikilists.letter == Page.wikilist) \
				.filter(Ref.page_id.isnot(None), Wikilists.title == wikilist_title) \
				.group_by(Ref.page_id) \
				.order_by(Page.title)
			pages4check = queryDB(pq)
			for page in pages4check:
				list_refs_entries += self.formated_refs_entries_of_page(page)

			# Fill wikilists page
			if list_refs_entries != '':
				pagename = u'Шаблон:' + root_wikilists + wikilist_title
				self.wikilists += self.formated_wikilist(pagename, list_refs_entries)

	def formated_wikilist(self, pagename, wiki_refs_entries):
		return "{start}\n'''{pagename}'''\n{header}\n{refs_entries}\n{footer}\n{end}\n\n".format(
			start=marker_page_start, end=marker_page_end,
			pagename=pagename, header=header, footer=footer,
			refs_entries=wiki_refs_entries)

	def formated_refs_entries_of_page(self, page):
		refs_entry, page_id, title = '', page[0], page[1]
		refs = queryDB(session.query(Ref.link_to_sfn, Ref.text).filter(Ref.page_id == page_id).order_by(Ref.citeref))
		if len(refs) > 0:
			page_wikilinks = []
			for ref in refs:
				page_wikilinks.append(
					r"[[#{link}|{text}]]".format(link=ref.refs_link_to_sfn, text=ref.refs_text))
			refs_entry = '* [[{t}]]:<br><section begin="{t}" />{all_wikilinks}<section end="{t}" />\n' \
				.format(t=title.replace('_', ' '), all_wikilinks=', '.join(page_wikilinks))
		return refs_entry

	def save_wikilist(self):
		file_savetext(filename_wikilists + '.txt', self.wikilists)

	# def formating_sql2wikilink(self, part):
	# 	"""Сортировка sql refs по алфавиту и форматирование в викиссылки."""
	# 	part_list_wikilinks = []
	# 	q = db.session.query(db.Page.page_id, db.Page.title)
	# 	for p in db.session.execute(q).fetchall():
	# 		q = db.session.query(db.Ref.link_to_sfn, db.Ref.text) \
	# 			.filter(db.Ref.page_id == p[0]) \
	# 			.order_by(db.Ref.citeref)
	# 		page_wikilinks = [r"[[#{link}|{text}]]".format(link=ref.refs_link_to_sfn, text=ref.refs_text) for ref in
	# 						  db.session.execute(q).fetchall()]
	# 		part_list_wikilinks.append(
	# 				r'* [[{t}]]:<br><section begin="{t}" />{all_wikilinks}<section end="{t}" />'.format(
	# 						t=p.pages_title.replace('_', ' '), all_wikilinks=', '.join(page_wikilinks)))
	# 	return part_list_wikilinks
