#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import requests
import ast
import pandas as pd
import time
import re
import json
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm



bbs_url = 'https://disp.cc/b/HatePolitics'

url_list=[]
for cid in tqdm(range(1,65315,20)):
# for cid in tqdm(range(1,42,20)):
    bbs_result = requests.post('https://disp.cc/b/HatePolitics?pn='+str(cid))
    soup = BeautifulSoup(bbs_result.text, 'html.parser')
    for i in soup.find_all('span', class_='L34 nowrap listTitle'):
        for url in i('a'):
            url_list.append(url['href'])

#f.write(','.join(['作者','標題','時間','評論模式','評論作者','評論內容', '內文']) + '\n')


author=[]
title=[]
time=[]
modes=[]
c_authors=[]
c_contents=[]
content=[]
error=[]

for pid in tqdm(url_list):
    mode=[]
    c_author=[]
    c_content=[]
    br=[]
    try:

        post_url = ('https://disp.cc/b/'+str(pid))
        post_result = requests.get(post_url)
        soup2 = BeautifulSoup(post_result.text, 'html.parser')

        i = soup2.find('div', class_='text_css')
        bar = i.find('div', class_='TH_div')
        bar_t = bar.text
        # cols = re.findall(r'作者\s(?P<author>.*)標題\s(?P<title>.*)時間\s(?P<time>.*)', bar.text)
        
        con = str(i)
        #con = unicode(con, errors='replace')
        con = con.replace(u"<br/>",u"<br>")
        root = etree.HTML(con)
        for element in root.iter():
            br.append(element.tail)
        stopWords = [None, '\n', '\xa0', '\n--', '--', '\r\n\r\n\n--']
        br = list(filter(lambda x: x not in stopWords, br))
    

        try:
            for j in i.find_all('div', class_='push_row'):
                
                try:
                    mode.append(j.find('span', class_='fg137').text[0])
                except:
                    mode.append(j.find('span', class_='fg131').text[0])
                c_author.append(j.find('span', class_='fg133').text)
                c_content.append(j.find('span', class_='fgY0').text)
        except:
            pass
    except:
         print('1',pid)
         error.append(pid)
    try:
        author_t = bar_t.split('作者\xa0')[1].split('標題\xa0')[0]
        title_t = bar_t.split('作者\xa0')[1].split('標題\xa0')[1].split('時間\xa0')[0]
        time_t = bar_t.split('作者\xa0')[1].split('標題\xa0')[1].split('時間\xa0')[1]   

        #author.append(author_t)
        #title.append(title_t)
        #time.append(time_t)
        #content.append(list(br))
        #modes.append(mode)
        #c_authors.append(c_author)
        #c_contents.append(c_content)

    except:
        print('2',pid)
        error.append(pid)
    finally:
        with open('HatePolitics.json', 'a', encoding='utf-8') as f:
            json_str = json.dumps({'作者':author_t, 
                                  '標題':title_t, 
                                  '時間':time_t, 
                                  '評論模式':mode, 
                                  '評論作者':c_author, 
                                  '評論內容':c_content,
                                  '內文':list(br)}, ensure_ascii=False)
            f.write(json_str + '\n')
            f.close()

#final =list(zip(author, title, time, modes, c_authors, c_contents, content))
#final_df = pd.DataFrame(final,columns=['作者','標題','時間','評論模式','評論作者','評論內容', '內文'])


#final_df.to_csv('HatePolitics.csv', index=False, encoding='utf-8')


error_df = pd.DataFrame(error)
error_df.to_csv('error.csv', index=False, encoding='utf-8')

