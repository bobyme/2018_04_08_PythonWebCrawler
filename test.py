
import os
#for (root, dirs, files) in os.walk(os.path.dirname(__file__)):

#(root, dirs, files)=os.walk(os.path.dirname(__file__))
result=os.walk(os.path.dirname(__file__))
#print("root:"+root)
#print("dirs:"+dirs)
#print("files:"+files)

print(result)