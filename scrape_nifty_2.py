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

import webscrape2 as ws
import re
import pandas as pd
import time

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
  
    def make_url(self, prefecture, area, max_price, max_year):
        min_m2 = 20
        max_dist_station = 15
        #&subtype=buc //中古マンション
        #buh& //中古一戸建て
        #b2=15000000 //価格上限（b1=下限）
        #&b10=20 //建物面積(m2)
        #&b6=15 //駅からの距離
        #b22=40 //築年数
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
        url = self.make_url(pref, area, max_price, max_year)
        print(url)
        body = webaccess.get_WebElement(url)

        scraper = Scraper_ListPage(body, self.webaccess)
        #scraper = Scraper_ListPage(None, self.webaccess)

        df = scraper.scrape()
        #df = self.exe_scrape_by_url(url, scraper)

        df['pref'] = pref
        df['area'] = area

        print("end")

        return df
        #return self.scrape_all(url)


class Scraper_ListPage(ws.Scraper):
    def get_sub_scrapers(self): #override
        nayoses = self.elem.css_select(".nayose")
        for nayose in nayoses:
            print(nayose.get_attr_value('data-name'))
            yield Scraper_Nayose(nayose, self.webaccess)

    def get_next_elem(self): #override
        elems = self.elem.css_select(".pageNation li.mg3 a")
        for a in elems:
            if a.text == "次へ>":
                print(a.get_attr_value('href'))
                return self.webaccess.get_element_by_url(a.get_attr_value('href'))


class Scraper_Nayose(ws.Scraper):

    def get_sub_scrapers(self):
        nayose = self.elem

        self.nayose_url = self.__get_nayose_url(nayose)
        #print(nayose.get('data-name'))
        print(self.nayose_url)
        elem_nayose_page = self.webaccess.get_element_by_url(self.nayose_url)
        
        #ページ種別で解析切替
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
        return a.get_attr_value('href')

    def update_df(self):
        #print("get_df : nayose")

        record = self.__get_simple_record()
        record['url'] = self.nayose_url
        record['cate'] = self.elem.css_select_one("span.cate").text
        
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
        record['site'] = self.company

        self.df = pd.DataFrame(record, index=[0])
        #return pd.DataFrame.from_dict(record, orient='index')


class Scraper_Detail_atHome(ws.Scraper):
    def __init__(self, elem, webaccess, company):
        super().__init__(elem, webaccess)
        self.company = company

    def update_df(self):
        #print("get_df : detail")
        element = self.elem
        elem_iframe = element.css_select_one('iframe#itemDetailFrame')
        athome_url = elem_iframe.get_attr_value('src')
        elem_athome_page = self.webaccess.get_element_by_url(athome_url)

        keys = elem_athome_page.css_select('.wrapLeftnoMap tr th')
        if len(keys) == 0:
            return None
        values = elem_athome_page.css_select('.wrapLeftnoMap tr td')
        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}

        record['name'] = record['建物名・部屋番号']
        record['site'] = self.company

        self.df = pd.DataFrame(record, index=[0])
        #return pd.DataFrame.from_dict(record, orient='index')


# Main #################################################################

start_time = time.time()
df = pd.DataFrame()

webaccess = ws.WebAccess_Rq("bs")

scraper = WebScrapeNifty(webaccess)

#tokyo
#df_tmp = scraper.scrape_all('tokyo', 't23_e', 20000000, 40)
#df = pd.concat([df,df_tmp])
df_tmp = scraper.scrape_all('tokyo', 't23_s', 20000000, 12)
df = pd.concat([df,df_tmp])
#df_tmp = scraper.scrape_all('tokyo', 't23_w', 20000000, 40)
#df = pd.concat([df,df_tmp])
#df_tmp = scraper.scrape_all('tokyo', 't23_n', 20000000, 40)
#df = pd.concat([df,df_tmp])

#ibaraki
df_tmp = scraper.scrape_all('ibaraki', 'mito', 20000000, 30)
df = pd.concat([df,df_tmp])

#yokohama
#df_tmp = scraper.scrape_all('kanagawa', 'yk_e', 20000000, 40)
#df = pd.concat([df,df_tmp])
#df_tmp = scraper.scrape_all('kanagawa', 'yk_n', 20000000, 40)
#df = pd.concat([df,df_tmp])
#df_tmp = scraper.scrape_all('kanagawa', 'yk_s', 20000000, 40)
#df = pd.concat([df,df_tmp])
#df_tmp = scraper.scrape_all('kanagawa', 'yk_w', 20000000, 40)
#df = pd.concat([df,df_tmp])
##kawasaki
#df_tmp = scraper.scrape_all('kanagawa', 'kwsk', 20000000, 40)
#df = pd.concat([df,df_tmp])

df.to_csv("nifty_records_all.csv", index=False) 
df.to_excel('test_2.xlsx')  

elapsed_time = time.time() - start_time
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
