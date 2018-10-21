#
# A simple Evernote API demo script that lists all notebooks in the user's
# account and creates a simple test note in the default notebook.
#
# Before running this sample, you must fill in your Evernote developer token.
#
# To run (Unix):
#   export PYTHONPATH=../../lib; python EDAMTest.py
#

#for Evernote
import hashlib
import binascii
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import os

#for Dcard
import requests
import time
import json
import datetime
import re, urllib
from bs4 import BeautifulSoup
import docx


from evernote.api.client import EvernoteClient

# Real applications authenticate with Evernote using OAuth, but for the
# purpose of exploring the API, you can get a developer token that allows
# you to access your own Evernote account. To get a developer token, visit
# https://sandbox.evernote.com/api/DeveloperToken.action
auth_token = "S=s1:U=94942:E=16d37b3d647:C=165e002a778:P=1cd:A=en-devtoken:V=2:H=7d9c53d58fe793e7bc4aff51c1029cd3"

#Dcard crawler setting
url ='https://www.dcard.tw/_api/forums/sex/posts?popular=false'
url_content='http://dcard.tw/_api/posts/'
blacklist=["看板功能相關說明"]
dateoffset=1
likecount_threshod=500

if auth_token == "Token_check":
    print("Please fill in your developer token")
    print("To get a developer token, visit " \
          "https://sandbox.evernote.com/api/DeveloperToken.action")
    exit(1)

# Initial development is performed on our sandbox server. To use the production
# service, change sandbox=False and replace your
# developer token above with a token from
# https://www.evernote.com/api/DeveloperToken.action
# To access Sandbox service, set sandbox to True
# To access production (International) service, set both sandbox and china to False
# To access production (China) service, set sandbox to False and china to True

sandbox=True
china=False

client = EvernoteClient(token=auth_token, sandbox=sandbox,china=china)

user_store = client.get_user_store()

version_ok = user_store.checkVersion(
    "Evernote EDAMTest (Python)",
    UserStoreConstants.EDAM_VERSION_MAJOR,
    UserStoreConstants.EDAM_VERSION_MINOR
)
print("Is my Evernote API version up to date? ", str(version_ok))
print("")
if not version_ok:
    exit(1)

note_store = client.get_note_store()

# List all of the notebooks in the user's account
notebooks = note_store.listNotebooks()
print("Found ", len(notebooks), " notebooks:")
for notebook in notebooks:
    print("  * ", notebook.name)

print()
print("Creating a new note in the default notebook")
print()

#Evernote function
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

def getcontent(id):
    post=get_web_page(url_content+str(id))
    dcarddata = json.loads(post)
    return dcarddata["content"]


def EvernoteAddNote(notedata):
    # To create a new note, simply create a new Note object and fill in
    # attributes such as the note's title.
    note = Types.Note()
    #note.title = "Test note from EDAMTest.py"
    note.title = notedata["Title"]


    # To include an attachment such as an image in a note, first create a Resource
    # for the attachment. At a minimum, the Resource contains the binary attachment
    # data, an MD5 hash of the binary data, and the attachment MIME type.
    # It can also include attributes such as filename and location.
    for root, dirs, files in os.walk(notedata["PicPath"], False):
        print("Root = ", root, "dirs = ", dirs, "files = ", files)

    image_path = constants_path = os.path.join(os.path.dirname(__file__), "enlogo.png")
    print("image_path:" + str(image_path))
    print("Path:" + os.path.dirname(__file__))
    with open(image_path, 'rb') as image_file:
        image = image_file.read()
    md5 = hashlib.md5()
    md5.update(image)
    hash = md5.digest()

    data = Types.Data()
    data.size = len(image)
    data.bodyHash = hash
    data.body = image

    resource = Types.Resource()
    resource.mime = 'image/png'
    resource.data = data

    # Now, add the new Resource to the note's list of resources
    note.resources = [resource]

    # To display the Resource as part of the note's content, include an <en-media>
    # tag in the note's ENML content. The en-media tag identifies the corresponding
    # Resource using the MD5 hash.
    hash_hex = binascii.hexlify(hash)
    hash_str = hash_hex.decode("UTF-8")

    # The content of an Evernote note is represented using Evernote Markup Language
    # (ENML). The full ENML specification can be found in the Evernote API Overview
    # at http://dev.evernote.com/documentation/cloud/chapters/ENML.php
    note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    note.content += '<!DOCTYPE en-note SYSTEM ' \
                    '"http://xml.evernote.com/pub/enml2.dtd">'
    note.content +='<en-note>%s<br/>' % notedata["Content"]
    #note.content += '<en-media type="image/png" hash="{}"/>'.format(hash_str)
    note.content += '</en-note>'

    # Finally, send the new note to Evernote using the createNote method
    # The new Note object that is returned will contain server-generated
    # attributes such as the new note's unique GUID.
    created_note = note_store.createNote(note)

    print("Successfully created a new note with GUID: ", created_note.guid)

def DCardsave(img_urls,dTitle,id,dLikeCount):
    if img_urls:
        os.makedirs(dTitle)
        temp=dict()
        currentdir=os.getcwd()
        print("005:"+dTitle)
        dcontent = getcontent(id)
        temp["ArticleID"] = str(id)
        temp["Title"]= dTitle
        temp["LikeCount"]= str(dLikeCount)
        temp["Content"]=dcontent

        #Dcarddoc.add_paragraph(dcontent)
        try:
            #print("001:"+img_urls)

            for img_url in img_urls:
                print("011:" + img_url['url'])
                dimg_url = img_url['url']
                fname = img_url['url'].split('/')[-1]
                urllib.request.urlretrieve(dimg_url, os.path.join(dTitle, fname))
                dPicPath=currentdir+"/"+dTitle+"/"+fname
                print("035:"+currentdir+"/"+dTitle+"/"+fname)
            temp["PicPath"]=currentdir + "/" + dTitle
        except Exception as e:
            print(e)
            print("013")
        EvernoteAddNote(temp)


def DcardTransferS2D(sDate):
    datetransfer = re.compile(r'(\d{4})-(\d{1,2})-(\d{2})')
    mo = datetransfer.search(sDate)
    if mo:
        sDcardDate = mo.group(1) + '_' + mo.group(2) + '_' + mo.group(3)  # 組合日期格式給資料夾檔名使用
        DcardDate = datetime.datetime.strptime(sDcardDate, "%Y_%m_%d").date()
    else:
        print("spttdate is abnormal:" + sDate)
    return sDcardDate,DcardDate



scurrentdate,currentdate = DcardTransferS2D(str(datetime.date.today()))
Dcarddoc = docx.Document()
keeptracking=1
dcardurl=url
while keeptracking==1:
    post = get_web_page(dcardurl)
    print("CS Url:"+dcardurl)

    dcarddata = json.loads(post)
    slatestdate, latestdate = DcardTransferS2D(dcarddata[0]['updatedAt'])
    for data in dcarddata:
        if (currentdate - datetime.timedelta(days=dateoffset) <= latestdate):
            if(data['likeCount'] > likecount_threshod) and (data['title'] not in blacklist):
                dTitle = slatestdate + data['title']  # 用 strip() 去除字串前後的空白
                dID=data["id"]
                dLikeCount=data["likeCount"]
                print("033:" + url_content + str(dID))
                #dexcerpt=data['excerpt']
                DCardsave(data['media'],dTitle,dID,dLikeCount)
        else:
            keeptracking=0
    if keeptracking==1:
        dcardurl=url+"&before="+str(dcarddata[29]["id"])
#docfilename="dcardata_from"+str(currentdate)+"to"+str(slatestdate)+"_.docx'
#Dcarddoc.save("dcardata_from"+slatestdate+"_to_"+scurrentdate+"_Thr_"+str(likecount_threshod)+"_.docx")




