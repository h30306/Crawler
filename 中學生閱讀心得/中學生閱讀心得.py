from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from multiprocessing.dummy import Pool as ThreadPool
import os
import json
from random import randint
import numpy as np

#初始化啟動chrome webdriver
driverpath= "../chromedriver"

date_list = ['1081015','1080315','1071031','1070315','1061031','1060315','1051031','1050315','1041031','1040315','1031031','1030315','1021031','1020315','1011130','1010315','1001031','1000315','9910','990315','9810','9804','9711','9704','9703','9702']
city_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18']
run = [(i,j) for i in date_list for j in city_list]

href = []
sum_number = 0
def crawler_link(data):
    global sum_number
    d= data[0]
    c= data[1]
    #d = '1081015'
    #c = '1'
#    print(data)
    browser=webdriver.Chrome(executable_path=driverpath)
    url="https://www.shs.edu.tw/index.php?p=search"
    browser.get(url)#get方式進入網站
    time.sleep(3)#網站有loading時間
    
    selectCath=Select(browser.find_element_by_id("s_cath"))
    selectCath.select_by_value('1')#選單項目定位
    
    selectcontest=Select(browser.find_element_by_id("s_contest_number"))
    selectcontest.select_by_value(d)#選單項目定位
    
    selectarea=Select(browser.find_element_by_id("s_area"))
    selectarea.select_by_value(c)#選單項目定位
    
    searchBtn=browser.find_element_by_id("search_button")#查詢按鈕定位
    searchBtn.click()#模擬點擊
    browser.implicitly_wait(30)
    if browser.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/h1").text == '作品查詢':
        try:     
            number = int(browser.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/form/table[1]/tbody/tr/td[1]/span[4]").text)
            if number == 0:
                browser.close()
                run.remove(data)
                #print('No Article')
                return print('No Article')
            else:
                sum_number += number
                print(sum_number)
                for a in range(2,int(number)+2):
                    href.append(browser.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/form/table[2]/tbody/tr/td/table/tbody/tr[{}]/td[9]/a".format(a)).get_attribute("href"))
                browser.close()
                run.remove(data)
        except:
            browser.close()
            #print('No number element')
            return print('No number element')
    else:
        return print('網頁又掛了')
    
def crawler_article(data):
    #data = 'https://www.shs.edu.tw/search_view_over.php?work_id=2115306'
    i = data[0]
    urls = data[1]
    text = {}
    browser=webdriver.Chrome(executable_path=driverpath)
    for j,url in enumerate(urls):
        try:
                    
            browser.get(url)
            time.sleep(randint(0, 1))
            text[url] = browser.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/table[7]/tbody/tr[2]/td').text
            print('Success', i, j)
            
        except:
            #browser.close()
            print('Fail', i, j)

        finally:
            pass
    browser.close()
    with open('./data/result_article_'+str(i)+'.json', 'w', encoding='utf-8') as f:
        json.dump(text, f, ensure_ascii=False, indent=2)
            
pool = ThreadPool(11)
pool.map(crawler_link, run)
with open('./data/href.json', 'a', encoding='utf-8') as f:
    json_str = json.dumps({'連結':href}, ensure_ascii=False)
    f.write(json_str + '\n')
    f.close()


f = open("./data./href.json", 'r', encoding='utf-8')
a = [json.loads(line) for line in f]
href = a[0]['連結']
print(len(href))

urls = np.array_split(np.array(href), 3156)
#crawler_article((0, urls[1]))

pool = ThreadPool(11)
pool.map(crawler_article, [(i,v) for i,v in enumerate(urls)])
pool.close()
pool.join()

print('ALL DONE')