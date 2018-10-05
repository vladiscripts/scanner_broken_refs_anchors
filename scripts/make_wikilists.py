# coding: utf-8
# author: https://github.com/vladiscripts
#
from settings import *
from scripts.db_models import db_session, PageWithSfn, ErrRef, Wikilists
from scripts.make_listspages import file_savetext


def make_and_save_wikilist():
    def make_wikilist_titles():
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

    def make_wikilists():
        wikilists = ''
        wikilists_sql = db_session.query(Wikilists.title).group_by(Wikilists.title).all()
        for wikilist_sql in wikilists_sql:
            wikilist_title = wikilist_sql[0]
            list_refs_entries = ''
            pq = db_session.query(PageWithSfn.page_id, PageWithSfn.title, ErrRef.link_to_sfn, ErrRef.text) \
                .join(ErrRef, PageWithSfn.page_id == ErrRef.page_id) \
                .join(Wikilists, Wikilists.letter == PageWithSfn.wikilist) \
                .filter(ErrRef.page_id.isnot(None), Wikilists.title == wikilist_title) \
                .order_by(PageWithSfn.title, ErrRef.citeref)
            refs_pages4check = pq.all()

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
                wikilists += formatted_wikilist(pagename, list_refs_entries)
        return wikilists

    def formatted_wikilist(pagename, wiki_refs_entries):
        return f"{marker_page_start}\n'''{pagename}'''\n{header}\n{wiki_refs_entries}\n{footer}\n{marker_page_end}\n\n"

    make_wikilist_titles()
    wikilists = make_wikilists()
    file_savetext(filename_wikilists, wikilists)
