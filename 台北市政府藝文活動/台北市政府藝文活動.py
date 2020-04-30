from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from multiprocessing.dummy import Pool as ThreadPool
import os
import json
import numpy as np
from math import ceil
import pandas as pd
os.listdir()

driverpath= "../chromedriver"

start_date = '20191001'
end_date = '20191231'
region = 'A63'#台北市

href = []
len(href)

def crawler_link(start_date, end_date, region):
    driver=webdriver.Chrome(executable_path=driverpath)
    url="https://event.moc.gov.tw/sp.asp?xdurl=HySearchG22016/SearchResult.asp&ctNode=676&mp=1"
    #每個類別分開爬
    for i in range(2,12):
        driver.get(url)#get方式進入網站
        time.sleep(3)#網站有loading時間
        
        #活動開始日期
        selectStartDate=driver.find_element_by_id("ev_start")
        selectStartDate.send_keys(start_date)
        
        #活動結束日期
        selectStartDate=driver.find_element_by_id("ev_end")
        selectStartDate.send_keys(end_date)
        
        #選擇縣市
        selectCity=Select(driver.find_element_by_name("ev_city"))
        selectCity.select_by_value(region)
    

        searchBtn=driver.find_element_by_xpath("/html/body/div[1]/div[1]/section[2]/form/table/tbody/tr[5]/td/div/label[{}]".format(i))#查詢按鈕定位
        searchBtn.click()#模擬點擊
        
        #滑到最底部
        js="var q=document.documentElement.scrollTop=100000"  
        driver.execute_script(js)
        
        #開始查詢
        searchBtn=driver.find_element_by_name("Search")#查詢按鈕定位
        searchBtn.click()#模擬點擊
        
        page = ceil(int(driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[3]/section[1]/p/em[1]").text)/10)
        print(page)
        for p in range(1,page):
            for i in range(2,12):
                try:
                    href_temp = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[3]/section[2]/table/tbody/tr[{}]/td[3]/a".format(i))
                    href_temp = href_temp.get_attribute("href")
                    href.append(href_temp)
                except:
                    print('沒文章')
                
            #爬完拉到最下面
            driver.execute_script(js)
            
            #點擊下一頁
            try:
                nextPagehBtn=driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[3]/section[1]/ul[1]/li/a[@title="下一頁"]')
                nextPagehBtn.click()
                time.sleep(2)#網站有loading時間
            except:
                print("點不到下一頁")

error = []
df = pd.DataFrame({'title':[],'place':[],'address':[],'time':[],'activityType':[],'activityClass':[],'ticketPrice':[]})
def crawler_article(urls):
    global df
    driver=webdriver.Chrome(executable_path=driverpath)
    for i in urls:
        url=i
        driver.get(url)
        try:
            title = driver.find_element_by_xpath('/html/body/div[1]/div[1]/section[3]/table/tbody/tr/th[text()="活動名稱"]/../td').text
            place = driver.find_element_by_xpath('/html/body/div[1]/div[1]/section[3]/table/tbody/tr/th[text()="所在縣市"]/../td').text
            address = driver.find_element_by_xpath('/html/body/div[1]/div[1]/section[3]/table/tbody/tr/th[text()="場地地址"]/../td').text
            time = driver.find_element_by_xpath('/html/body/div[1]/div[1]/section[3]/table/tbody/tr/th[text()="活動時間"]/../td').text
            activityType = driver.find_element_by_xpath('/html/body/div[1]/div[1]/section[3]/table/tbody/tr/th[text()="活動型態"]/../td').text
            activityClass = driver.find_element_by_xpath('/html/body/div[1]/div[1]/section[3]/table/tbody/tr/th[text()="活動類別"]/../td').text
            ticketPrice = driver.find_element_by_xpath('/html/body/div[1]/div[1]/section[3]/table/tbody/tr/th[text()="票價"]/../td').text
            
            df = df.append(pd.Series({'title':title,'place':place,'address':address,'time':time,'activityType':activityType,'activityClass':activityClass,'ticketPrice':ticketPrice}), ignore_index=True)
        except:
            print('有問題')
            error.append(i)
            continue



crawler_link(start_date, end_date, region)
urls = np.array_split(np.array(href), 5)
pool = ThreadPool(5)
pool.map(crawler_article, urls)
pool.close()
pool.join()

#輸出link
with open('./data/href.json', 'a', encoding='utf-8') as f:
    json_str = json.dumps({'連結':href}, ensure_ascii=False)
    f.write(json_str + '\n')
    f.close()

#輸出
df.to_csv('./data/activity.csv', encoding='utf-8')
