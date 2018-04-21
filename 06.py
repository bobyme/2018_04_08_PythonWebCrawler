import re
datetransfer=re.compile(r'(\d{4})/(\d{1,2})/(\d{2})')
date="2018/4/11"
mo=datetransfer.search(date)
if mo:
    print("CS"+mo.group(1))
else:
    print("not match")