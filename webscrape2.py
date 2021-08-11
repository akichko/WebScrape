from abc import ABCMeta, abstractmethod
#import webscrape as ws
import requests
#import lxml.html
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

class WebScrape2(metaclass=ABCMeta):
    def __init__(self):
        self.session = requests.Session()
        self.headers = {}
        self.cookies = {}
        self.get_interval = 0.7

    def get_element_by_url(self, url, cssselect_expr=None):
        response = self.session.get(url, headers=self.headers, cookies=self.cookies)
        response.encoding = response.apparent_encoding
        #self.cookie = response.cookies
        time.sleep(self.get_interval)
        soup = BeautifulSoup(response.text, 'lxml')
        for a in soup.find_all('a'):
            a.attrs['href'] = urljoin(url,a.get('href'))
        
        if cssselect_expr != None:
            return soup.select(cssselect_expr)
        else:
            return soup

    def exe_scrape(self, url, scraper):
        first_elem = self.get_element_by_url(url)
        scraper.set_elem(first_elem)
        return scraper.scrape()


class Scraper(metaclass=ABCMeta):
    def __init__(self, elem, webscrape):
        self.webscrape = webscrape
        self.elem = elem
        self.df = pd.DataFrame()

    def set_elem(self, elem):
        self.elem = elem

    def scrape(self):
        #element = first_element
        while True:
            sub_scrapers = self.get_sub_scrapers()
            for sub_elem in sub_scrapers:
                df_tmp = sub_elem.scrape()
                self.df = self.df.append(df_tmp, ignore_index=True)
            self.update_df()
            
            next_elem = self.get_next_elem()
            if next_elem == None:
                break
            self.elem = next_elem

        return self.df

    def get_sub_scrapers(self):
        return []

    def update_df(self):
        pass

    def get_next_elem(self):
        pass
