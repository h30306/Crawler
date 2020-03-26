# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import pyodbc
import datetime
##最新 (爬資料庫URL近五天更新留言部分)

##最新 (增加 爬到重覆的 就停止)
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

    
#連接資料庫
conn = DB_CONNECT('PTT_BOARD')
cursor = conn.cursor()

#設存入時間
today = datetime.date.today()
tmp_year = datetime.date.today().year

#設置爬的板
sql = ('SELECT [ID] , [URL] , [POSITIVE_PUSH] , [GENERAL_PUSH] , [NEGATIVE_PUSH] FROM [PTT] WHERE  DATEDIFF (DAY,[PUBLISH_DATE],GETDATE()) <=5  OR DATEDIFF (DAY,[PUBLISH_TIME],GETDATE()) <=5')
result = cursor.execute(sql)
row = cursor.fetchall()


#進入版的INDEX頁面，抓取 最舊頁碼與 IDEX上一頁頁碼 (IDEX頁面無頁數，因此做這個動作)
payload = { 'from':'/bbs/Gossiping/index.html','yes':'yes' }
rs = requests.session()
rs.post('https://www.ptt.cc/ask/over18' , data = payload)

#開始爬版，依照迴圈爬
for  update_item in row  :
    print (update_item[0])
    ptt_id = update_item[0]
    history_url =  update_item[1]
    positive_push =  update_item[2]
    general_push = update_item[3]
    negative_push = update_item[4]
    max_messge_id = update_item[2] + update_item[3] + update_item[4]


    res2 = rs.get(history_url)
    outer_soup2= BeautifulSoup(res2.text, 'html.parser')

    # 第二層內文儲存
    maincontent = outer_soup2.findAll('div', {'id': 'main-content'})

    # 將內文簽名檔後面刪除，計算回文中引述的留言，(包含簽名檔計算)
    try:
        content_span = re.sub('\n--\n\S*<span (.*\n)*', '', maincontent[0].__str__())
    except:
        continue
    premessage = content_span.count('push-tag')

    num=0
    premessage_count=premessage
    for ab in maincontent[0].findAll('div',{'class':'push'}):
        if (premessage_count>0):
            premessage_count = premessage_count-1
            continue
        num = num + 1


    nulldata_num = 0
    for ab in maincontent[0].findAll('div', {'class': 'push'})[premessage:]:
        if (ab.text.strip() == u'檔案過大！部分文章無法顯示'):
            nulldata_num = nulldata_num + 1

    if num == (max_messge_id  + nulldata_num):
        continue

    message_count = max_messge_id
    start_num =max_messge_id
    #num 總數

    for ab in maincontent[0].findAll('div', {'class': 'push'})[premessage:]:
        #留言中出現灰色方格擋住 (格式不對 ，略過)
        if (ab.text.strip() == u'檔案過大！部分文章無法顯示'):
            continue
        if (start_num > 0):
            start_num = start_num - 1
            continue

        push_tag = ab.select('span')[0].text.strip()  # 推
        name = ab.select('span')[1].text.strip()  # 作者
        message = ab.select('span')[2].text.strip()[1:]  # 回文
        messagetime = ab.select('span')[3].text.strip()  # 時間


        if push_tag == u'推':
            positive_push=positive_push+1
            
        if push_tag == u'→':
            general_push = general_push + 1
            
        if push_tag == u'噓':
            negative_push = negative_push + 1
            

        message_date = messagetime[messagetime.find('/')-2:messagetime.find('/')] + '-' + messagetime[messagetime.find('/')+1:messagetime.find('/')+3]
        message_time = messagetime[messagetime.find(':') - 2:messagetime.find(':')] + ':' + messagetime[messagetime.find(':') + 1:messagetime.find(':') + 3]
        message_count = message_count + 1
        

        SQLCommand = "INSERT INTO MESSAGE ( ID, MESSAGE_ID,  NAME, MESSAGE, PUSH_TAG, PUBLISH_DATE, PUBLISH_TIME,W_DATE)  VALUES (?,?,?,?,?,?,?,?)"
        Values = [ptt_id, message_count , name, message, push_tag, message_date, message_time, today]
        cursor.execute(SQLCommand, Values)
        conn.commit()

    SQLCommand = 'UPDATE [PTT] SET [POSITIVE_PUSH] =?  , [GENERAL_PUSH] =? , [NEGATIVE_PUSH] =?  where ID =?'
    Values = [positive_push, general_push, negative_push, ptt_id]
    cursor.execute(SQLCommand, Values)
    conn.commit()
    print ('update')
    print (ptt_id)
print ('END')