from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

import os
import logging
import time
import filecmp

URL_TO_MONITOR : str = "https://jexam.inf.tu-dresden.de/de.jexam.web.v5/spring/welcome"
DELAY_TIME_SECONDS : int = 10

def content_comparison():
    f1 = './previous_exam_results.txt'
    f2 = './new_exam_results.txt'
    if not os.path.exists(f2):
        return False
    return filecmp.cmp(f1, f2)


def filter_for_exams(content:str, file_name:str):
    with open(file_name, 'w') as f:
        for line in open(content):
            if 'INF' in line or 'PLB' in line:
                f.write(line)


def page_crawler():

### Configurations
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.page_load_strategy = 'none'

    # returns the path web driver downloaded
    chrome_path = ChromeDriverManager().install()
    chrome_service = Service(chrome_path)
    # pass the defined options and service objects to initialize the web driver
    driver = Chrome(options=options, service=chrome_service)
    driver.implicitly_wait(5)

    driver.get(URL_TO_MONITOR)
    time.sleep(2)
###
    page_content = driver.find_element(By.CSS_SELECTOR, "div[class*='news-wrapper']")

    # check if the file exists, ran on the first iteration
    if not os.path.exists("previous_content.txt"):
        open("previous_content.txt", 'w+').close()

    filehandle = open('previous_content.txt', 'w')
    filehandle.write(page_content.text)
    filehandle.close()

    filter_for_exams('previous_content.txt', 'previous_exam_results.txt')

    if not os.path.exists('new_exam_results.txt'):
        open('new_exam_results.txt', 'w+').close()

    if content_comparison() is True:
        return False
    else:
        with open('previous_content.txt','w') as f:
            f.write(page_content.text)
        filter_for_exams('previous_content.txt', 'previous_exam_results.txt')
        with open('previous_exam_results.txt','r') as firstfile, open('new_exam_results.txt','a') as secondfile:
            for line in firstfile:
                secondfile.write(line)
            firstfile.close()
            secondfile.close()
        return True


def main():
    log = logging.getLogger(__name__)
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    log.info("Running Website Monitor")
    while True:
        try:
            if page_crawler():
                log.info("WEBPAGE WAS CHANGED.")
            else:
                log.info("Webpage was not changed.")
        except:
            log.info("Error checking website.")
        time.sleep(DELAY_TIME_SECONDS)


if __name__ == "__main__":
    main()
