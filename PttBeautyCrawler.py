import requests
import time
import datetime
import re, urllib
import os
from bs4 import BeautifulSoup
def get_web_page(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text

blacklist=["[公告] 表特板板規 (2015.2.12)","[公告] 不願上表特 ＆ 優文推薦 ＆ 檢舉建議專區","[公告] 對於謾罵，希望大家將心比心","[公告] 板規修訂 - 意淫文字","[公告] 偷拍相關板規修訂"]

def get_articles(dom, currentdate,dateoffset):
    print("008 get articles start=======")
    soup = BeautifulSoup(dom, 'html.parser')
    offset=datetime.timedelta(days=dateoffset)
    pre_link=None
    articles = []  # 儲存取得的文章資料
    latestdate=currentdate
    divs = soup.find_all('div', 'r-ent')
    datetransfer = re.compile(r'(\d{4})/(\d{1,2})/(\d{2})')
    for d in divs:
        pttdate=str(d.find('div', 'date').string.lstrip())
        spttdate='/'.join([str(currentdate.year),pttdate])
        pttdate = datetime.datetime.strptime(spttdate, "%Y/%m/%d").date()
        mo=datetransfer.search(spttdate)
        if mo:
            spttdate=mo.group(1)+'_'+mo.group(2)+'_'+mo.group(3) #組合日期格式給資料夾檔名使用
        else:
            print("spttdate is abnormal:"+spttdate)

        if  currentdate-pttdate<=offset:  # 發文日期正確
            # 取得推文數
            push_count = 0
            if d.find('div', 'nrec').string:
                try:
                    push_count = int(d.find('div', 'nrec').string)  # 轉換字串為數字
                except ValueError:  # 若轉換失敗，不做任何事，push_count 保持為 0
                    pass

            # 取得文章連結及標題
            if d.find('a'):  # 有超連結，表示文章存在，未被刪除
                href = d.find('a')['href']
                title = d.find('a').string
                if title in blacklist:
                    pass
                else:
                    articles.append({
                        'date':spttdate,
                        'title': title,
                        'href': href,
                        'push_count': push_count
                    })
        else :#日期不在區間內
            if d.find('a'):
                if d.find('a').string in blacklist:
                    print("003"+str(d.find('a').string))
                else:
                    if latestdate>pttdate:
                        print("004 late date str:"+d.find('a').string)
                        latestdate=pttdate
                        print("005 latestdate:"+str(latestdate))
                        print(d.find('a').string)

#   # 接下來的程式碼是要處理上一頁的控制
    weblinks = soup.find_all('a', 'btn wide')
    for weblink in weblinks:
        if weblink.find('a'):
            print("cs:find"+weblink.find('a').string)
        else:
            print("cs:not find")
        if weblink.string == '‹ 上頁':
            pre_link = weblink['href']
    print("009 get articles end=======")
    return articles,pre_link,latestdate


def parse(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    links = soup.find(id='main-content').find_all('a')
    img_urls = []
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
            img_urls.append(link['href'])
    return img_urls

def save(img_urls, title, date):
    if img_urls:
        try:
            dname = date+title.strip()  # 用 strip() 去除字串前後的空白
            print("012:"+dname)
            os.makedirs(dname)
            for img_url in img_urls:
                #print("cs path:"+img_url)
                if img_url.split('//')[1].startswith('m.'):
                    img_url = img_url.replace('//m.', '//i.')
                if not img_url.split('//')[1].startswith('i.'):
                    img_url = img_url.split('//')[0] + '//i.' + img_url.split('//')[1]
                if not img_url.endswith('.jpg'):
                    img_url += '.jpg'
                fname = img_url.split('/')[-1]
                urllib.request.urlretrieve(img_url, os.path.join(dname, fname))
        except Exception as e:
            print(e)


PTT_URL = 'https://www.ptt.cc'


page = get_web_page('https://www.ptt.cc/bbs/Beauty/index.html')
dateoffset = 0
push_count_threshold = 50
if page:
    #date = time.strftime("%m/%d").lstrip('0')  # 今天日期, 去掉開頭的 '0' 以符合 PTT 網站格式
    currentdate= datetime.date.today()
    latestdate = datetime.date.today()

    date = time.strftime("%y/%m/%d")
    print("CS"+str(date))

    while currentdate-datetime.timedelta(days=dateoffset)<=latestdate:
        print("latest date:"+str(latestdate))
        current_articles, pre_link, latestdate = get_articles(page, currentdate, dateoffset)
        print("001 CS latest date:"+str(type(latestdate)))
        if pre_link==None:
            print("011")
            break
        else:
            print("002 :"+str(PTT_URL+pre_link))
            page=get_web_page(PTT_URL+pre_link)
            print("009 pre_link:" + PTT_URL +pre_link)
            for article in current_articles:
                #print("002 CS No:"+str(article['push_count']))

                if article["push_count"] >push_count_threshold:
                    page_data = get_web_page(PTT_URL + article['href'])
                    print(article['title'])
                    if page_data:
                        img_urls = parse(page_data)
                        save(img_urls, article['title'],article['date'])
                        article['num_image'] = len(img_urls)
