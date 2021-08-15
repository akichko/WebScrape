import webscrape as ws
#import re
import pandas as pd
import time

class WebScrapeBaseball(ws.WebScrape3):
 
    def scrape_all(self, url):
        print("start")
        print(url)

        df = self.exe_scraping(url)

        print("end")
        return df

    def get_scraper(self, elem) -> ws.Scraper: #override
        return Scraper_TopPage(elem, self.webaccess)


class Scraper_TopPage(ws.Scraper):

    def get_sub_scrapers(self): #override
        team_urls = self.elem.css_select("#team_list a")
        for team_url in team_urls:
            print(team_url.get_attr_value('href'))
            elem_team = self.webaccess.get_element_by_url(team_url.get_attr_value('href'))
            yield Scraper_TeamPage(elem_team, self.webaccess)


class Scraper_TeamPage(ws.Scraper):

    def get_sub_scrapers(self): #override
        player_urls = self.elem.css_select("td.rosterRegister a")
        for player_url in player_urls:
            print(player_url.get_attr_value('href'))
            elem_player = self.webaccess.get_element_by_url(player_url.get_attr_value('href'))
            yield Scraper_PlayerPage(elem_player, self.webaccess)


class Scraper_PlayerPage(ws.Scraper):

    def update_df(self):
        keys = self.elem.css_select('#tablefix_p thead tr th')
        keys_string = [key.text for key in keys]
        if len(keys_string) == 0:
            return None
        values = self.elem.css_select('#tablefix_p tbody tr.registerStats')[-1].css_select('td')

        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}
        name = self.elem.css_select('#pc_v_name #pc_v_name')
        inning = self.elem.css_select('#tablefix_p tbody tr.registerStats table.table_inning tbody tr th')

        record['名前'] = name[0].text.strip()
        record['投球回'] = inning[-1].text
        
        self.df = pd.DataFrame(record, index=[0])


# Main #################################################################

start_time = time.time()
#df = pd.DataFrame()
webaccess = ws.WebAccess_Rq("bs")
scraper = WebScrapeBaseball(webaccess)

#kawasaki
df = scraper.scrape_all('https://npb.jp/bis/teams/')

df.to_csv("player_records_2.csv", index=False)  

elapsed_time = time.time() - start_time
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
