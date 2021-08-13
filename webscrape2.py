## MIT License
 #
 # Copyright (c) 2021 akichko
 # 
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:
 # 
 # The above copyright notice and this permission notice shall be included in all
 # copies or substantial portions of the Software.
 # 
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 # SOFTWARE.

from abc import ABCMeta, abstractmethod
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
import time
from urllib.parse import urljoin
import lxml.html

# WebElement #######################################

class WebElement(metaclass=ABCMeta):
        
    @abstractmethod
    def css_select(select_str) -> 'WebElement':
        pass

    @abstractmethod
    def css_select_one(select_str) -> 'WebElement':
        pass

class WebElement_bs(WebElement):
    def __init__(self, elem : Tag):
        self.elem = elem

    def create_by_rq_response(self, response) -> WebElement:
        elem = BeautifulSoup(response.text, 'lxml')
        for a in elem.find_all('a'):
            a.attrs['href'] = urljoin(response.url,a.get('href'))
        return WebElement_bs(elem)

    def create_by_urlib_response(self, response) -> WebElement:
        return WebElement_bs(BeautifulSoup(response, 'lxml'))

    def css_select(self, select_str) -> WebElement:
        ret = []
        for elem in self.elem.select(select_str):
            ret.append(WebElement_bs(elem))
        return ret

    def css_select_one(self, select_str) -> WebElement:
        return WebElement_bs(self.elem.select_one(select_str))


class WebElement_lxml(WebElement):
    def __init__(self, elem):
        self.elem = elem

    def create_by_rq_response(self, response) -> WebElement:
        element = lxml.html.fromstring(response.content)
        element.make_links_absolute(response.url)
        return WebElement_lxml(element)

    def create_by_urlib_response(self, response) -> WebElement:
        pass#return WebElement_lxml#(BeautifulSoup(response, 'lxml'))

    def css_select(self, select_str) -> WebElement:
        pass
    def css_select_one(self, select_str) -> WebElement:
        pass
    
# WebAccess #######################################

class WebAccess(metaclass=ABCMeta):
    def __init__(self, web_elem_type):
        self.headers = {}
        self.cookies = {}
        self.get_interval = 0.7

    @abstractmethod
    def get_WebElement(self, url) -> WebElement:
        pass


class WebAccess_Rq(WebAccess):
    def __init__(self):
        self.headers = {}
        self.cookies = {}

    def get_WebElement(self, url) -> WebElement:
        response = self.session.get(url, headers=self.headers, cookies=self.cookies)
        response.encoding = response.apparent_encoding
        #self.cookie = response.cookies
        time.sleep(self.get_interval)

        #if bs
        elem = WebElement_bs.create_by_rq_response(response)
        #if lxlm
        #elem = WebElement_lxml.create_by_rq_response(response)

        return elem


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

    def exe_scrape_by_url(self, url, scraper):
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
            for sub_scraper in sub_scrapers:
                df_tmp = sub_scraper.scrape()
                self.df = self.df.append(df_tmp, ignore_index=True)
            self.update_df()
            
            next_elem = self.get_next_elem()
            if next_elem == None:
                break
            self.set_elem(next_elem)

        return self.df

    def get_sub_scrapers(self):
        return []

    def update_df(self):
        pass

    def get_next_elem(self):
        pass
