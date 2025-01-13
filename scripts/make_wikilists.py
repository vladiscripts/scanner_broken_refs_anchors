# coding: utf-8
# author: https://github.com/vladiscripts
#
import itertools
import re
from settings import *
from scripts.db_models import PageWithSfn, ErrRef, db_session as s
from scripts.make_listspages import file_savetext


def make_wikilists_by_page_ids():
    pq = (s.query(PageWithSfn.page_id, PageWithSfn.title, ErrRef.link_to_sfn, ErrRef.text)
          .join(ErrRef, PageWithSfn.page_id == ErrRef.page_id)
          .filter(ErrRef.page_id.isnot(None))
          .order_by(PageWithSfn.page_id, ErrRef.citeref))
    refs_pages4check = pq.all()

    wikilists = []
    for k, group_list in itertools.groupby(refs_pages4check, key=lambda g: g.page_id // 1000000):
        list_refs_entries = []
        for i, page_refs in itertools.groupby(list(group_list), key=lambda g: g.page_id):
            page_refs = list(page_refs)
            p = page_refs[0]
            refs_wikilinks = []
            for ref in page_refs:
                ankor = ref.link_to_sfn
                if not re.search(r'^[\w_-]+$', ref.link_to_sfn): ankor = '{{urlencode:%s}}' % ref.link_to_sfn
                refs_wikilinks.append(f"[[#{ankor}|{ref.text}]]")
            refs_entry = '* {pid} [[{title}]]:<br><section begin="{pid}" />{all_wikilinks}<section end="{pid}" />' \
                .format(title=p.title.replace('_', ' '), pid=p.page_id, all_wikilinks=', '.join(refs_wikilinks))
            list_refs_entries.append(refs_entry)

        # Fill wikilists page
        if list_refs_entries:
            pagename = f'Шаблон:{root_wikilists}/{k}m'
            fw = formatted_wikilist(pagename, '\n'.join(list_refs_entries))
            wikilists.append(fw)
    wikilists = ''.join(wikilists)
    return wikilists


def formatted_wikilist(pagename, wiki_refs_entries):
    return f"{marker_page_start}\n'''{pagename}'''\n{header}\n{wiki_refs_entries}\n{footer}\n{marker_page_end}\n\n"


def make_and_save_wikilist():
    wikilists = make_wikilists_by_page_ids()
    file_savetext(filename_wikilists, wikilists)
