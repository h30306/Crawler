# -*- coding: utf-8 -*-

##最新 (增加 爬到重覆的 "那頁爬完"就停止)

#Revised Date: 2018/11/14
#Description:
    #加上 def CONTENT_CLEAN(CONTENT)
    #網址頁碼修正 #for tnum in range(int(page_E)+1,int(page_S)-1,-1):
    #錯誤迴圈刪除 #for nextitem in a:
#Author: Nelly C. Chuang

import requests
from bs4 import BeautifulSoup
import re
import pyodbc
import datetime

############################################################
##########[DB_CONNECT]資料庫連線
############################################################
#def DB_CONNECT(DB):
#    
#    f = open('C:\crawler_code\CRAWLER.txt', 'r')
#    SERVER=f.readline()[6:].strip()
#    UID=f.readline()[4:].strip()
#    PWD=f.readline()[4:].strip()
#    f.close()
#    CONNECT = pyodbc.connect(driver='{SQL Server Native Client 11.0}', server=SERVER,
#                          database=DB, uid=UID, pwd=PWD)
#    return CONNECT

def DB_CONNECT(DB):
    CONNECT = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER=TWA01115864\SQLEXPRESS;DATABASE='+DB+';Trusted_Connection=yes; ')
    return CONNECT 


############################################################
##########[CONTENT_CLEAN]內文清理
############################################################
def CONTENT_CLEAN(CONTENT):
    #將內文前面div部分拿掉，並刪除簽名檔後面
    CONTENT = re.sub('<div.*\n*.*div>', '', CONTENT[0].__str__())
    CONTENT = re.sub('\n--\n\S*(.*\n)*', '', CONTENT) #目前不留簽名檔，--\n\S(.*\n)* 留下簽名檔
    
    #拿掉引述 <span class="f2">※ 引述.*(\n<.span>.*: .*)*\n<.span>
    
    #刪掉文章內所有標籤 remove_span = re.sub('<.*>?', '', content_span)
    CONTENT = re.sub('<span.*?>', '', CONTENT) #顏色前標籤
    CONTENT = re.sub('<.span>', '', CONTENT) #顏色後標籤
    CONTENT = re.sub('<a.*?>', '', CONTENT ) #網址標籤
    CONTENT = re.sub('<.a>', '', CONTENT) #網址後標籤
    CONTENT = re.sub('<.div>', '', CONTENT) #刪除可能的div標籤
    CONTENT = re.sub('\n-----\n.*', '', CONTENT)
    CONTENT = CONTENT.strip()

    CONTENT = re.sub('\r\n','<BR>',CONTENT)
    CONTENT = re.sub('\r','<BR>',CONTENT)
    CONTENT = re.sub('\n','<BR>',CONTENT)

    return CONTENT

#連接資料庫
conn = DB_CONNECT('PTT_BOARD')
cursor = conn.cursor()

#設存入時間
today = datetime.date.today()
tmp_year = datetime.date.today().year

#設置爬的板
website_array = [ 'Stock' , 'CareerPlan' , 'Finance' , 'Salary' , 'Accounting' , 'Hate' ,'Gossiping', 'creditcard' , 'Bank_Service' , 'Tour-Agency' , 'Japan_Travel' , 'Anti-ramp','Car']
#website_array = ['Gossiping']

#進入版的INDEX頁面，抓取 最舊頁碼與 IDEX上一頁頁碼 (IDEX頁面無頁數，因此做這個動作)
payload = { 'from':'/bbs/Gossiping/index.html','yes':'yes' }
rs = requests.session()
rs.post('https://www.ptt.cc/ask/over18' , data = payload)

#開始爬版，依照迴圈爬
for website in website_array :
    first_res = rs.get('https://www.ptt.cc/bbs/'+website+'/index.html')
    fist_outer_soup = BeautifulSoup(first_res.text, 'html.parser')
    div = fist_outer_soup.findAll('div', {'class': 'btn-group btn-group-paging'})
    
    #設置最舊頁碼 #1
    page_S = div[0].select('a')[0].get('href').strip()[div[0].select('a')[0].get('href').find('index') +5: div[0].select('a')[0].get('href').find('.')]
    #設置第二新頁碼
    page_E = div[0].select('a')[1].get('href').strip()[div[0].select('a')[1].get('href').find('index') +5: div[0].select('a')[1].get('href').find('.')]
    print (page_S)
    category_end = 0
    
    for tnum in range(int(page_E)+1,int(page_S)-1,-1):
        print ("頁數: "+str(tnum))
        res = rs.get('https://www.ptt.cc/bbs/'+website+'/index'+str(tnum)+'.html')
        outer_soup = BeautifulSoup(res.text, 'html.parser')
        div = outer_soup.findAll('div', {'class': 'r-ent'})
        
        #檢查排除熱門區塊的熱門文章
        page_span = re.sub('<div class=.r-list-sep.>(.*\n.*)*', '', outer_soup.__str__())
        gerneral_tile_num = page_span.count('r-ent')
        
        for item in div:
            print (gerneral_tile_num)
            #熱門文章不在，不在首頁做存取
            if gerneral_tile_num == 0:
                break
            gerneral_tile_num = gerneral_tile_num - 1
            
            #當有刪除文章的情況，跳過
            if u'刪除)' in item.findAll('div', {'class': 'title'})[0].text or '-' == item('div', {'class': 'author'})[0].text:
                #u'[公告]' in item.findAll('div', {'class': 'title'})[0].text or\
                #u'[公告]' in item.findAll('div', {'class': 'title'})[0].text or\
                continue
            
            a = item.select('a')
            title = a[0].text.strip()
            url = 'https://www.ptt.cc' + a[0].get('href')
            
            mark = item('div', {'class': 'mark'})[0].text.strip()
            date = item('div', {'class': 'date'})[0].text.replace('/','-').strip()
            author = item('div', {'class': 'author'})[0].text.strip().strip()
            #push = item('div', {'class': 'nrec'})[0].text.strip()
            # 正負面
            general_push = 0
            positive_push = 0
            negative_push = 0
            
            res2 = rs.get(url)
            outer_soup2 = BeautifulSoup(res2.text, 'html.parser')
            
            #頁面的TITLE 與 內文的TITLE 只要有@皆會遮蔽，因此只要出現，就抓內文的HTML的標頭
            if (title.find(u'[email protected]') >1):
                title = outer_soup2.select('title')[0].text.strip()
            #第二層內文儲存
            maincontent = outer_soup2.findAll('div', {'id': 'main-content'})
            
            # 抓內文時間儲存，算日期 ，若抓不到 則是404ERROR
            try:
                contentdate = maincontent[0].findAll('span', {'class': 'article-meta-value'})[3].text
            except:
                continue
            try:
                contentdate_year = contentdate[-4:]
                contentdate_month = date[:date.find('-')]
                contentdate_day = date[date.find('-')+1:]
                contentdate_h = contentdate[contentdate.find(':') - 2:contentdate.find(':') ]
                contentdate_m = contentdate[contentdate.find(':')+1:contentdate.find(':') +3]
                contentdate_s = contentdate[contentdate.find(':' )+4:contentdate.find(':') + 6]
                if int(contentdate_year) < 2000:
                    contentdate = datetime.date(int(tmp_year), int(contentdate_month), int(contentdate_day))
                    contentdateime = datetime.datetime(int(tmp_year), int(contentdate_month), int(contentdate_day),int(contentdate_h), int(contentdate_m), int(contentdate_s))
                else:
                    tmp_year = contentdate_year
                    contentdate = datetime.date(int(contentdate_year), int(contentdate_month), int(contentdate_day))
                    contentdateime = datetime.datetime(int(contentdate_year), int(contentdate_month), int(contentdate_day),int(contentdate_h), int(contentdate_m), int(contentdate_s))
            except:
                contentdate_month = date[:date.find('-')]
                contentdate_day = date[date.find('-') + 1:]
                contentdate = datetime.date(int(tmp_year), int(contentdate_month), int(contentdate_day))
                contentdateime = 'NULL'
            # 將內文簽名檔後面刪除，計算回文中引述的留言，(包含簽名檔計算)
            content_span = re.sub('\n--\n\S*<span (.*\n)*', '', maincontent[0].__str__())
            premessage = content_span.count('push-tag')
            
            content = CONTENT_CLEAN(maincontent) #內文清理
            
            num = 0
            premessage_count = premessage
            for ab in maincontent[0].findAll('div',{'class':'push'}):
                 if (premessage_count>0):
                     premessage_count = premessage_count-1
                     continue
                 num = num + 1
                 
            try:
                if contentdateime == 'NULL' :
                    SQLCommand = 'INSERT INTO PTT ( TITLE, CONTENT, PUBLISH_DATE, PUBLISH_TIME, CATEGORY, AUTHOR, URL, MARK, W_DATE, POSITIVE_PUSH, GENERAL_PUSH, NEGATIVE_PUSH) VALUES (?,?,?,NULL,?,?,?,?,?,0,0,0)'
                    Values = [title, content, contentdate, website, author, url, mark, today]
                    cursor.execute(SQLCommand, Values)
                    conn.commit()
                else:
                    SQLCommand = 'INSERT INTO PTT ( TITLE, CONTENT, PUBLISH_DATE, PUBLISH_TIME, CATEGORY, AUTHOR, URL, MARK, W_DATE, POSITIVE_PUSH, GENERAL_PUSH, NEGATIVE_PUSH) VALUES (?,?,?,?,?,?,?,?,?,0,0,0)'
                    Values = [title, content, contentdate, contentdateime, website, author, url, mark, today]
                    cursor.execute(SQLCommand, Values)
                    conn.commit()
            except pyodbc.IntegrityError:
                category_end = category_end+1
                continue
            
            message_count = 0
            SQLCommand = ('SELECT ID FROM PTT WHERE URL=? AND AUTHOR=? AND PUBLISH_DATE=?')
            Values = (url, author, contentdate)
            result = cursor.execute(SQLCommand, Values)
            row = cursor.fetchone()
            
            for ab in maincontent[0].findAll('div', {'class': 'push'})[premessage:]:
                #留言中出現灰色方格擋住 (格式不對 ，略過)
                if (ab.text.strip() == u'檔案過大！部分文章無法顯示'):
                    continue
                push_tag = ab.select('span')[0].text.strip() #推
                name = ab.select('span')[1].text.strip() #作者
                message = ab.select('span')[2].text.strip()[1:] #回文
                messagetime = ab.select('span')[3].text.strip() #時間
                
                if push_tag == u'推':
                    positive_push = positive_push+1

                if push_tag == u'→':
                    general_push = general_push + 1

                if push_tag == u'噓':
                    negative_push = negative_push + 1
                    
                message_date = messagetime[messagetime.find('/')-2:messagetime.find('/')] + '-' + messagetime[messagetime.find('/')+1:messagetime.find('/')+3]
                message_time = messagetime[messagetime.find(':') - 2:messagetime.find(':')] + ':' + messagetime[messagetime.find(':') + 1:messagetime.find(':') + 3]
                message_count = message_count + 1
                
                SQLCommand = "INSERT INTO MESSAGE ( ID, MESSAGE_ID, NAME, MESSAGE, PUSH_TAG, PUBLISH_DATE, PUBLISH_TIME, W_DATE) VALUES (?,?,?,?,?,?,?,?)"
                Values = [str(row[0]), message_count , name, message, push_tag, message_date, message_time, today]
                cursor.execute(SQLCommand, Values)
                conn.commit()
                
            SQLCommand = 'UPDATE [PTT] SET [POSITIVE_PUSH]=? , [GENERAL_PUSH]=? , [NEGATIVE_PUSH]=? where ID=?'
            Values = [positive_push, general_push, negative_push, str(row[0])]
            cursor.execute(SQLCommand, Values)
            conn.commit()
            
            print (website)
            
        if category_end >= 1:
            break
    print ('change BOARD')