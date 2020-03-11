import unittest
import re
from datetime import datetime, timezone
import pathlib
from vladi_helpers.file_helpers import json_load_from_file, json_save_to_file, file_save
from settings import *
from scripts.logger import logger
from scripts import scan_pages
from scripts import scan_pages_multithreads
from scripts.db_update import UpdateDB
from scripts.make_listspages import save_listpages_for_add_warning_tpls, save_listpages_for_remove_warning_tpls
from scripts.make_wikilists import make_and_save_wikilist


class TestProblem1(unittest.TestCase):

    # def setUp(self):
    #     self.gigs_formed_subcategory = json_load_from_file('gigs_formed_subcategory.json')
    #     # gigs_formed_subcategory = json_save_to_file('gigs_formed_subcategory.json', gigs_formed_subcategory)
    #
    #     # datetime_utc = datetime.now(timezone.utc)
    #     columnswidth = False
    #     # self.sheets = make_sheets.MakeSheets(columnswidth)
    #     # self.fileops = operating_xls_files.OperatingXlsFiles(datetime_utc, outdirectory_general='test_results')
    #
    #     self.datetime_utc = datetime.now(timezone.utc)
    #     self.re_j = re.compile(r"gigData\s*=\s*{(.*?)}", flags=re.S)
    #     self.re_b = re.compile(r"(^|,)(\s*[^\s]+\s*:)", flags=re.S)
    #
    #     self.session = helpers.open_requests_session(None)
    #     self.makesheets = make_sheets.MakeSheets(None)
    #     self.fileops = operating_xls_files.FormatPath(self.datetime_utc)
    #
    #     self.packages_formed_subcategory = []
    #
    #     self.run = fiverr_crawler.Run()
    #
    #     class Set_fmeta:
    #         re_truncate = re.compile(r'^(\w+(?:\W\w{,3})?)')
    #         subcategory_meta = ('Digital Marketing', 2, 'Marketing Strategy', 218)
    #         cname, cid = subcategory_meta[0], subcategory_meta[1]
    #         sname, sid = subcategory_meta[2], subcategory_meta[3]
    #         cnameshort = re_truncate.search(cname).group(1)
    #         snameshort = re_truncate.search(sname).group(1)
    #         catname, scatname = f'{cnameshort}_{cid}', f'{snameshort}_{sid}'
    #         outdir_base = f'gigs/{catname}' + '_{datetime}'
    #         f_dir = f'{snameshort}' + '_{datetime}'
    #
    #     self.d = Set_fmeta()

    # @unittest.skip("skipping")

    @unittest.skip("skipping")
    def test_download(self):
        downloader = Downloader()
        fcontent = downloader.download_file()
        pathlib.Path('tests/PET_CONS_PSUP_DC_NUS_MBBLPD_M.xls')
        file_save(f'tests/{downloader.file_name}', fcontent)

    @unittest.skip("skipping")
    def test_recheck_lists(self):
        scanner = scan_pages_multithreads.ScannerMultithreads()
        scanner.recheck_lists()

        # excelfile = 'tests/PET_CONS_PSUP_DC_NUS_MBBLPD_M.xls'
        # # parse_pandas(filename=excelfile)
        # df,names = parse_pandas2(filename=excelfile)
        # put_rows_to_db(df,names)

    # @unittest.skip("skipping")
    def test_do_scan_multithreads(self):
        scanner = scan_pages_multithreads.ScannerMultithreads()
        scanner.threads_num = 3
        scanner.pages_limit_by_query = 3
        scanner.queue_len = 3
        scanner.do_scan(test=True)

        # excelfile = 'tests/PET_CONS_PSUP_DC_NUS_MBBLPD_M.xls'
        # # parse_pandas(filename=excelfile)
        # df,names = parse_pandas2(filename=excelfile)
        # put_rows_to_db(df,names)

    @unittest.skip("skipping")
    def test_allInOne_sheet(self):
        d = self.d
        catname, scatname = d.catname, d.scatname
        outdir_base, f_dir = d.outdir_base, d.f_dir

        limit_rows = 100
        keywords_filter = None
        sort_reverse = True
        sort_by = None
        self.sheets.gigs_sorted_manyonesheet(
            self.gigs_formed_subcategory, sort_by, sort_reverse, limit_rows, keywords_filter)

        f_filename = f'top100allInOne_{catname}_{scatname}' + '_{datetime}.xlsx'
        self.fileops.save(self.sheets.wb, outdir_base=outdir_base, f_dir=f_dir, filename=f_filename)

        print()

    @unittest.skip("skipping")
    def test_sheets_makesave_subcategory(self):
        # run = fiverr_crawler.Run()
        # fiverr_crawler.Run().sheets_makesave_subcategory(
        self.run.sheets_makesave_subcategory(
            self.d.subcategory_meta, self.gigs_formed_subcategory, self.packages_formed_subcategory,
            limit_rows=20, keywords_filter='seo, plan')
        print()

    @unittest.skip("skipping")
    def test_format_filenames(self):
        cname, cid = "Graphics \u0026 Design", 3
        sname, sid = "Business Cards \u0026 Stationery", 56

        outdir_base = 'gigs'
        f_string = f'{cname}_{cid}_{sname}_{sid}'
        f_dir = '{datetime}_' + f'{cname}_{cid}'
        # f_dir = f'gigs_{cname}_{cid}'
        f_filename = '{datetime}_{string}.xlsx'
        self.fileops.format_path_output(f_string, f_dir, f_filename, outdir_general=outdir_base)

        fn_outpath_general = self.fileops.outdir_base
        fn_outpath = self.fileops.outdir
        fn_filename = self.fileops.filename
        fn_filepath = self.fileops.filepath
        print()

    @unittest.skip("skipping")
    def test_make_sheets_gigs_formed(self):
        self.sheets.gigs(self.gigs_formed_subcategory)
        f_dir = 'results'
        self.fileops.save(self.sheets.wb, f_string="gigs", f_dir=f_dir, filename='{string}_({datetime}).xlsx')

    @unittest.skip("skipping")
    def test_make_sheets_gigs_formed_sorted(self):
        d = self.d
        catname, scatname = d.catname, d.scatname
        outdir_base, f_dir = d.outdir_base, d.f_dir

        # Make resorted
        limit_rows = 100
        sort_reverse = True
        keywords_filter = None
        metafiles = (
            ('rating_count', 'top{limitrows}rating_count_{datetime}.xlsx'),
            ('rating_velocity', 'top{limitrows}rating_velocity_{datetime}.xlsx'),
            ('gig_created', 'top{limitrows}gig_created_{datetime}.xlsx'),
            ('fastest_delivery_time', 'top{limitrows}fastest_delivery_time_{datetime}.xlsx'),
            ('avg_delivery_time', 'top{limitrows}avg_delivery_time_{datetime}.xlsx'),
        )
        for sort_by, f_filename in metafiles:
            if sort_by in ['fastest_delivery_time', 'avg_delivery_time']:
                sort_reverse = False
            f_filename = f'{catname}_{scatname}_' + f_filename.replace('{limitrows}', str(limit_rows))

            self.sheets.gigs_sorted(self.gigs_formed_subcategory, sort_by, sort_reverse, limit_rows,
                                    keywords_filter)

            self.fileops.save(self.sheets.wb, outdir_base=outdir_base, f_dir=f_dir, filename=f_filename)

        print()


if __name__ == '__main__':
    unittest.main()
