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
        
    @property
    def text(self):
        return self.elem.text

    @abstractmethod
    def css_select(select_str) -> 'WebElement':
        pass

    @abstractmethod
    def css_select_one(select_str) -> 'WebElement':
        pass

    @abstractmethod
    def get_attr_value(self, attr_name):
        pass


class WebElement_bs(WebElement):
    def __init__(self, elem : Tag):
        self.elem = elem

    @classmethod
    def create_by_rq_response(self, response) -> WebElement:
        elem = BeautifulSoup(response.text, 'lxml')
        for a in elem.find_all('a'):
            a.attrs['href'] = urljoin(response.url,a.get('href'))
        return WebElement_bs(elem)

    #@classmethod
     #def create_by_urlib_response(self, response) -> WebElement:
     #    return WebElement_bs(BeautifulSoup(response, 'lxml'))

    def css_select(self, select_str) -> WebElement: #override
        ret = []
        for elem in self.elem.select(select_str):
            ret.append(WebElement_bs(elem))
        return ret

    def css_select_one(self, select_str) -> WebElement: #override
        return WebElement_bs(self.elem.select_one(select_str))

    #override
    def get_attr_value(self, attr_name):
        return self.elem.get(attr_name)


#class WebElement_lxml(WebElement):
 #    def __init__(self, elem):
 #        self.elem = elem
 #
 #    def create_by_rq_response(self, response) -> WebElement:
 #        element = lxml.html.fromstring(response.content)
 #        element.make_links_absolute(response.url)
 #        return WebElement_lxml(element)
 #
 #    def create_by_urlib_response(self, response) -> WebElement:
 #        pass#return WebElement_lxml#(BeautifulSoup(response, 'lxml'))
 #
 #    def css_select(self, select_str) -> WebElement:
 #        pass
 #    def css_select_one(self, select_str) -> WebElement:
 #        pass
    
# WebAccess #######################################

class WebAccess(metaclass=ABCMeta):
    def __init__(self):
        self.headers = {}
        self.cookies = {}
        self.get_interval = 0.7

    @abstractmethod
    def get_WebElement(self, url) -> WebElement:
        pass

    def get_element_by_url(self, url):
        return self.get_WebElement(url)


class WebAccess_Rq(WebAccess):
    def __init__(self, elem_type):
        super().__init__()
        self.session = requests.Session()
        self.elem_type = elem_type

    def get_WebElement(self, url) -> WebElement: #override
        response = self.session.get(url, headers=self.headers, cookies=self.cookies)
        response.encoding = response.apparent_encoding
        #self.cookie = response.cookies
        time.sleep(self.get_interval)

        if self.elem_type == 'bs':
            elem = WebElement_bs.create_by_rq_response(response)
        #if lxlm
        #elem = WebElement_lxml.create_by_rq_response(response)
        else:
            raise ValueError("error!")

        return elem

# Scraper #######################################

class Scraper(metaclass=ABCMeta):
    def __init__(self, elem, webaccess):
        self.webaccess = webaccess
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

# WebScrape #######################################

class WebScrape3(metaclass=ABCMeta):
    def __init__(self, webaccess : WebAccess):
        self.webaccess = webaccess

    def exe_scraping(self, url):
        elem = self.webaccess.get_WebElement(url)
        scraper = self.get_scraper(elem)
        df = scraper.scrape()
        self.update_df()
        return df

    @abstractmethod
    def get_scraper(self, elem) -> Scraper:
        pass

    def update_df(self):
        pass


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
