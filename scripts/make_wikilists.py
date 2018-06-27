# coding: utf-8
# author: https://github.com/vladiscripts
#
from config import *
from scripts.db_init import db_session, SfnPageChanged, ErrRef, Wikilists, queryDB
from scripts.make_listspages import file_savetext


class MakeWikiLists:
    def __init__(self):
        self.wikilists = ''
        self.make_wikilist_titles()
        self.make_wikilists()
        self.save_wikilist()

    def make_wikilist_titles(self):
        wikilists = (
            ('А', 'А'), ('Б', 'Б'), ('В', 'ВГ'), ('Г', 'ВГ'), ('Д', 'Д'),
            ('Е', 'ЕЁЖЗИЙ'), ('Ё', 'ЕЁЖЗИЙ'), ('Ж', 'ЕЁЖЗИЙ'), ('З', 'ЕЁЖЗИЙ'), ('И', 'ЕЁЖЗИЙ'), ('Й', 'ЕЁЖЗИЙ'),
            ('К', 'К'), ('Л', 'ЛМ'), ('М', 'ЛМ'), ('Н', 'НО'),
            ('О', 'НО'), ('П', 'П'), ('Р', 'Р'), ('С', 'С'), ('Т', 'Т'),
            ('У', 'УФХ'), ('Ф', 'УФХ'), ('Х', 'УФХ'),
            ('Ц', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ч', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ш', 'ЦЧШЩЪЫЬЭЮЯ'), ('Щ', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ъ', 'ЦЧШЩЪЫЬЭЮЯ'),
            ('Ы', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ь', 'ЦЧШЩЪЫЬЭЮЯ'), ('Э', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ю', 'ЦЧШЩЪЫЬЭЮЯ'), ('Я', 'ЦЧШЩЪЫЬЭЮЯ'),
            ('*', 'Не русские буквы'),
        )
        for letter, pagename in wikilists:
            db_session.merge(Wikilists(letter, pagename))
        db_session.commit()

    def make_wikilists(self):
        wikilists_sql = queryDB(db_session.query(Wikilists.title).group_by(Wikilists.title))
        for wikilist_sql in wikilists_sql:
            wikilist_title = wikilist_sql[0]
            list_refs_entries = ''
            pq = db_session.query(SfnPageChanged.page_id, SfnPageChanged.title, ErrRef.link_to_sfn, ErrRef.text) \
                .join(ErrRef, SfnPageChanged.page_id == ErrRef.page_id) \
                .join(Wikilists, Wikilists.letter == SfnPageChanged.wikilist) \
                .filter(ErrRef.page_id.isnot(None), Wikilists.title == wikilist_title) \
                .order_by(SfnPageChanged.title, ErrRef.citeref)
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
        return f"{marker_page_start}\n'''{pagename}'''\n{header}\n{wiki_refs_entries}\n{footer}\n{marker_page_end}\n\n"

    def save_wikilist(self):
        file_savetext(f'{filename_wikilists}.txt', self.wikilists)
