import webscrape as ws
import time


class WebScrapeBaseball(ws.WebScrape):
    
    def get_record_by_elem(self, body):
        keys = body.cssselect('#tablefix_p thead tr th')
        keys_string = [key.text for key in keys]
        if len(keys_string) == 0:
            return None

        values = body.cssselect('#tablefix_p tbody tr.registerStats')[-1]

        record = {keys[i].text: values[i].text.strip() for i in range(len(keys))}
        name = body.cssselect('#pc_v_name #pc_v_name')
        inning = body.cssselect('#tablefix_p tbody tr.registerStats table.table_inning tbody tr th')

        record['名前'] = name[0].text.strip()
        record['投球回'] = inning[-1].text
        return record
    
    def scrape_all(self, url):
        team_urls = self.get_url_by_url(url,'#team_list a')
        for team_url in team_urls:
            print(team_url)
            player_urls = self.get_url_by_url(team_url, 'td.rosterRegister a')
            for player_url in player_urls:
                print(player_url)
                time.sleep(1)
                record = self.get_record_by_url(player_url)
                self.df = self.df.append(record, ignore_index=True)
        return self.df


wsb = WebScrapeBaseball()
df = wsb.scrape_all('https://npb.jp/bis/teams/')

df.to_csv("player_records.csv", index=False)   