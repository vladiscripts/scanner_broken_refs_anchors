# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import re
from lxml.html import tostring, fromstring

tag_a = re.compile(r'<a [^>]*>(.*?)</a>', re.DOTALL)


def ScanRefsOfPage(html):
    # """ Разница списков сносок с имеющейся библиографией. Возращает: self.full_errrefs """
    htmltree = fromstring(html)

    list_sfns, all_sfns_info = find_sfns_on_page(htmltree)
    list_citations = find_citations_on_page(htmltree)

    # список сносок с отсутствующими ссылками, из сравнения списков сносок и примечаний
    err_citerefs = list_sfns - list_citations

    err_refs = []
    if err_citerefs:
        for c in sorted(err_citerefs):
            for sfn in all_sfns_info:
                if c == sfn.citeref:
                    err_refs.append(sfn)
                    break
    return err_refs


def find_sfns_on_page(htmltree):
    """ Список сносок из раздела 'Примечания'.
    Возвращает:
    self.list_sfns - список только sfn-id
    self.all_sfn_info_of_page - полный список
    """
    list_sfns = set()
    all_sfns_info = []

    for li in htmltree.cssselect("ol.references li[id^='cite']"):
        for a in li.cssselect("span.reference-text a[href^='#CITEREF']"):
            aText = tag_a.search(str(tostring(a, encoding='unicode'))).group(1)
            idRef = a.attrib['href'].lstrip('#')
            list_sfns.add(idRef)
            all_sfns_info.append(
                {'citeref': idRef, 'text': aText, 'link_to_sfn': str(li.attrib['id'])})
            # return list_sfns, all_sfns_info
    return list_sfns, all_sfns_info


def find_citations_on_page(htmltree):
    """ Список id библиографии. Возвращает: self.list_refs """
    # cssselect использован для надёжности.
    # В xpath сложней выбор по классу, когда в атрибутах их несколько через пробел
    return {e.attrib['id'] for css in ['span.citation[id^="CITEREF"]', 'cite[id^="CITEREF"]']
            for e in htmltree.cssselect(css)}

#     # def error_print(self, error):
# 	error_text = 'Error "{}" on parsing footnotes of page "{}"'.format(error, self.title)
# 	print(error_text)
# 	file_savelines(filename_error_log, error_text)
