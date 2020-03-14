from scripts import *
from settings import *


def recheck(scanner, filename: str, type_opp: int):
    lst = file_readlines(filename)
    logger.info(f'\ntest: {filename}, {len(lst)} pages')
    lst_new = []
    for title in lst:
        logger.debug(f'scan: {title}')
        # if title != 'Битва_при_Мьяхадосе':
        #     continue
        err_refs = scanner.scan_page(title)
        if err_refs is None:
            continue
        if type_opp == 1 and len(err_refs) == 0:
            logger.error('no errrefs on page "{title}", where it should be'.format(title=title))
            continue
        elif type_opp == 2 and len(err_refs) > 0:
            logger.error(f'errrefs on page "{title}", where it should not be')
            continue
        lst_new.append(title)
    file_savelines(filename, lst_new)


def recheck_lists(scanner):
    # todo: pid
    # listpages_errref_where_no_yet_warning_tpl
    recheck(scanner, filename_listpages_errref_where_no_yet_warning_tpl, 1)

    # list_to_remove_warning_tpl
    recheck(scanner, filename_listpages_errref_where_no_yet_warning_tpl, 2)
