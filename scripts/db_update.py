# coding: utf-8
# author: https://github.com/vladiscripts
#
from scripts.__init__ import *
from scripts.db_models import PageWithSfn, ErrRef, PageWithWarning, Timecheck
from scripts import wdb


class UpdateDB:
    def __init__(self, db):
        self.db = db

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
        self.drop_orphan_errrefs()

    def reload_listpages_have_WarningTpl(self):
        """Обновить список страниц имеющих установленный шаблон."""
        w_pages = wdb.get_listpages_have_WarningTpl()
        self.db.query(PageWithWarning).delete()
        for pid, title in w_pages:
            self.db.add(PageWithWarning(pid, title))
        self.db.commit()

    def reload_listpages_have_sfnTpl(self):
        """Загрузка списка страниц имеющих шаблоны типа {{sfn}}, и обновление ими базы данных"""
        w_pages_with_sfns = wdb.get_listpages_have_sfnTpl()  # long query ~45000 rows

        # db_pages = self.db_session.query(PageWithSfn.page_id, PageWithSfn.title, Timecheck.timecheck) \
        #     .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id).all()
        db_pages = self.db.query(PageWithSfn).all()

        # чистка PageWithSfn
        self.drop_orphan_sfnpages(w_pages_with_sfns, db_pages)

        # upsert
        logging.info('Update of timelastedits on merge in reload_listpages_have_sfnTpl')
        for page_id, title, timelastedit in w_pages_with_sfns:
            self.db.merge(PageWithSfn(page_id, title, int(timelastedit)))

        # слишком долгая операция
        # for page_id, title, timelastedit in w_pages_with_sfns:
        #     for db in db_pages:
        #         if page_id == db.page_id:
        #             if int(timelastedit) >= int(db.timecheck) or title.decode("utf-8") != db.title:
        #                 self.db_session.merge(PageWithSfn(page_id, self.byte2utf(title), int(timelastedit)))
        #             break

        # очистка и перезаливка таблицы
        # не подходит - если удалять все, то параметр ForeignKey ondelete="CASCADE" удалит и все проверки
        # if len(w_pages_with_sfns) > 10000:  # 10000 иногда возвращается обрезанный результат
        #     self.db_session.query(PageWithSfn).delete()
        # w_pages_with_sfns = [PageWithSfn(id, self.byte2utf(title), int(timelastedit))
        #                      for id, title, timelastedit in w_pages_with_sfns]
        # self.db_session.bulk_save_objects(w_pages_with_sfns)
        # long query
        self.db.commit()

    def drop_orphan_sfnpages(self, w_pages_with_sfns, db_pages):
        logging.info('Drop_orphan_sfnpages')
        db_pages_ids = {p.page_id for p in db_pages}
        w_pages_ids = {page_id for page_id, title, timelastedit in w_pages_with_sfns}
        delta = db_pages_ids - w_pages_ids
        if delta:
            self.db.query(PageWithSfn).filter(PageWithSfn.page_id.in_(delta)).delete(synchronize_session='fetch')
            self.db.commit()

    def drop_orphan_by_timecheck(self):
        """Если в pages нет записи о статье, то удалить ее строки из timecheck"""
        logging.info('Drop_orphan_by_timecheck')
        pages = self.db.query(Timecheck.page_id).outerjoin(PageWithSfn).filter(
            PageWithSfn.page_id.is_(None)).all()
        for p in pages:
            self.db.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete()
        self.db.commit()

    def drop_orphan_errrefs(self):
        logging.info('Drop_refs_of_changed_pages')
        # pages = Session.query(ErrRef.page_id).outerjoin(PageWithSfn).filter(PageWithSfn.page_id.is_(None)).all()
        # for p in pages:  # DELETE do not work with JOIN
        #     Session.query(ErrRef).filter(ErrRef.page_id == p.page_id).delete(synchronize_session='fetch')
        pages = (p.page_id for p in
                 self.db.query(ErrRef.page_id).outerjoin(PageWithSfn).filter(PageWithSfn.page_id.is_(None)).all())
        self.db.query(ErrRef).filter(ErrRef.page_id.in_(pages)).delete(synchronize_session='fetch')
        self.db.commit()

    def drop_timechecks_of_erropages(self):
        logging.info('Drop_timechecks_of_erropages')
        # pages = self.db_session.query(ErrRef.page_id).all()
        # for p in pages:
        #     self.db_session.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete(synchronize_session='fetch')
        pages = (p.page_id for p in self.db.query(ErrRef.page_id).all())
        self.db.query(Timecheck).filter(Timecheck.page_id.in_(pages)).delete(synchronize_session='fetch')
        self.db.commit()

    # Helpers
    def drop_check_pages_with_warnings(self):
        """Удаление метки проверки у страниц имеющих warning-шаблон."""
        pages = self.db.query(PageWithWarning.page_id).all()
        for p in pages:
            self.db.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete(synchronize_session='fetch')
        self.db.commit()

    def drop_all_check_pages(self):
        """Очистка таблицы Timecheck: удаление метки проверки у всех страниц"""
        self.db.query(Timecheck).delete()
        self.db.commit()

    def drop_all_refs(self):
        """Очистка таблицы Refs"""
        self.db.query(ErrRef).delete()
        self.db.commit()
