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

import pandas as pd
#import matplotlib.pyplot as plt
import seaborn as sns
import re
#import openpyxl


def get_kanri(text):
    if pd.isna(text):
        return None
    m = re.search(r'管理費等：(.+)修繕積立金：(.+)', text)
    return calc_manen(m.group(1)) + calc_manen(m.group(2)) if m else None

def calc_manen(text):
    if pd.isna(text):
        return None
    i10000 = int(m10000.group(1)) if (m10000 := re.search(r'([0-9]+)万', text)) else 0
    i1 = int(m1.group(1)) if (m1 := re.search(r'([0-9]+)円', text)) else 0 
    return i10000 * 10000 + i1

def calc_year(text):
    if pd.isna(text):
        return None
    m = int(m_month.group(1)) if (m_month := re.search(r'([0-9]+)ヶ月', text)) else 0
    y = int(m_year.group(1)) if (m_year := re.search(r'([0-9]+)年', text)) else 0 
    return y + m / 12

def get_floor(text):
    if pd.isna(text):
        return None
    sign = -1 if (m := re.match(r'地下', text)) else 1
    return sign * int(m.group(1)) if (m := re.search(r'([0-9]+)階/', text)) else None

df = pd.read_csv("nifty_records_all.csv")

df['year'] = df['築年月'].map(calc_year)
df['year'] = pd.to_numeric(df['year'])
#df['year'] = df['築年月'].replace(r'([0-9]+)ヶ月','', regex=True).replace('年','', regex=True)
#df['year'] = pd.to_numeric(df['year'])

df['price'] = df['価格'].replace(',','',regex=True).replace(r'([0-9]+)万.+',r'\1', regex=True)
df['price'] = pd.to_numeric(df['price'])

df['m2'] = df['専有面積'].replace(r'([\.0-9]+)(.+)',r'\1', regex=True)
df['m2'] = df['m2'].astype(float, errors = 'raise')

df['kanri'] = df['othercost'].replace(r',','',regex=True).map(get_kanri)
df['kanri'] = pd.to_numeric(df['kanri'])
df.loc[df['kanri'].isna(), 'kanri'] = df['修繕積立金'].replace(r',','',regex=True).map(calc_manen) + df['管理費等'].replace(r',','',regex=True).map(calc_manen)


df['floor'] = df['所在階/階建'].map(get_floor)
if '所在階/構造・階建' in df.columns :
    df.loc[df['floor'].isna(), 'floor'] = df['所在階/構造・階建'].map(get_floor)
    
df['station'] = df['交通'].map(lambda x : match.group(1) if (match := re.search(r'徒歩([0-9]+)分', x)) else None)
df['station'] = pd.to_numeric(df['station'])

#異常値フィルタ
drop_index = df.index[(df['price']>2000) | (df['year']>=40) | (df['kanri']>=60000)]
df = df.drop(drop_index)

df.to_excel('list.xlsx')

sns.set(style='darkgrid')
g = sns.pairplot(data=df[df['year']<=40], vars=['year', 'price', 'm2', 'kanri', 'floor', 'station'], hue='area')
g.fig.set_figheight(10)
g.fig.set_figwidth(15)
g.savefig("ouput.png")

g = sns.pairplot(data=df[df['year']<=40], vars=['year', 'price', 'm2', 'kanri'], hue='area')
g.fig.set_figheight(10)
g.fig.set_figwidth(15)
g.savefig("ouput2.png")
