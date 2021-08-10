from abc import ABCMeta, abstractmethod
#import webscrape as ws
import requests
#import lxml.html
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

class WebScrapeBs():
    def __init__(self):
        self.session = requests.Session()
        self.df = pd.DataFrame()
        self.headers = {}

    def clear_df(self):
        self.df = pd.DataFrame()

    def get_element_by_url(self, url, cssselect_expr=None):
        response = self.session.get(url, headers=self.headers)
        response.encoding = response.apparent_encoding
        time.sleep(0.8)
        soup = BeautifulSoup(response.text, 'lxml')
        for a in soup.find_all('a'):
            a.attrs['href'] = urljoin(url,a.get('href'))
        
        if cssselect_expr != None:
            return soup.select(cssselect_expr)
        else:
            return soup

    #def get_url_by_elem(self, element, cssselect_expr_a):
        #    for a in element.select(cssselect_expr_a):
        #        link_url = a.get('href')
        #        yield link_url

    #def get_url_by_url(self, url, cssselect_expr_a):
        #    element = self.get_element_by_url(url)
        #    link_urls = self.get_url_by_elem(element, cssselect_expr_a)
        #    for link_url in link_urls:
        #        yield link_url

    #def get_record_by_url(self, url):     
        #    element = self.get_element_by_url(url)
        #    return self.get_record_by_elem(element)

    #def get_record_by_elem(self, element):
        #    pass

    def scrape_all(self, url):
        pass

    def paging_exe(self, first_element, scrape_func, get_next_func):
        element = first_element
        while True:
            scrape_func(element)
            
            next_page_url = get_next_func(element)
            if next_page_url == None:
                break
            print(next_page_url)
            element = self.get_element_by_url(next_page_url)


