import requests
import time
import json
import datetime
import re, urllib
import os
from bs4 import BeautifulSoup

#url ='https://www.dcard.tw/_api/forums/sex/posts?popular=true'

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


def save(img_urls,dname):
    if img_urls:
        os.makedirs(dname)
        print("005:"+dname)
        #print(img_urls[0]['url'])
        #print("0016")
        try:
            #print("001:"+img_urls)

            for img_url in img_urls:
                print("011:" + img_url['url'])
                dimg_url = img_url['url']
                    # if img_url.split('//')[1].startswith('m.'):
                    #    img_url = img_url.replace('//m.', '//i.')
                    # if not img_url.split('//')[1].startswith('i.'):
                    #    img_url = img_url.split('//')[0] + '//i.' + img_url.split('//')[1]
                    # if not img_url.endswith('.jpg'):
                    #    img_url += '.jpg'
                fname = img_url['url'].split('/')[-1]
                    # print("017"+str(fname))
                urllib.request.urlretrieve(dimg_url, os.path.join(dname, fname))
        except Exception as e:
            print(e)
            print("013")




url ='https://www.dcard.tw/_api/forums/sex/posts?popular=false'
blacklist=["[公告] 表特板板規 (2015.2.12)","[公告] 不願上表特 ＆ 優文推薦 ＆ 檢舉建議專區"]

dateoffset=30
likecount_threshod=10



#mo=datetransfer.search(dcarddata[0]['updatedAt'])
def DcardTransferS2D(sDate):
    datetransfer = re.compile(r'(\d{4})-(\d{1,2})-(\d{2})')
    mo = datetransfer.search(sDate)
    if mo:
        sDcardDate = mo.group(1) + '_' + mo.group(2) + '_' + mo.group(3)  # 組合日期格式給資料夾檔名使用
        DcardDate = datetime.datetime.strptime(sDcardDate, "%Y_%m_%d").date()
    else:
        print("spttdate is abnormal:" + spttdate)
    return sDcardDate,DcardDate


#print("0010:"+str(DcardTransferS2D(dcarddata[0]['updatedAt'])))
#print("0011:"+str(DcardTransferS2D(dcarddata[1]['updatedAt'])))
#print(type(dcarddata[0]['likeCount']))
currentdate = datetime.date.today()
#print("002:"+str(currentdate))


keeptracking=1
while keeptracking==1:
    post = get_web_page(url)
    print("CS Url:"+url)
    dcarddata = json.loads(post)
    slatestdate, latestdate = DcardTransferS2D(dcarddata[0]['updatedAt'])
    for data in dcarddata:
    #    if (currentdate-datetime.timedelta(days=dateoffset)<=latestdate)&(data[i]['likeCount']>likecount_threshod):
        if (currentdate - datetime.timedelta(days=dateoffset) <= latestdate):
            if(data['likeCount'] > likecount_threshod):
                dname = slatestdate + data['title']  # 用 strip() 去除字串前後的空白
                #print("003:" + dname)
                #os.makedirs(dname)
                #print("005"+str(data['media']))
                save(data['media'],dname)
        else:
            keeptracking=0
    if keeptracking==1:
        url=url+"&before="+str(dcarddata[29]["id"])

