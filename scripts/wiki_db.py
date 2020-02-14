# coding: utf-8
# author: https://github.com/vladiscripts
#
from typing import Callable, Iterator
from pywikibot.data import mysql
from settings import *


def get_listpages_have_WarningTpl(limit=''):
    """Обновить список страниц имеющих установленный шаблон."""
    sql = f"""SELECT page_id, page_title
            FROM page
            JOIN templatelinks ON templatelinks.tl_from = page.page_id
            WHERE tl_namespace = 10 AND page_namespace = 0
            AND tl_title LIKE "{normalization_pagename(warning_tpl_name)}"
            ORDER BY page.page_id ASC;"""
    pages = tuple(wdb_query(sql))
    return pages


def get_listpages_have_sfnTpl():
    """Обновить список страниц, имеющих шаблоны типа {{sfn}}"""
    # tpls_str = _list_to_str_params('tl_title', names_sfn_templates)
    # sql = f"""SELECT
    #           page.page_id,
    #           page.page_title,
    #           MAX(revision.rev_timestamp) AS timelastedit
    #         FROM page
    #           INNER JOIN templatelinks ON page.page_id = templatelinks.tl_from
    #           INNER JOIN revision ON page.page_id = revision.rev_page
    #         WHERE templatelinks.tl_namespace = 10 AND page.page_namespace = 0
    #         AND ({tpls_str})
    #         GROUP BY page.page_title
    #         ORDER BY page.page_id;"""
    tpls = ','.join((f'"{normalization_pagename(s)}"' for s in names_sfn_templates))
    sql = f"""SELECT
              page_id,
              page_title,
              rev_timestamp
            FROM page
              INNER JOIN templatelinks ON page_id = tl_from
                AND tl_title IN ({tpls})
                AND page_namespace = 0 
                AND tl_namespace = 10 
              INNER JOIN revision ON page_latest = rev_id;"""
    pages = tuple(wdb_query(sql))
    return pages


def normalization_pagename(t: str) -> str:
    """Первая буква в верхний регистр, ' ' → '_' """
    t = t.strip()
    return t[0:1].upper() + t[1:].replace(' ', '_')


def list_to_str_params(string, strings: Iterator[str], couple_arg='LIKE', wordjoin=' OR ') -> str:
    """Return string like:  string LIKE string1 OR string LIKE string2"""
    return wordjoin.join([f'%s %s "%s"' % (string, couple_arg, normalization_pagename(s)) for s in strings])


def _list_to_str_params(field: str, strings: Iterator[str]) -> str:
    """Return string like:  string LIKE string1 OR string LIKE string2"""
    tpls = ','.join((f'"{normalization_pagename(s)}"' for s in strings))
    result = f' AND {field} IN ({tpls})'
    return result

def wdb_query(sql):
    result = mysql.mysql_query(sql)
    return result

# def wdb_query_pymysql(sql):
#     import pymysql
#     import passwords
#     connection = pymysql.connect(
#         # Для доступа к wiki-БД с ПК необходим ssh-тунель с перебросом порта с localhost
#         # ssh -L 4711:ruwiki.labsdb:3306 <username>@login.tools.wmflabs.org -i "<path/to/key>"
#         # см. https://wikitech.wikimedia.org/wiki/Help:Tool_Labs/Database#Connecting_to_the_database_replicas_from_your_own_computer
#         # host='127.0.0.1', port=4711,
#         # или для доступа из скриптов на tools.wmflabs.org напрямую:
#         # host='ruwiki.labsdb', port=3306,
#         host='127.0.0.1' if run_local_not_from_wmflabs else 'ruwiki.labsdb',
#         port=4711 if run_local_not_from_wmflabs else 3306,
#         db='ruwiki_p',
#         user=passwords.wdb_user,
#         password=passwords.wdb_pw,
#         use_unicode=True, charset="utf8")
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(sql)
#         result = cursor.fetchall()
#     finally:
#         connection.close()
#     return result

# def query_transcludes_any_tpl(self, tpl_name):
#     """Полоучение списка трансклюзий какого-либо шаблона.
#     Для тестов в основном, и сброса отметки проверки и перепроверки неучтённых шаблонов."""
#     tpls_str = self.list_to_str_params('tl_title',
#                                        map(self.normalization_pagename, self.str2list(tpl_name)))
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
