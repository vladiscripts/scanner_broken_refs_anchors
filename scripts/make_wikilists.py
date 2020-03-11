# coding: utf-8
# author: https://github.com/vladiscripts
#
from settings import *
from scripts.db_models import PageWithSfn, ErrRef, Wikilists, db_session as s
from scripts.make_listspages import file_savetext


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
        s.merge(Wikilists(letter, pagename))
    s.commit()


def make_wikilists():
    wikilists = []
    wikilists_sql = s.query(Wikilists.title).group_by(Wikilists.title).all()
    for wikilist_sql in wikilists_sql:
        wikilist_title = wikilist_sql[0]
        list_refs_entries = []
        pq = s.query(PageWithSfn.page_id, PageWithSfn.title, ErrRef.link_to_sfn, ErrRef.text) \
            .join(ErrRef, PageWithSfn.page_id == ErrRef.page_id) \
            .join(Wikilists, Wikilists.letter == PageWithSfn.wikilist) \
            .filter(ErrRef.page_id.isnot(None), Wikilists.title == wikilist_title) \
            .order_by(PageWithSfn.title, ErrRef.citeref)
        refs_pages4check = pq.all()

        for page_id, page_title in sorted({(p.page_id, p.title) for p in refs_pages4check}, key=lambda p: p[1]):
            page_refs = [r for r in refs_pages4check if r.title == page_title]
            refs_wikilinks = [r"[[#%s|%s]]" % (ref.link_to_sfn, ref.text) for ref in page_refs]
            refs_entry = '* {pid} [[{t}]]:<br><section begin="{pid}" />{all_wikilinks}<section end="{pid}" />' \
                .format(t=page_title.replace('_', ' '), pid=page_id, all_wikilinks=', '.join(refs_wikilinks))
            list_refs_entries.append(refs_entry)
            pass

        # Fill wikilists page
        if list_refs_entries:
            pagename = f'Шаблон:{root_wikilists}/{wikilist_title}'
            fw = formatted_wikilist(pagename, '\n'.join(list_refs_entries))
            wikilists.append(fw)
    wikilists = ''.join(wikilists)
    return wikilists


def formatted_wikilist(pagename, wiki_refs_entries):
    return f"{marker_page_start}\n'''{pagename}'''\n{header}\n{wiki_refs_entries}\n{footer}\n{marker_page_end}\n\n"


def make_and_save_wikilist():
    make_wikilist_titles()
    wikilists = make_wikilists()
    file_savetext(filename_wikilists, wikilists)
