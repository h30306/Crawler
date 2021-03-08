#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from multiprocessing.dummy import Pool as ThreadPool
from selenium.webdriver.chrome.options import Options
import json
import time
from tqdm import tqdm
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument('--disable-gpu')


# In[ ]:


#初始化啟動chrome webdriver
driverpath= "../Driver/chromedriver88OS"


# In[ ]:


#Read Legislator List
df = pd.read_csv('./data/demo_data/立委名單.txt', sep='/n', encoding='utf-8')
legislator = list(set(list(df['立委姓名'])))


# In[ ]:


browser=webdriver.Chrome(executable_path=driverpath)
browser.implicitly_wait(30)


# In[ ]:


link = {}
for i,name in enumerate(legislator):
    l=[]
    for page in range(500):
        url="https://www.setn.com/search.aspx?q={}&r=0&p={}".format(name, page)
        browser.get(url)
        css = browser.find_element_by_css_selector("div.col-md-9.col-sm-12.contLeft")
        gt = css.find_elements_by_class_name('gt')
        l_temp=[]
        for element in gt:
            l_temp.append(element.get_attribute('href'))
        l_temp = l_temp[0::2]
        if len(l_temp)!=36:
            link[name]=list(set(l))
            print(len(link[name]))
            break
        else:
            l.extend(l_temp)


# In[ ]:


with open('./data/link.json', 'w') as f:
    json.dump(link, f)


# In[2]:


with open('./data/link.json', 'r') as f:
    link = json.load(f)


# In[3]:


def crawler_article(data):
    name = data[0]
    urls = data[1]
    
    if (urls!=[]) & (name  not in [i.split('.')[0] for i in os.listdir('./data')]):
        
        print("Start crawler news of {}".format(name))

        Title = []
        Time = []
        Category = []
        Hashtag = []
        Content = []
        Link = []
        Error_list = []
        
        print('Number of news of {}:'.format(name), len(urls))
        for url in urls:
            #print("Browser Get Success")
            resp = requests.get(url)
            if resp.status_code != 200:
                Error_list.append(url)
            else:
                try:
                    soup = BeautifulSoup(resp.text, 'lxml')

                    #Crawler Title
                    #print('Crawler Title')
                    title = soup.find('h1', 'news-title-3').string.strip()

                    #Crawler Time
                    #print('Crawler Time')
                    time = soup.find('time', 'page-date').string.strip()

                    #Crawler Category
                    #print('Crawler Category')
                    category = soup.find('meta', property="article:section").get('content')

                    #Crawler Hashtag
                    #print("Crawler Hashtag")
                    hashtag = soup.find('meta', itemprop="keywords").get('content')
                    hashtag = "#"+"#".join(hashtag.split(','))

                    #Crawler Content
                    #print("Crawler Content")
                    C1 = soup.find_all('p')
                    content=''
                    for p in C1:
                        if "▲" in p.text or p.text == '':
                            continue
                        else:
                            content+=p.text.strip()+'\n'
                except:
                    print(url)
                        
                if content.replace('\n', '') == '':
                    continue

                Title.append(title)
                Time.append(time)
                Category.append(category)
                Hashtag.append(hashtag)
                Content.append(content)
                Link.append(url)

        print("{} Crawler Done!".format(name))

        df = pd.DataFrame({"TITLE":Title, "政治野心": np.nan, "TIME":Time, "CATEGORY":Category, "HASHTAG":Hashtag, "Content":Content, "SOURCE":['三立新聞網']*len(Title), "LINK":Link})

        print('Save {} as XLSX'.format(name))
        df.to_excel("./data/{}.SETN.xlsx".format(name), encoding='utf-8-sig', index=False)
        return name, Error_list


# In[4]:


error_website={}


# In[5]:


run = [(name, link[name]) for name in link]


# In[6]:


pool = ThreadPool(4)
try:
    name, Error_list = pool.map(crawler_article, run)
    error_website[name] = Error_list
except:
    pass
pool.close()
pool.join()


# In[ ]:




