# coding: utf-8
# author: https://github.com/vladiscripts
#
from pywikibot.data import mysql
from scripts.db_models import db_session, PageWithSfn, ErrRef, PageWithWarning, Timecheck
from settings import *
from scripts import wdb


class UpdateDB:
    def listpages(self):
        # обновить список страниц, имеющих установленный шаблон
        self.reload_listpages_have_WarningTpl()

        # обновить список страниц, имеющих шаблоны типа {{sfn}}
        self.reload_listpages_have_sfnTpl()

        # очистка метки проверки неучтенных шаблонов
        # self.query_transcludes_any_tpl(('Citation', 'Cite'))
        # self.query_transcludes_any_tpl('Cite')

        # чистка PageTimecheck и Ref от записей которых нет в pages
        # не нужно с ForeignKey ondelete="CASCADE"
        # таки нужно
        self.drop_orphan_by_timecheck()
        self.drop_refs_of_changed_pages()

    def reload_listpages_have_WarningTpl(self):
        """Обновить список страниц имеющих установленный шаблон."""
        w_pages = wdb.get_listpages_have_WarningTpl()
        Session()
        db_session.query(PageWithWarning).delete()
        for pid, title in w_pages:
            db_session.add(PageWithWarning(pid, self.byte2utf(title)))
        db_session.commit()

    def reload_listpages_have_sfnTpl(self):
        """Загрузка списка страниц имеющих шаблоны типа {{sfn}}, и обновление ими базы данных"""
        w_pages_with_sfns = wdb.get_listpages_have_sfnTpl()  # long query ~45000 rows

        # db_pages = Session.query(PageWithSfn.page_id, PageWithSfn.title, Timecheck.timecheck) \
        #     .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id).all()
        db_pages = db_session.query(PageWithSfn).all()

        # чистка PageWithSfn
        self.drop_orphan_sfnpages(w_pages_with_sfns, db_pages)

        # upsert
        for page_id, title, timelastedit in w_pages_with_sfns:
            db_session.merge(PageWithSfn(page_id, self.byte2utf(title), int(timelastedit)))

        # слишком долгая операция
        # for page_id, title, timelastedit in w_pages_with_sfns:
        #     for db in db_pages:
        #         if page_id == db.page_id:
        #             if int(timelastedit) >= int(db.timecheck) or title.decode("utf-8") != db.title:
        #                 db_session.merge(PageWithSfn(page_id, self.byte2utf(title), int(timelastedit)))
        #             break

        # очистка и перезаливка таблицы
        # не подходит - если удалять все, то параметр ForeignKey ondelete="CASCADE" удалит и все проверки
        # if len(w_pages_with_sfns) > 10000:  # 10000 иногда возвращается обрезанный результат
        #     db_session.query(PageWithSfn).delete()
        # w_pages_with_sfns = [PageWithSfn(id, self.byte2utf(title), int(timelastedit))
        #                      for id, title, timelastedit in w_pages_with_sfns]
        # db_session.bulk_save_objects(w_pages_with_sfns)
        # long query
        db_session.commit()

    @staticmethod
    def drop_orphan_sfnpages(w_pages_with_sfns, db_pages):
        print('Doing drop_orphan_sfnpages')
        db_pages_ids = {p.page_id for p in db_pages}
        w_pages_ids = {page_id for page_id, title, timelastedit in w_pages_with_sfns}
        delta = db_pages_ids - w_pages_ids
        if delta:
            db_session.query(PageWithSfn).filter(PageWithSfn.page_id.in_(delta)).delete(synchronize_session='fetch')
            db_session.commit()

    @staticmethod
    def drop_orphan_by_timecheck():
        """Если в pages нет записи о статье, то удалить ее строки из timecheck"""
        print('Doing drop_orphan_by_timecheck')
        pages = db_session.query(Timecheck.page_id).outerjoin(PageWithSfn) \
            .filter(PageWithSfn.page_id.is_(None)).all()
        for p in pages:
            db_session.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete()
        db_session.commit()

    @staticmethod
    def drop_refs_of_changed_pages():
        print('Doing drop_refs_of_changed_pages')
        pages = db_session.query(ErrRef.page_id).outerjoin(PageWithSfn).filter(PageWithSfn.page_id.is_(None)).all()
        # for p in pages:
        #     db_session.query(ErrRef).filter(ErrRef.page_id == p.page_id).delete(synchronize_session='fetch')
        db_session.query(ErrRef).filter(ErrRef.page_id.in_(pages)).delete(synchronize_session='fetch')

        # subq = db_session.query(PageWithSfn.page_id)
        # db_session.query(ErrRef).filter(ErrRef.page_id.in_(subq)).delete(synchronize_session='fetch')
        # db_session.query(ErrRef.page_id).outerjoin(SfnPageChanged).filter(SfnPageChanged.page_id.is_(None)).delete()  # DELETE do not work with JOIN
        db_session.commit()

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
