# author: https://github.com/vladiscripts
from typing import NamedTuple, Generator
from pywikibot.data import mysql
from urllib.parse import quote_from_bytes, unquote
from datetime import datetime

from settings import *


class PageWithSfnInWiki(NamedTuple):
    """Страница с {{sfn}} и временем последнего редактирования."""
    page_id: int
    title: str
    timelastedit: datetime


class PageWithWarningInWiki(NamedTuple):
    """Страница с установленным шаблоном-предупреждением."""
    page_id: int
    title: str


def get_listpages_have_WarningTpl() -> tuple[PageWithWarningInWiki, ...]:
    """Получить список страниц, имеющих установленный шаблон-предупреждение."""
    sql = f"""SELECT page_id, page_title
                FROM page
                    INNER JOIN templatelinks ON tl_from = page_id
                    INNER JOIN linktarget on tl_target_id = lt_id 
                WHERE lt_namespace = 10
                  AND lt_title = "{normalization_pagename(warning_tpl_name)}"
                  AND page_namespace = 0;"""
    pages = tuple(PageWithWarningInWiki(r[0], byte2utf(r[1])) for r in wdb_query(sql))
    return pages


def get_listpages_have_sfnTpl() -> tuple[PageWithSfnInWiki, ...]:
    """Получить список страниц, имеющих шаблоны типа {{sfn}}."""
    tpls = ','.join((f'"{normalization_pagename(s)}"' for s in names_sfn_templates))
    sql = f"""SELECT page_id, page_title, rev_timestamp
                FROM page
                  INNER JOIN templatelinks ON page_id = tl_from
                  INNER JOIN linktarget on tl_target_id = lt_id
                  INNER JOIN revision ON page_latest = rev_id
                  WHERE lt_namespace = 10
                    AND page_namespace = 0
                    AND lt_title IN ({tpls});"""
    pages = tuple(PageWithSfnInWiki(r[0], byte2utf(r[1]), datetime.strptime(r[2].decode(), '%Y%m%d%H%M%S')) for r in wdb_query(sql))
    return pages


def normalization_pagename(t: str) -> str:
    """Первая буква в верхний регистр, ' ' → '_' """
    t = t.strip()
    return t[0:1].upper() + t[1:].replace(' ', '_')


# def list_to_str_params(string, strings: Iterator[str], couple_arg='LIKE', wordjoin=' OR ') -> str:
#     """Return string like:  string LIKE string1 OR string LIKE string2"""
#     return wordjoin.join([f'%s %s "%s"' % (string, couple_arg, normalization_pagename(s)) for s in strings])


# def _list_to_str_params(field: str, strings: Iterator[str]) -> str:
#     """Return string like:  string LIKE string1 OR string LIKE string2"""
#     tpls = ','.join((f'"{normalization_pagename(s)}"' for s in strings))
#     result = f' AND {field} IN ({tpls})'
#     return result


def wdb_query(sql, limit='') -> Generator:
    result = mysql.mysql_query(sql.format(limit), dbname='ruwiki')
    return result


def byte2utf(string):
    return unquote(quote_from_bytes(string), encoding='utf8')

# def query_transcludes_any_tpl(self, tpl_name):
#     """Получение списка трансклюзий какого-либо шаблона.
#     Для тестов в основном, и сброса отметки проверки и перепроверки неучтённых шаблонов."""
#     tpls_str = self.list_to_str_params('tl_title', map(self.normalization_pagename, self.str2list(tpl_name)))
#     sql = f"""SELECT page_id, page_title
# 		FROM page
# 		JOIN templatelinks ON templatelinks.tl_from = page.page_id
# 		WHERE tl_namespace = 10 AND page_namespace = 0
# 		AND ({tpls_str})
# 		ORDER BY page.page_id ASC;"""
#     pages = self.wdb_query(sql)
#     # pages_titles = sorted([self.byte2utf(p[1]) for p in pages])
#     Session.query(Timecheck).filter(Timecheck.page_id in (p[0] for p in pages)).delete()
#     Session.commit()
