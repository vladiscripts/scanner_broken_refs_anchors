# coding: utf-8
# author: https://github.com/vladiscripts
#
from pywikibot.data import mysql
from scripts.db_models import db_session, PageWithSfn, ErrRef, PageWithWarning, Timecheck
from settings import *


class UpdateDB:
    def __init__(self):
        # обновить список страниц, имеющих установленный шаблон
        self.reload_listpages_have_WarningTpl()

        # обновить список страниц, имеющих шаблоны типа {{sfn}}
        self.reload_listpages_have_sfnTpl()

        # очистка метки проверки неучтенных шаблонов
        # self.query_transcludes_any_tpl(('Citation', 'Cite'))
        # self.query_transcludes_any_tpl('Cite')

        # Опциональные чистки, проще (?) удалить и пересоздать файл базы данных
        if clear_check_pages_with_warnings:
            # удаление метки проверки у страниц имеющих warning-шаблон
            self.drop_check_pages_with_warnings()
        if clear_all_check_pages:
            # сброс всех меток проверки
            self.drop_all_check_pages()
            db_session.query(ErrRef).delete()

        # чистка PageTimecheck и Ref от записей которых нет в pages
        # не нужно с ForeignKey ondelete="CASCADE"
        # self.drop_orphan_by_timecheck()
        # self.drop_refs_of_changed_pages()

    def reload_listpages_have_WarningTpl(self):
        """Обновить список страниц имеющих установленный шаблон."""
        tpls_str = self.list_to_str_params('tl_title',
                                           map(self.normalization_pagename, self.str2list(warning_tpl_name)))
        sql = f"""SELECT page_id, page_title
				FROM page
				JOIN templatelinks ON templatelinks.tl_from = page.page_id
				WHERE tl_namespace = 10 AND page_namespace = 0
				AND ({tpls_str})
				ORDER BY page.page_id ASC;"""
        w_pages = self.wdb_query(sql)
        db_session.query(PageWithWarning).delete()
        for pid, title in w_pages:
            db_session.add(PageWithWarning(pid, self.byte2utf(title)))
        db_session.commit()

    def reload_listpages_have_sfnTpl(self):
        """Загрузка списка страниц имеющих шаблоны типа {{sfn}}, и обновление ими базы данных"""

        w_pages_with_sfns = self.wdb_get_listpages_have_sfnTpl()  # long query ~45000 rows

        # if len(w_pages_with_sfns) > 10000:  # 10000 иногда возвращается обрезанный результат
        #     db_session.query(PageWithSfn).delete()

        # избранное удаление страниц из ДБ, которых нет в вики
        # иначе если удалять все, то параметр ForeignKey ondelete="CASCADE" удалит и все проверки
        # Если же не использовать ondelete="CASCADE", а удалять через WHERE отдельными DELETE, как раньше - это долго

        # db_pages = db_session.query(PageWithSfn.page_id, PageWithSfn.title, Timecheck.timecheck) \
        #     .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id).all()
        db_pages = db_session.query(PageWithSfn).all()
        db_pages_ids = {p.page_id for p in db_pages}
        w_pages_ids = {page_id for page_id, title, timelastedit in w_pages_with_sfns}
        delta = db_pages_ids - w_pages_ids
        # new_delta = w_pages_ids - db_pages_ids
        if delta:
            db_session.query(PageWithSfn).filter(PageWithSfn.page_id.in_(delta)).delete(synchronize_session='fetch')
            db_session.commit()

        # w_pages_with_sfns = [PageWithSfn(id, self.byte2utf(title), int(timelastedit))
        #                      for id, title, timelastedit in w_pages_with_sfns]

        for page_id, title, timelastedit in w_pages_with_sfns:
            db_session.merge(PageWithSfn(page_id, self.byte2utf(title), int(timelastedit)))

        # слишком долная операция
        # for page_id, title, timelastedit in w_pages_with_sfns:
        #     for db in db_pages:
        #         if page_id == db.page_id:
        #             if int(timelastedit) >= int(db.timecheck) or title.decode("utf-8") != db.title:
        #                 db_session.merge(PageWithSfn(page_id, self.byte2utf(title), int(timelastedit)))
        #             break

        # db_session.bulk_save_objects(w_pages_with_sfns)
        # long query
        db_session.commit()

    def wdb_get_listpages_have_sfnTpl(self):
        """Обновить список страниц, имеющих шаблоны типа {{sfn}}"""
        tpls_str = self.list_to_str_params('templatelinks.tl_title',
                                           map(self.normalization_pagename, self.str2list(names_sfn_templates)))
        sql = f"""SELECT
                  page.page_id,
                  page.page_title,
                  MAX(revision.rev_timestamp) AS timelastedit
                FROM page
                  INNER JOIN templatelinks ON page.page_id = templatelinks.tl_from
                  INNER JOIN revision ON page.page_id = revision.rev_page
                WHERE templatelinks.tl_namespace = 10 AND page.page_namespace = 0
                AND ({tpls_str})
                GROUP BY page.page_title
                ORDER BY page.page_id ASC;"""
        pages = self.wdb_query(sql)
        # if len(wdb_pages_with_sfns) > 10000:  # 10000 иногда возвращается обрезанный результат
        #     db_session.query(PageWithSfn).delete()
        # long query ~45000 rows
        return pages

    # @staticmethod
    # def drop_orphan_by_timecheck():
    #     """Если в pages нет записи о статье, то удалить ее строки из timecheck"""
    #     pages = db_session.query(Timecheck.page_id).outerjoin(PageWithSfn).filter(
    #         PageWithSfn.page_id.is_(None)).all()
    #     for p in pages:
    #         db_session.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete()
    #     db_session.commit()

    # @staticmethod
    # def drop_refs_of_changed_pages():
    #     # pages = db_session.query(ErrRef.page_id).outerjoin(SfnPageChanged).filter(SfnPageChanged.page_id.is_(None)).all()
    #     # for p in pages:
    #     #     db_session.query(ErrRef).filter(ErrRef.page_id == p.page_id).delete()
    #     subq = db_session.query(PageWithSfn.page_id)
    #     db_session.query(ErrRef).filter(ErrRef.page_id.in_(subq)).delete(synchronize_session='fetch')
    #     # db_session.query(ErrRef.page_id).outerjoin(SfnPageChanged).filter(SfnPageChanged.page_id.is_(None)).delete()
    #     db_session.commit()

    # Helpers
    @staticmethod
    def drop_check_pages_with_warnings():
        """Удаление метки проверки у страниц имеющих warning-шаблон."""
        pages = db_session.query(PageWithWarning.page_id).all()
        for p in pages:
            db_session.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete()
        db_session.commit()

    @staticmethod
    def drop_all_check_pages():
        """Очистка таблицы Timecheck: удаление метки проверки у всех страниц"""
        db_session.query(Timecheck).delete()
        db_session.commit()

    @staticmethod
    def drop_all_refs():
        """Очистка таблицы Refs"""
        db_session.query(ErrRef).delete()
        db_session.commit()

    @staticmethod
    def str2list(string):
        """Строку в список"""
        return [string] if isinstance(string, str) else string

    @staticmethod
    def byte2utf(string):
        import urllib.parse
        string = urllib.parse.quote_from_bytes(string)
        string = urllib.parse.unquote(string, encoding='utf8')
        return string

    @staticmethod
    def normalization_pagename(t):
        """Первая буква в верхний регистр, ' ' → '_' """
        t = t.strip()
        return t[0:1].upper() + t[1:].replace(' ', '_')

    @staticmethod
    def list_to_str_params(string, strings2list, couple_arg='LIKE', wordjoin=' OR '):
        """Return string like:  string LIKE string1 OR string LIKE string2"""
        return wordjoin.join(['%s %s "%s"' % (string, couple_arg, s) for s in strings2list])

    @staticmethod
    def wdb_query(sql):
        result = list(mysql.mysql_query(sql))
        return result

    # @staticmethod
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
    #     db_session.query(Timecheck).filter(Timecheck.page_id in (p[0] for p in pages)).delete()
    #     db_session.commit()
