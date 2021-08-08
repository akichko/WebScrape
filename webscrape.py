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
        
    def get_url_by_elem(self, element, cssselect_expr_a):
        body = lxml.html.fromstring(element.content)
        body.make_links_absolute(element.url)
        for a in body.cssselect(cssselect_expr_a):
            link_url = a.get('href')
            yield link_url

    def get_url_by_url(self, url, cssselect_expr_a):
        response = self.session.get(url, headers=self.headers)
        link_urls = self.get_url_by_elem(response, cssselect_expr_a)
        for link_url in link_urls:
            yield link_url

    def get_record_by_url(self, url):        
        response = self.session.get(url, headers=self.headers)
        body = lxml.html.fromstring(response.content)
        return self.get_record_by_elem(body)

    @abstractmethod
    def get_record_by_elem(self, element):
        pass

    @abstractmethod
    def scrape_all(self, url):
        pass

    def paging_exe(self, element, scrape_func, *args):
       while True:
            scrape_func(element, *args)
            
            next_page_url = self.get_next_page_url(element)
            if next_page_url == None:
                break
            time.sleep(1)
            response = self.session.get(next_page_url, headers=self.headers)
            element = lxml.html.fromstring(response.content)
            element.make_links_absolute(response.url)
        #return self.df

#    @abstractmethod
#    def get_next_page(self, response):
#        pass
        
