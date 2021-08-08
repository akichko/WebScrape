import webscrape as ws
#from abc import ABCMeta, abstractmethod
#import requests
import lxml.html
import time
#import pandas as pd


class WebScrapeNifty(ws.WebScrape):    
    def __init__(self):
        super().__init__()
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        self.headers = {'User-Agent': ua}
  
    def get_page_list(self, element):
        nayoses = element.cssselect(".nayose")
        for nayose in nayoses:
            print(nayose.get('data-name'))
            links = nayose.cssselect(".nayose_head p a")
    #        for link in links:
    #            yield link.get('href')
            if len(links) > 0:
    #            print(links[0].get('href'))
                yield links[0].get('href')

    def get_record_by_elem(self, element):
        keys = element.cssselect('#detailInfoTable tr th')
        if len(keys) == 0:
            return None
        values = element.cssselect('#detailInfoTable tr td')
        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}
        if len(element.cssselect('.titleMain .name')) > 0:
            record['名前'] = element.cssselect('.titleMain .name')[0].text
        if len(element.cssselect('.otherPrice')) > 0:
            record['管理費等'] = element.cssselect('.otherPrice')[0].text
        return record

    def get_df_by_url(self, url):
        response = self.session.get(url, headers=self.headers)
        body = lxml.html.fromstring(response.content)
        body.make_links_absolute(response.url)
        return self.get_record_by_elem(body)

    def get_next_page_url(self, element):
        links = element.cssselect(".marginTop0 .pageNation li.mg3 a")
        if len(links) == 0:
            return None
        if links[-1].text != "次へ>":
            return None
        link_url = links[-1].get('href')
        #print(link_url)
        return link_url


    def scrape_all(self, url):
        response = self.session.get(url, headers=self.headers)
        body = lxml.html.fromstring(response.content)
        body.make_links_absolute(response.url)
        while True:
            nayose_urls = self.get_page_list(body)
            for nayose_url in nayose_urls:
                print(nayose_url)
                record = self.get_record_by_url(nayose_url)
                self.df = self.df.append(record, ignore_index=True)
            next_page_url = self.get_next_page_url(body)
            if next_page_url == None:
                print("end")
                break
            time.sleep(1)
            print(next_page_url)
            response = self.session.get(next_page_url, headers=self.headers)
            body = lxml.html.fromstring(response.content)
            body.make_links_absolute(response.url)
        return self.df


wsn = WebScrapeNifty()
#wsn.set_header()
df = wsn.scrape_all('https://myhome.nifty.com/chuko/mansion/kanto/tokyo/?cities=shinjukuku,toshimaku,itabashiku&subtype=buc,buh&b2=15000000&b10=20&b6=15')

df.to_csv("nifty_records.csv", index=False)   
