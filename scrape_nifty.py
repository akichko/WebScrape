import webscrape2 as ws
import re
import pandas as pd


class WebScrapeNifty(ws.WebScrape):    
    def __init__(self):
        super().__init__()
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        self.headers = {'User-Agent': ua}
  
    def __scrape_list_page(self, element):
        nayoses = element.cssselect(".nayose")
        for nayose in nayoses:
            nayose_url = self.__get_nayose_url(nayose)
            print(nayose.get('data-name'))
            print(nayose_url)

            record = self.__get_simple_record(nayose)
            #ページ種別で解析切替
            detail_record = self.get_record_by_url(nayose_url)
            if detail_record != None:
                record.update(detail_record)
                
            self.df = self.df.append(record, ignore_index=True)
            record['url'] = nayose_url

    
    def __get_nayose_url(self, nayose):
        links = nayose.cssselect(".nayose_head p a")
        #for link in links:
            #   yield link.get('href')
        if len(links) > 0:
            #  print(links[0].get('href'))
            return links[0].get('href')

    def __get_sub_page_list(self, element):
        nayoses = element.cssselect(".nayose")
        for nayose in nayoses:
            print(nayose.get('data-name'))
            yield self.__get_nayose_url(nayose)

            #links = nayose.cssselect(".nayose_head p a")
            #if len(links) > 0:
            #    yield links[0].get('href')

    def get_record_by_elem(self, element): #element:detail page
        keys = element.cssselect('#detailInfoTable tr th')
        if len(keys) == 0:
            return None
        values = element.cssselect('#detailInfoTable tr td')
        values = [x.text if x.text is not None else '' for x in values]
        record = {keys[i].text: values[i].strip() for i in range(len(keys))}
        if len(element.cssselect('.titleMain .name')) > 0:
            record['名前'] = element.cssselect('.titleMain .name')[0].text
        if len(element.cssselect('.otherPrice')) > 0:
            record['管理費等'] = element.cssselect('.otherPrice')[0].text
        return record

    def __get_simple_record(self, nayose):
        keys = nayose.cssselect(".itemContent dt")
        values = nayose.cssselect(".itemContent dd")
        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}
        return record
       

    def __get_next_list_page_url(self, element): #override
        links = element.cssselect(".marginTop0 .pageNation li.mg3 a")
        if len(links) == 0:
            return None
        if links[-1].text != "次へ>":
            return None
        link_url = links[-1].get('href')
        #print(link_url)
        return link_url


    def scrape_all(self, url): #override
        body = self.get_element(url)

        self.paging_exe(body, self.__scrape_list_page, self.__get_next_list_page_url)

        print("end")
        return self.df


kanto = {}
west = ['nerimaku','setagayaku','shinjukuku','nakanoku','suginamiku','shibuyaku']
north = ['itabashiku','toshimaku','bunkyoku','adachiku','kitaku','arakawaku']
east = ['katsushikaku','edogawaku','taitoku','kotoku','sumidaku','chuoku']
south = ['minatoku','shinagawaku','otaku','meguroku','chiyodaku']
kanto['tokyo'] = {'e':east, 'w':west, 's':south, 'n':north}
kanto['tokyo']


def make_url(prefecture, area, max_price):
    #&subtype=buc //中古マンション
    #buh& //中古一戸建て
    #b2=15000000 //価格上限（b1=下限）
    #&b10=20 //建物面積(m2)
    #&b6=15 //駅からの距離
    #max_price = 15000000
    url = "https://myhome.nifty.com/chuko/mansion/kanto/" \
        + prefecture \
        + "/?cities=" + re.sub("[\[\]\'\ ]","", str(kanto[prefecture][area])) \
        + "&subtype=buc" \
        + "&b2=" + str(max_price) \
        + "&b10=20&b6=15"
    return url

wsn = WebScrapeNifty()
#url = make_url('tokyo', 'w')

df_e = wsn.scrape_all(make_url('tokyo', 'e', 20000000))
df_e['area'] = 'east'
df_s = wsn.scrape_all(make_url('tokyo', 's', 20000000))
df_s['area'] = 'south'
df = pd.concat([df_e,df_s])

#df = pd.concat([df_w,df_e,df_n,df_s])
df.to_csv("nifty_records_tokyo.csv", index=False)   

