# coding: utf-8
# author: https://github.com/vladiscripts
#
from pywikibot.data import mysql
from scripts.db_init import db_session, Page, ErrRef, WarningTpls, Timecheck, queryDB
from config import *


class UpdateDB:
    def __init__(self):
        # обновить список страниц, имеющих установленный шаблон
        self.update_listpages_have_WarningTpl()

        # обновить список страниц, имеющих шаблоны типа {{sfn}}
        self.update_transcludes_sfn_tempates()

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
        self.drop_orphan_by_timecheck()  # ненадо, если хранить только общее timelastcheck, а не таблицу по всем стр.
        self.drop_refs_of_changed_pages()

    def update_listpages_have_WarningTpl(self):
        """Обновить список страниц имеющих установленный шаблон."""
        tpls_str = self.list_to_str_params('tl_title',
                                           map(self.normalization_pagename, self.str2list(warning_tpl_name)))
        sql = f"""SELECT page_id, page_title
				FROM page
				JOIN templatelinks ON templatelinks.tl_from = page.page_id
				WHERE tl_namespace = 10 AND page_namespace = 0
				AND ({tpls_str})
				ORDER BY page.page_id ASC;"""
        pages = self.wdb_query(sql)
        db_session.query(WarningTpls).delete()
        for id, title in pages:
            db_session.add(WarningTpls(id, self.byte2utf(title)))
        db_session.commit()

    def update_transcludes_sfn_tempates(self):
        """Обновить список страниц, имеющих шаблоны типа {{sfn}}."""
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
        transcludes_wdb = self.wdb_query(sql)
        # long query ~45000 rows
        if len(transcludes_wdb) > 100:  # 10000 иногда возвращается обрезанный результат
            db_session.query(Page).delete()
        # for id, title, timeedit in transcludes_wdb:
        #     # id, title, timeedit = p[0], self.byte2utf(p[1]), int(p[2])
        #     db_session.add(Page(id, self.byte2utf(title), int(timeedit)))
        transcludes_wdb = [Page(id, self.byte2utf(title), int(timeedit)) for id, title, timeedit in transcludes_wdb]
        db_session.bulk_save_objects(transcludes_wdb)
        # long query
        db_session.commit()

    @staticmethod
    def drop_orphan_by_timecheck():
        """Если в pages нет записи о статье, то удалить ее строки из timecheck"""
        pages = db_session.query(Timecheck.page_id).outerjoin(Page).filter(Page.page_id.is_(None)).all()
        for p in pages:
            db_session.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete()
        db_session.commit()

    @staticmethod
    def drop_refs_of_changed_pages():
        # pages = db_session.query(ErrRef.page_id).outerjoin(Page).filter(Page.page_id.is_(None)).all()
        # for p in pages:
        #     db_session.query(ErrRef).filter(ErrRef.page_id == p.page_id).delete()
        subq = db_session.query(Page.page_id)
        db_session.query(ErrRef).filter(ErrRef.page_id.in_(subq)).delete(synchronize_session='fetch')
        # db_session.query(ErrRef.page_id).outerjoin(SfnPageChanged).filter(SfnPageChanged.page_id.is_(None)).delete()
        db_session.commit()

    # Helpers
    @staticmethod
    def drop_check_pages_with_warnings():
        """Удаление метки проверки у страниц имеющих warning-шаблон."""
        pages = queryDB((db_session.query(WarningTpls.page_id))).all()
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


"""
-- SELECT * FROM warning_tpls_transcludes
-- JOIN pages ON warning_tpls_transcludes.page_id = pages.id
-- JOIN timecheck ON timecheck.page_id = pages.id
-- LEFT OUTER JOIN refs USING (page_id)
-- WHERE refs.page_id IS NULL

-- SELECT * FROM pages
-- LEFT OUTER JOIN warning_tpls_transcludes ON pages.id = warning_tpls_transcludes.page_id
-- LEFT OUTER JOIN refs ON pages.id = refs.page_id
-- WHERE warning_tpls_transcludes.page_id IS NULL
-- AND refs.page_id  IS NOT NULL
-- GROUP BY pages.id

-- с новыми правками или без проверки
-- SELECT * FROM pages JOIN timecheck ON pages.page_id = timecheck.page_id
-- WHERE pages.timeedit > timecheck.timecheck OR timecheck.timecheck IS NULL

-- pages без warning
-- SELECT * FROM pages LEFT OUTER JOIN warnings ON pages.page_id = warnings.page_id WHERE warnings.page_id IS NULL

-- warnings без refs, к снятию warnings
-- SELECT * FROM warnings LEFT OUTER JOIN refs ON warnings.page_id = refs.page_id WHERE  refs.page_id IS NULL

-- titles for add warnings
-- SELECT pages.title FROM pages LEFT OUTER JOIN warnings ON warnings.page_id = pages.page_id
-- JOIN refs ON pages.page_id = refs.page_id
-- WHERE  warnings.page_id IS NULL AND refs.page_id  IS NOT NULL
-- -- ORDER BY pages.page_id, refs.citeref
-- GROUP BY pages.title

--- pages with errrefs
-- SELECT * FROM refs  GROUP BY refs.page_id
--- pages with errrefs and pagnames
SELECT * FROM pages LEFT OUTER JOIN  refs ON pages.page_id = refs.page_id
WHERE refs.page_id  IS NOT NULL
GROUP BY refs.page_id

-- LEFT OUTER JOIN warnings ON warnings.page_id = refs.page_id
-- JOIN pages ON warnings.page_id = refs.page_id
-- WHERE  warnings.page_id IS NULL
-- ORDER BY warnings.page_id, refs.page_id
-- -- JOIN timecheck USING (page_id)
-- -- ORDER BY warnings.page_id, refs.page_id
-- -- GROUP BY warnings.page_id


-- DELETE FROM timecheck WHERE page_id IN (
-- SELECT page_id, title
-- FROM warning_tpls_transcludes
-- LEFT OUTER JOIN refs USING (page_id)
-- JOIN pages ON pages.id = refs.page_id
-- WHERE refs.page_id IS NULL
-- GROUP BY refs.page_id
-- )


SELECT * FROM pages JOIN refs USING (page_id) JOIN timecheck USING (page_id) WHERE title LIKE 'Росянка'
-- SELECT refs.page_id FROM refs LEFT OUTER JOIN pages WHERE  pages.page_id IS NULL

-- удаление timecheck у страниц с warnings
-- DELETE FROM timecheck WHERE timecheck.page_id IN (
-- SELECT page_id FROM warnings
--  )

-- удаление timecheck у страниц с refs
-- DELETE FROM timecheck WHERE timecheck.page_id IN (SELECT page_id FROM refs GROUP BY page_id  )


-- SELECT * FROM pages JOIN refs USING (page_id) JOIN timecheck USING (page_id)
-- WHERE title LIKE 'Росянка'


-- move timecheck.timecheck → pages.timecheck
-- UPDATE pages SET timecheck = (SELECT timecheck.timecheck FROM timecheck WHERE pages.page_id = timecheck.page_id)
"""
