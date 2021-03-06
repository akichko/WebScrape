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

import webscrape as ws
import re
import pandas as pd
import time
import urllib.parse

class WebScrapeNifty(ws.WebScrape3):

    kanto = {
        'tokyo' : {
            't23_w' : ['nerimaku','setagayaku','shinjukuku','nakanoku','suginamiku','shibuyaku'],
            't23_n' : ['itabashiku','toshimaku','bunkyoku','adachiku','kitaku','arakawaku'],
            't23_e' : ['katsushikaku','edogawaku','taitoku','kotoku','sumidaku','chuoku'],
            't23_s' : ['minatoku','shinagawaku','otaku','meguroku','chiyodaku']
        },

        'ibaraki' : {
            'mito' : ['mitoshi','hitachinakashi']
        },

        'kanagawa' : {
            'yk_e' : ['yokohamashitsurumiku','yokohamashikanagawaku','yokohamashinishiku','yokohamashinakaku'],
            'yk_n' : ['yokohamashikohokuku','yokohamashiaobaku','yokohamashitsuzukiku','yokohamashimidoriku','yokohamashitotsukaku'],
            'yk_s' : ['yokohamashisakaeku','yokohamashiisogoku','yokohamashikanazawaku','yokohamashikonanku','yokohamashiminamiku'],
            'yk_w' : ['yokohamashiseyaku','yokohamashiizumiku','yokohamashiasahiku','yokohamashihodogayaku'],
            'kwsk' : ['kawasakishikawasakiku','kawasakishisaiwaiku','kawasakishinakaharaku','kawasakishitakatsuku', \
                        'kawasakishitamaku','kawasakishimiyamaeku','kawasakishiasaoku']
        }
    }
 
    def __init__(self, webaccess : ws.WebAccess):
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        webaccess.headers = {'User-Agent': ua}
        super().__init__(webaccess)
  
    def __make_url(self, prefecture, area, max_price, max_year):
        min_m2 = 20
        max_dist_station = 15
        #&subtype=buc //?????????????????????
        #buh& //??????????????????
        #b2=15000000 //???????????????b1=?????????
        #&b10=20 //????????????(m2)
        #&b6=15 //??????????????????
        #b22=40 //?????????
        #max_price = 15000000
        url = "https://myhome.nifty.com/chuko/mansion/kanto/" \
            + prefecture \
            + "/?cities=" + re.sub("[\[\]\'\ ]","", str(self.kanto[prefecture][area])) \
            + "&subtype=buc" \
            + "&b2=" + str(max_price) \
            + "&b10=" + str(min_m2) \
            + "&b6=" + str(max_dist_station) \
            + "&b22=" + str(max_year)
        return url

    def scrape_all(self, pref, area, max_price, max_year):
        print("start")
        #self.pref = pref
        #self.area = area
        url = self.__make_url(pref, area, max_price, max_year)
        print(url)

        df = self.exe_scraping(url)

        df['pref'] = pref
        df['area'] = area

        print("end")
        return df

    def get_scraper(self, elem) -> ws.Scraper: #override
        return Scraper_ListPage(elem, self.webaccess)


class Scraper_ListPage(ws.Scraper):
    def get_sub_scrapers(self): #override
        nayoses = self.elem.css_select(".nayose")
        for nayose in nayoses:
            print(nayose.get_attr_value('data-name'))
            yield Scraper_Nayose(nayose, self.webaccess)

    def get_next_elem(self): #override
        elems = self.elem.css_select(".pageNation li.mg3 a")
        for a in elems:
            if a.text == "??????>":
                print(a.get_attr_value('href'))
                return self.webaccess.get_element_by_url(a.get_attr_value('href'))


class Scraper_Nayose(ws.Scraper):

    def get_sub_scrapers(self):
        nayose = self.elem

        self.nayose_url = self.__get_nayose_url(nayose)
        #print(nayose.get('data-name'))
        print(self.nayose_url)
        elem_nayose_page = self.webaccess.get_element_by_url(self.nayose_url)
        
        #??????????????????????????????
        yield self.__get_sub_scraper(nayose, elem_nayose_page)
   
    def __get_sub_scraper(self, nayose, elem_nayose_page) -> ws.Scraper:        
        elem_link = nayose.css_select_one(".shinchiku_manshion .data .company")
        if elem_link.css_select('.athomef'):
            #print('at home')
            return Scraper_Detail_atHome(elem_nayose_page, self.webaccess, 'at home')

        elif elem_link.css_select('.yahoof'):
            #print('yahoo')
            return Scraper_Detail_basic(elem_nayose_page, self.webaccess, 'yahoo')

        elif elem_link.css_select('.forrenf'):
            #print('suumo')
            return Scraper_Detail_basic(elem_nayose_page, self.webaccess, 'suumo') #suumo

        elif elem_link.css_select('.adparkf'):
            print('adpark')
            return Scraper_Detail_basic(elem_nayose_page, self.webaccess, 'adpark') #NG

        else:
            print('other')
            return Scraper_Detail_basic(elem_nayose_page, self.webaccess, 'other')

    def __get_nayose_url(self, nayose):
        a = nayose.css_select_one(".nayose_head > p > a")
        url = a.get_attr_value('href')
        if re.search(r'/mansion/detail/', url):
            qs  = urllib.parse.urlparse(url)
            qsdic = urllib.parse.parse_qs(qs.query)

            url = urllib.parse.unquote(qsdic['url'][0])
        return url 

    def update_df(self):
        #print("get_df : nayose")

        record = self.__get_simple_record()
        record['data-name'] = self.elem.get_attr_value('data-name')
        record['url'] = self.nayose_url
        record['cate'] = self.elem.css_select_one("span.cate").text
        
        if self.df.empty:
            self.df = pd.DataFrame(record, index=[0])

        for e in record:
            self.df[e] = record[e]

    def __get_simple_record(self):
        keys = self.elem.css_select(".itemContent dt")
        values = self.elem.css_select(".itemContent dd")
        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}
        return record


class Scraper_Detail_basic(ws.Scraper):
    def __init__(self, elem, webaccess, company):
        super().__init__(elem, webaccess)
        self.company = company

    def update_df(self):
        #print("get_df : detail")
        element = self.elem
        keys = element.css_select('#detailInfoTable tr th')
        if len(keys) == 0:
            return None
        values = element.css_select('#detailInfoTable tr td')
        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}
        if len(element.css_select('.titleMain .name')) > 0:
            record['name'] = element.css_select('.titleMain .name')[0].text
        if len(element.css_select('.otherPrice')) > 0:
            record['othercost'] = element.css_select('.otherPrice')[0].text
            
        keys2 = element.css_select('.unitDetail .detailBox dt')
        values2 = element.css_select('.unitDetail .detailBox dd')
        record2 = {keys2[i].text: values2[i].text.strip() for i in range(len(keys2))}
        record.update(record2)

        record['site'] = self.company

        self.df = pd.DataFrame(record, index=[0])
        #return pd.DataFrame.from_dict(record, orient='index')


class Scraper_Detail_atHome(ws.Scraper):
    def __init__(self, elem, webaccess, company):
        super().__init__(elem, webaccess)
        self.company = company

    def update_df(self):
        elem_athome_page = self.elem
        keys = elem_athome_page.css_select('.wrapLeftnoMap tr th')
        if len(keys) == 0:
            return None
        values = elem_athome_page.css_select('.wrapLeftnoMap tr td')
        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}

        record['name'] = record['????????????????????????']
        record['site'] = self.company

        self.df = pd.DataFrame(record, index=[0])
        #return pd.DataFrame.from_dict(record, orient='index')
