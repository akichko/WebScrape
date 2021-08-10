import webscrapeBs as ws
import re
import pandas as pd


class WebScrapeNiftyBs(ws.WebScrapeBs):    
    def __init__(self):
        super().__init__()
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        self.headers = {'User-Agent': ua}
  

    def __scrape_list_page(self, element):
        nayoses = element.select(".nayose")
        for nayose in nayoses:
            #pass
            self.__get_record_by_nayose(nayose)            

    def __get_next_list_page_url(self, element): #override
        elems = element.select(".pageNation li.mg3 a")
        for a in elems:
            if a.text == "次へ>":
                return a.get('href')
        #if len(links) == 0:
        #    return None
        #if links[-1].text != "次へ>":
        #    return None
        #link_url = links[-1].get('href')
        ##print(link_url)
        #return link_url


    def __get_record_by_nayose(self, nayose):
        
        nayose_url = self.__get_nayose_url(nayose)
        print(nayose.get('data-name'))
        print(nayose_url)

        record = self.__get_simple_record(nayose)
        elem_nayose_page = self.get_element_by_url(nayose_url)

        #ページ種別で解析切替
        elem_link = nayose.select_one(".shinchiku_manshion .data .company")
        if elem_link.select('.athomef'):
            detail_record = self.__get_record_by_detail_page_2(elem_nayose_page)
            print('at home')
        elif elem_link.select('.yahoof'):
            detail_record = self.__get_record_by_detail_page(elem_nayose_page)
            print('yahoo')
        else:
            detail_record = self.__get_record_by_detail_page(elem_nayose_page)
            print('other')
            pass

        if detail_record != None:
            detail_record.update(record)
            record = detail_record
            
        record['url'] = nayose_url
        record['cate'] = nayose.select_one("span.cate").text

        record['pref'] = self.pref
        record['area'] = self.area
        self.df = self.df.append(record, ignore_index=True)
    
    def __get_nayose_url(self, nayose):
        a = nayose.select_one(".nayose_head > p > a")
        return a.get('href')

    def __get_simple_record(self, nayose):
        keys = nayose.select(".itemContent dt")
        values = nayose.select(".itemContent dd")
        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}
        return record

    def __get_record_by_detail_page(self, element): #element:detail page
        keys = element.select('#detailInfoTable tr th')
        if len(keys) == 0:
            return None
        values = element.select('#detailInfoTable tr td')
        #values = [x.text if x.text is not None else '' for x in values]
        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}
        if len(element.select('.titleMain .name')) > 0:
            record['name'] = element.select('.titleMain .name')[0].text
        if len(element.select('.otherPrice')) > 0:
            record['othercost'] = element.select('.otherPrice')[0].text
        record['site'] = 'nifty'
        return record

    def __get_record_by_detail_page_2(self, element): #element:detail page
        #別ページ
        elem_iframe = element.select_one('iframe#itemDetailFrame')
        athome_url = elem_iframe.get('src')
        elem_athome_page = self.get_element_by_url(athome_url)

        keys = elem_athome_page.select('.wrapLeftnoMap tr th')
        if len(keys) == 0:
            return None
        values = elem_athome_page.select('.wrapLeftnoMap tr td')
        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}

        record['name'] = record['建物名・部屋番号']
        record['site'] = 'at home'

        return record


    def scrape_all(self, url): #override
        print("start")
        self.clear_df()
        print(url)

        body = self.get_element_by_url(url)

        self.paging_exe(body, self.__scrape_list_page, self.__get_next_list_page_url)

        print("end")
        return self.df


class Controller:

    kanto = {}
    west = ['nerimaku','setagayaku','shinjukuku','nakanoku','suginamiku','shibuyaku']
    north = ['itabashiku','toshimaku','bunkyoku','adachiku','kitaku','arakawaku']
    east = ['katsushikaku','edogawaku','taitoku','kotoku','sumidaku','chuoku']
    south = ['minatoku','shinagawaku','otaku','meguroku','chiyodaku']
    kanto['tokyo'] = {'e':east, 'w':west, 's':south, 'n':north}

    mito = ['mitoshi','hitachinakashi']
    kanto['ibaraki'] = {'mito':mito}

    north = ['yokohamashitsurumiku','yokohamashikanagawaku','yokohamashinishiku', \
            'yokohamashinakaku','yokohamashiminamiku','yokohamashihodogayaku', \
            'yokohamashikohokuku','yokohamashiaobaku','yokohamashitsuzukiku']
    south = ['yokohamashiisogoku','yokohamashikanazawaku','yokohamashitotsukaku', \
            'yokohamashikonanku','yokohamashiasahiku','yokohamashimidoriku', \
            'yokohamashiseyaku','yokohamashisakaeku','yokohamashiizumiku']
    kanto['kanagawa'] = {'n':north, 's':south}



    def __init__(self):
        self.wsn = WebScrapeNiftyBs()

    def make_url(self, prefecture, area, max_price):
        #&subtype=buc //中古マンション
        #buh& //中古一戸建て
        #b2=15000000 //価格上限（b1=下限）
        #&b10=20 //建物面積(m2)
        #&b6=15 //駅からの距離
        #max_price = 15000000
        url = "https://myhome.nifty.com/chuko/mansion/kanto/" \
            + prefecture \
            + "/?cities=" + re.sub("[\[\]\'\ ]","", str(self.kanto[prefecture][area])) \
            + "&subtype=buc" \
            + "&b2=" + str(max_price) \
            + "&b10=20&b6=15"
        return url

    def start_scraping(self, pref, area, max_price = 20000000):
        self.wsn.pref = pref
        self.wsn.area = area
        url = self.make_url(pref, area, max_price)
        return self.wsn.scrape_all(url)


#Main
controller = Controller()
df = pd.DataFrame()

#tokyo
#df_tmp = controller.start_scraping('tokyo', 'e', 20000000)
#df = pd.concat([df,df_tmp])
#df_tmp = controller.start_scraping('tokyo', 's', 20000000)
#df = pd.concat([df,df_tmp])
#df_tmp = controller.start_scraping('tokyo', 'w', 20000000)
#df = pd.concat([df,df_tmp])
#df_tmp = controller.start_scraping('tokyo', 'n', 20000000)
#df = pd.concat([df,df_tmp])

#df = pd.concat([df_w,df_e,df_n,df_s])

#df.to_csv("nifty_records_tokyo.csv", index=False)   

#ibaraki
df_tmp = controller.start_scraping('ibaraki', 'mito', 20000000)
df = pd.concat([df,df_tmp])
#df.to_csv("nifty_records_ibaraki.csv", index=False)   

#yokohama
#df_tmp = controller.start_scraping('kanagawa', 's', 20000000)
#df = pd.concat([df,df_tmp])
#df_tmp = controller.start_scraping('kanagawa', 'n', 20000000)
#df = pd.concat([df,df_tmp])
#df.to_csv("nifty_records_yokohama.csv", index=False)   

df.to_csv("nifty_records_all.csv", index=False)   
