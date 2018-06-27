# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import re

from lxml.html import tostring, fromstring

tag_a = re.compile(r'<a [^>]*>(.*?)</a>', re.DOTALL)


class ScanRefsOfPage:
    def __init__(self, html):
        self.list_sfns = set()
        self.list_citations = set()
        self.all_sfns_info = []
        self.err_refs = []
        self.htmltree = fromstring(html)
        self.find_sfns_on_page()
        self.find_citations_on_page()
        self.compare_refs()

    def find_sfns_on_page(self):
        """ Список сносок из раздела 'Примечания'.
        Возвращает:
        self.list_sfns - список только sfn-id
        self.all_sfn_info_of_page - полный список
        """
        try:
            for li in self.htmltree.cssselect("ol.references li[id^='cite']"):
                for a in li.cssselect("span.reference-text a[href^='#CITEREF']"):
                    aText = tag_a.search(str(tostring(a, encoding='unicode'))).group(1)
                    idRef = a.attrib['href'].lstrip('#')
                    self.list_sfns.add(idRef)
                    self.all_sfns_info.append(
                        {'citeref': idRef, 'text': aText, 'link_to_sfn': str(li.attrib['id'])})

        except Exception as error:
            # self.error_print(error)
            pass

    def find_citations_on_page(self):
        """ Список id библиографии. Возвращает: self.list_refs """
        try:
            # cssselect использован для надёжности.
            # В xpath сложней выбор по классу, когда в атрибутах их несколько через пробел
            self.list_citations = {e.attrib['id'] for css in ['span.citation[id^="CITEREF"]', 'cite[id^="CITEREF"]']
                                   for e in self.htmltree.cssselect(css)}

        except Exception as error:
            # self.error_print(error)
            pass

    def compare_refs(self):
        """ Разница списков сносок с имеющейся библиографией. Возращает: self.full_errrefs """
        # список сносок с отсутствующими ссылками, из сравнения списков сносок и примечаний
        err_refs = self.list_sfns - self.list_citations
        # Если в статье есть некорректные сноски без целевых примечаний
        if err_refs:
            self.err_refs = []
            for citeref_bad in sorted(err_refs):
                it_sfn_double = False
                for sfn in self.all_sfns_info:
                    if citeref_bad == sfn['citeref'] and not it_sfn_double:
                        self.err_refs.append(sfn)
                        it_sfn_double = True

# def error_print(self, error):
# 	error_text = 'Error "{}" on parsing footnotes of page "{}"'.format(error, self.title)
# 	print(error_text)
# 	file_savelines(filename_error_log, error_text)
