# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from settings import *
from scripts.db_init import db_session, PageWithSfn, ErrRef, PageWithWarning


def save_listpages_to_remove_warning_tpl():
    query = db_session.query(PageWithWarning.title) \
        .outerjoin(ErrRef, PageWithWarning.page_id == ErrRef.page_id) \
        .filter(ErrRef.page_id.is_(None))

    list_to_remove_warning_tpl = (str(title[0]) for title in query.all())
    file_savelines(filename_list_to_remove_warning_tpl, sorted(list_to_remove_warning_tpl))


def save_listpages_to_add_warning_tpl():
    """Список куда предупреждение ещё не поставлено."""
    errpages_without_warning_tpl = db_session.query(PageWithSfn.title) \
        .outerjoin(PageWithWarning, PageWithSfn.page_id == PageWithWarning.page_id) \
        .join(ErrRef, PageWithSfn.page_id == ErrRef.page_id) \
        .filter(PageWithWarning.page_id.is_(None), ErrRef.page_id.isnot(None)) \
        .group_by(PageWithSfn.title).all()

    errpages_without_warning_tpl = (p.title for p in errpages_without_warning_tpl)
    file_savelines(filename_listpages_errref_where_no_yet_warning_tpl, errpages_without_warning_tpl)


def file_savelines(filename, strlist, append=False):
    mode = 'a' if append else 'w'
    text = '\n'.join(strlist)
    with open(filename, mode, encoding='utf-8') as f:
        f.write(text)


def file_savetext(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)
