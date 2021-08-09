from abc import ABCMeta, abstractmethod
import requests
import lxml.html
import pandas as pd
import time

class WebScrape(metaclass=ABCMeta):
    def __init__(self):
        self.session = requests.Session()
        self.df = pd.DataFrame()
        self.headers = {}
        
    def get_element(self, url, cssselect_expr=None):
        response = self.session.get(url, headers=self.headers)
        element = lxml.html.fromstring(response.content)
        element.make_links_absolute(response.url)
        time.sleep(0.8)
        return element

    def get_elems_by_elem(self, element, cssselect_expr):
        for elem in element.cssselect(cssselect_expr):
            yield elem

    def get_url_by_elem(self, element, cssselect_expr_a):
        for a in element.cssselect(cssselect_expr_a):
            link_url = a.get('href')
            yield link_url

    def get_url_by_url(self, url, cssselect_expr_a):
        element = self.get_element(url)
        link_urls = self.get_url_by_elem(element, cssselect_expr_a)
        for link_url in link_urls:
            yield link_url

    def get_record_by_url(self, url):     
        element = self.get_element(url)
        return self.get_record_by_elem(element)

    @abstractmethod
    def get_record_by_elem(self, element):
        pass

    @abstractmethod
    def scrape_all(self, url):
        pass

    def paging_exe(self, first_element, scrape_func, get_next_func):
        element = first_element
        while True:
            scrape_func(element)
            
            next_page_url = get_next_func(element)
            if next_page_url == None:
                break
            #time.sleep(1)
            print(next_page_url)
            element = self.get_element(next_page_url)

    #def get_next_page_url(self, element):
    #    pass


class Iterator(metaclass=ABCMeta):
    def has_next():
        pass

    def next():
        pass


class WebPage(metaclass=ABCMeta):
    @abstractmethod
    def parse_page(self):
        pass

    @abstractmethod
    def parse_elem(self):
        pass

    @abstractmethod
    def parse_url(self):
        pass

    @abstractmethod
    def next_page(self):
        pass

    @abstractmethod
    def get_record(self):
        pass

