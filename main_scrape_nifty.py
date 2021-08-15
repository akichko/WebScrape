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
import scrape_nifty as wsn
import pandas as pd
import time

start_time = time.time()
df = pd.DataFrame()
webaccess = ws.WebAccess_Rq("bs")
scraper = wsn.WebScrapeNifty(webaccess)

#tokyo
df_tmp = scraper.scrape_all('tokyo', 't23_e', 20000000, 40)
df = pd.concat([df,df_tmp])
df_tmp = scraper.scrape_all('tokyo', 't23_s', 20000000, 40)
df = pd.concat([df,df_tmp])
df_tmp = scraper.scrape_all('tokyo', 't23_w', 20000000, 40)
df = pd.concat([df,df_tmp])
df_tmp = scraper.scrape_all('tokyo', 't23_n', 20000000, 40)
df = pd.concat([df,df_tmp])

#ibaraki
df_tmp = scraper.scrape_all('ibaraki', 'mito', 20000000, 40)
df = pd.concat([df,df_tmp])

#yokohama
df_tmp = scraper.scrape_all('kanagawa', 'yk_e', 20000000, 40)
df = pd.concat([df,df_tmp])
df_tmp = scraper.scrape_all('kanagawa', 'yk_n', 20000000, 40)
df = pd.concat([df,df_tmp])
df_tmp = scraper.scrape_all('kanagawa', 'yk_s', 20000000, 40)
df = pd.concat([df,df_tmp])
df_tmp = scraper.scrape_all('kanagawa', 'yk_w', 20000000, 40)
df = pd.concat([df,df_tmp])
#kawasaki
df_tmp = scraper.scrape_all('kanagawa', 'kwsk', 20000000, 40)
df = pd.concat([df,df_tmp])

df.to_csv("nifty_records.csv", index=False) 
df.to_excel('nifty_records.xlsx')  

elapsed_time = time.time() - start_time
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
