# author: https://github.com/vladiscripts
from sqlalchemy import select

from scripts import file_savelines
from settings import *
from scripts.db_models import PagesWithSfn, ErrRef, PageWithWarning, Session


def save_listpages_for_remove_warning_tpls():
    """Создать список страниц, где можно удалить шаблон-предупреждение (нет ошибочных сносок)."""
    with Session() as s:
        stmt = (
            select(PageWithWarning.title)
            .outerjoin(ErrRef, PageWithWarning.page_id == ErrRef.page_id)
            .where(ErrRef.page_id.is_(None))
            .order_by(PageWithWarning.title)
        )
        titles = [row[0] for row in s.execute(stmt).fetchall()]
        file_savelines(filename_list_to_remove_warning_tpl, sorted(titles))


def save_listpages_for_add_warning_tpls():
    """Список куда предупреждение ещё не поставлено."""
    with Session() as s:
        stmt = (
            select(PagesWithSfn.title)
            .join(ErrRef, PagesWithSfn.page_id == ErrRef.page_id)
            .outerjoin(PageWithWarning, PagesWithSfn.page_id == PageWithWarning.page_id)
            .where(PageWithWarning.page_id.is_(None))
            .group_by(PagesWithSfn.title)
            .order_by(PagesWithSfn.title)
        )
        titles = [row.title for row in s.execute(stmt).fetchall()]
        file_savelines(filename_listpages_errref_where_no_yet_warning_tpl, titles)
