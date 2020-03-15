# coding: utf-8
# author: https://github.com/vladiscripts
#
import itertools
from settings import *
from scripts.db_models import PageWithSfn, ErrRef, Wikilists, db_session as s
from scripts.make_listspages import file_savetext


def make_wikilists_by_page_ids():
    pq = (s.query(PageWithSfn.page_id, PageWithSfn.title, ErrRef.link_to_sfn, ErrRef.text)
          .join(ErrRef, PageWithSfn.page_id == ErrRef.page_id)
          # .join(Wikilists, Wikilists.letter == PageWithSfn.wikilist)
          .filter(ErrRef.page_id.isnot(None)
                  # , Wikilists.title == w.title
                  )
          .order_by(PageWithSfn.page_id, ErrRef.citeref))
    refs_pages4check = pq.all()

    wikilists = []
    for k, group_list in itertools.groupby(refs_pages4check, key=lambda g: g.page_id // 1000000):
        print()
        # wikilists.append(list(g))
        list_refs_entries = []
        for i, page_refs in itertools.groupby(list(group_list), key=lambda g: g.page_id):
            page_refs = list(page_refs)
            p = page_refs[0]
            refs_wikilinks = [r"[[#%s|%s]]" % (ref.link_to_sfn, ref.text) for ref in page_refs]
            # for pid in {n.page_id for n in g}:

            # for pid in {n.page_id for n in g}:
            #     page_refs = [r for r in refs_pages4check if r.title == page_title]

            refs_entry = '* {pid} [[{t}]]:<br><section begin="{pid}" />{all_wikilinks}<section end="{pid}" />' \
                .format(t=p.title.replace('_', ' '), pid=p.page_id, all_wikilinks=', '.join(refs_wikilinks))
            list_refs_entries.append(refs_entry)
            pass

        # Fill wikilists page
        if list_refs_entries:
            pagename = f'Шаблон:{root_wikilists}/{k}m'
            fw = formatted_wikilist(pagename, '\n'.join(list_refs_entries))
            wikilists.append(fw)
    wikilists = ''.join(wikilists)
    return wikilists


def make_wikilists_by_alphabet():
    wikilists = []
    wikilists_titles = s.query(Wikilists.title).group_by(Wikilists.title).all()
    for w in wikilists_titles:
        list_refs_entries = []
        pq = s.query(PageWithSfn.page_id, PageWithSfn.title, ErrRef.link_to_sfn, ErrRef.text) \
            .join(ErrRef, PageWithSfn.page_id == ErrRef.page_id) \
            .join(Wikilists, Wikilists.letter == PageWithSfn.wikilist) \
            .filter(ErrRef.page_id.isnot(None), Wikilists.title == w.title) \
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
            pagename = f'Шаблон:{root_wikilists}/{w.title}'
            fw = formatted_wikilist(pagename, '\n'.join(list_refs_entries))
            wikilists.append(fw)
    wikilists = ''.join(wikilists)
    return wikilists


def formatted_wikilist(pagename, wiki_refs_entries):
    return f"{marker_page_start}\n'''{pagename}'''\n{header}\n{wiki_refs_entries}\n{footer}\n{marker_page_end}\n\n"


def make_and_save_wikilist():
    # wikilists = make_wikilists_by_alphabet()
    # file_savetext('alphabet_' + filename_wikilists, wikilists)
    wikilists = make_wikilists_by_page_ids()
    file_savetext(filename_wikilists, wikilists)
