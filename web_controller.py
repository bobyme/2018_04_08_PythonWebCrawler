from selenium import webdriver
chrome_path = "/Applications/Google Chrome.app" #chromedriver.exe執行檔所存在的路徑

#chromedriver = "Mach/Users/markchang/tools/webdriver/chromedriver"
browser =webdriver.Chrome()
#browser = webdriver.Safari()
print(type(browser))
browser.get('http://google.com')