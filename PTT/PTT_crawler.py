
#coding=utf-8

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--b', type=str, default='NBA', help='board_name')
parser.add_argument('--ps', type=int, default='1', help='page_start')
parser.add_argument('--pe', type=int, default='2', help='page_end')
args = parser.parse_args()

author, title, time, content, content_author, comment = [], [], [], [], [], []
for n in tqdm(range(args.ps,args.pe,1)):
    print(n)
    res = requests.get("https://www.ptt.cc/bbs/"+args.b+"/index"+str(n)+".html")
    soup = BeautifulSoup(res.text)
    for i in soup.select(".title"):
        try:    
            if i('a') == []:
                continue
            else:
                res2 = requests.get("https://www.ptt.cc"+i('a')[0]['href'])
                soup2 = BeautifulSoup(res2.text)
            
                author_text = soup2.select(".article-meta-value")[0].text
                title_text = soup2.select(".article-meta-value")[2].text
                time_text = soup2.select(".article-meta-value")[3].text
                content_text = soup2.select("#main-content")[0].text.split(u"※")[0].split(time_text)[1]
                
                author.append(author_text)
                title.append(title_text)
                time.append(time_text)
                content.append(content_text)         
                lst = []
                for m in soup2.select(".push .f3.push-content")[0:]:
                    lst.append(m.text)
                comment.append(lst)
                lst_ = []
                for z in soup2.select(".push .f3.hl.push-userid")[0:]:
                    lst_.append(z.text.strip())
                content_author.append(lst_)

        except IndexError:
            print("出錯喔")


assert len(author) == len(title) == len(time) == len(content)

ptt = list(zip(title, time, author, content, content_author, comment))

df = pd.DataFrame(ptt, columns=['標題', '時間', '作者', '內文', '留言作者','留言'])

df.to_csv('{}_crawler.csv'.format(args.b), encoding='utf-8')

