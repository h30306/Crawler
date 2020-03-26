def Ruten_Spider(url):
    import requests
    import json
    from bs4 import BeautifulSoup
    import pandas as pd
    
    headers = requests.utils.default_headers()
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    img_result=[]
    title_result=[]
    price_result=[]
    for i in range(3):
        res = requests.get(url+'&p='+str(i),headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text,"html.parser")

        #image
        img = soup.find_all('img')
        for i in range(0,30):
            link=img[i].get('src')
            img_result.append(link)
            
        #title
        title = soup.select('h3.item-name.isDefault-name a')
        for s in title:
            title_result.append(s.text)
            
        #price
        price = soup.find_all('rt-ml.inline')
        price = soup.find_all("span", class_="item-direct-price rt-ml-remove")
        for p in range(0,30):
            price_tag=price[p].get('data-price')
            price_result.append(price_tag)
    dictionary = {'image_link' : img_result,
                       'title' : title_result,
                       'price' : price_result}
    df=pd.DataFrame(dictionary)
    result =  df.to_json(orient='index',force_ascii=False)
    return(result)
Ruten_Spider('https://class.ruten.com.tw/user/index00.php?s=vvooxx')
