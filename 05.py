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

#<a class="btn wide" href="/bbs/Beauty/index2446.html">‹ 上頁</a>

def get_articles(dom, date):
    soup = BeautifulSoup(dom, 'html.parser')

    articles = []  # 儲存取得的文章資料
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        date1=date
        date2=str(d.find('div', 'date').string.lstrip())
        date3= datetime.datetime.strptime(date2,"%m/%d")
        print("date3:"+str(date3))

        #if d.find('div', 'date').string == date:  # 發文日期正確
        if date1 == date2.lstrip():  # 發文日期正確
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
                articles.append({
                    'title': title,
                    'href': href,
                    'push_count': push_count
                })
    weblinks = soup.find_all('a', 'btn wide')
    #print(weblinks.pree)
    for weblink in weblinks:
       # print("CS:"+weblink.find('div','btn wide').string)
        print(weblink.prettify())
        print("cs1:"+str(weblink.find('a')))
        print("cs2:" + str(type(weblink.find('a'))))
        print("cs3:" + str(type(weblink)))
        print("cs4:" + str(weblink.string))
        #if weblink.find('a',"btn wide"):
        if weblink.find('a'):
            print("cs:find"+weblink.find('a').string)
        else:
            print("cs:not find")
       # if weblink.string == '‹ 上頁':
       #     href = weblink['href']
       #     print("cs:find pre-link")
       #     articles.append({'pre_link':href})

    print(articles)
    return articles


def parse(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    links = soup.find(id='main-content').find_all('a')
    img_urls = []
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
            img_urls.append(link['href'])
    return img_urls

def save(img_urls, title):
    if img_urls:
        try:
            dname = title.strip()  # 用 strip() 去除字串前後的空白
            os.makedirs(dname)
            for img_url in img_urls:
                print("cs path:"+img_url)
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
if page:
    #date = time.strftime("%m/%d").lstrip('0')  # 今天日期, 去掉開頭的 '0' 以符合 PTT 網站格式
    date = time.strftime("%m/%d")
    print(date)
    #print("today: "+date)
    current_articles = get_articles(page, date)
    #print(current_articles)
    for article in current_articles:
        print("CS No:"+str(article['push_count']))
        if article["push_count"] >50:
            page = get_web_page(PTT_URL + article['href'])
            if page:
                img_urls = parse(page)
                save(img_urls, article['title'])
                article['num_image'] = len(img_urls)
