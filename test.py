
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager
import os
import time


options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.page_load_strategy = 'none'

# returns the path web driver downloaded
chrome_path = ChromeDriverManager().install()
chrome_service = Service(chrome_path)
# pass the defined options and service objects to initialize the web driver
driver = Chrome(options=options, service=chrome_service)
driver.implicitly_wait(5)

url = "https://jexam.inf.tu-dresden.de/de.jexam.web.v5/spring/welcome"

driver.get(url)
time.sleep(2)

content = driver.find_element(By.CSS_SELECTOR, "div[class*='news-wrapper'")

if not os.path.exists("previous_content.txt"):
    open("previous_content.txt", 'w+').close()

filehandle = open("previous_content.txt", 'r')
previous_response_html = filehandle.read()
filehandle.close()

filehandle = open("previous_content.txt", 'w')
filehandle.write(content.text)
filehandle.close()

open('exam_results.txt','w').writelines([ line for line in open('previous_content.txt') if 'INF' in line or 'PLB' in line])



