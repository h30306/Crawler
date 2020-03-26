#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
import requests
import pandas as pd
import re
import json
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm
import argparse
from multiprocessing.dummy import Pool as ThreadPool


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = cleantext.replace("]","")
    cleantext = cleantext.replace("[","")
    stopWords = ['\n', '\xa0', '\n--', '--', '\r\n\r\n\n--', "\"", '\\n', "'", "\\","xa0"]
    for i in stopWords:
        cleantext = cleantext.replace(i,"")
    return cleantext

url_list=[]

board = 'Boy-Girl'
start_range = 1
end_range = 80

for cid in tqdm(range(int(start_range),int(end_range),20)):
    bbs_result = requests.post('https://disp.cc/b/{}?pn='.format(board)+str(cid))
    soup = BeautifulSoup(bbs_result.text, 'html.parser')
    for i in soup.find_all('span', class_='L34 nowrap listTitle'):
        for url in i('a'):
            url_list.append(url['href'])
error=[]
done = 0


def crawler(pid):
    global done
	#for pid in url_list:
    done+=1
    mode=[]
    c_author=[]
    c_content=[]
    post_url = ('https://disp.cc/b/'+str(pid))
    post_result = requests.get(post_url)
    soup2 = BeautifulSoup(post_result.text, 'html.parser')
    i = soup2.find('div', class_='text_css')
    bar_t = i.find('div', class_='TH_div').text
    article = cleanhtml(str(i.find_all('div', class_='combine-lines')))
    if article == '':
        br=[]
        root = etree.HTML(str(i).replace(u"<br/>",u"<br>"))
        for element in root.iter():
            br.append(element.tail)
        stopWords = [None, '\n', '\xa0', '\n--', '--', '\r\n\r\n\n--']
        br = list(filter(lambda x: x not in stopWords, br))
        article = cleanhtml(str(br[1:]))
    for j in i.find_all('div', class_='push_row'):
        try:
            mode.append(j.find('span', class_='fg137').text[0])
        except:
            mode.append(j.find('span', class_='fg131').text[0])
        author_temp = j.find_all('span', class_='ptt-push-author')[0].text#留言中的作者一
        if c_author == []:#狀況:第一個作者；後面但有換行；後面但沒換行；接著編輯log列
            c_author.append(author_temp)
            c_content.append(cleanhtml(j.find('span', class_='fgY0').text[2:]))
        elif author_temp == c_author[-1]:
            c_content[-1] += cleanhtml(j.find('span', class_='fgY0').text[2:])
        elif len(j.find_all('span', class_='ptt-push-author')) == 1:
            c_author.append(author_temp)
            c_content.append(cleanhtml(j.find('span', class_='fgY0').text[2:]))
        else:
            c_author.append(author_temp)
            c_content_temp = ''
            for x in j.find_all('span', class_='fgY0'):
                c_content_temp += cleanhtml(x.text[2:])
            c_content.append(c_content_temp)
    author_t = bar_t.split('作者\xa0')[1].split('標題\xa0')[0]
    title_t = bar_t.split('作者\xa0')[1].split('標題\xa0')[1].split('時間\xa0')[0]
    time_t = bar_t.split('作者\xa0')[1].split('標題\xa0')[1].split('時間\xa0')[1]

    with open('{}_pool.json'.format(board), 'a', encoding='utf-8') as f:
        json_str = json.dumps({'連結':post_url,
                              '作者':author_t,
                              '標題':title_t,
                              '時間':time_t,
                              '內文':article,
                              '評論模式':mode,
                              '評論作者':c_author,
                              '評論內容':c_content,
                              }, ensure_ascii=False)
        f.write(json_str + '\n')
        f.close()
        
# =============================================================================
# for i in url_list:
#     crawler(i)
# =============================================================================

pool = ThreadPool(8)
pool.map(crawler, url_list)
pool.close()
pool.join()

df = pd.DataFrame({'error': error})
df.to_csv('{}_error_pool'.format(args.board),encoding='utf-8')
