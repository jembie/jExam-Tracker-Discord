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
DELAY_TIME_SECONDS : int = 300

class Page_Tracker():

    def content_comparison(self):
        f1 = './previous_exam_results.txt'
        f2 = './new_exam_results.txt'
        if not os.path.exists(f2):
            return False
        return filecmp.cmp(f1, f2)


    def filter_for_exams(self, content:str, file_name:str):
        with open(file_name, 'w') as f:
            for line in open(content):
                if 'INF' in line or 'PLB' in line:
                    f.write(line)

    def return_new_exams(File1,File2):
        with open(File1,'r') as f:
            prev = set(f.readlines())


        with open(File2,'r') as f:
            new = set(f.readlines())

        return list(new - prev)

    def page_crawler(self):

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

        self.filter_for_exams('previous_content.txt', 'previous_exam_results.txt')

        if not os.path.exists('new_exam_results.txt'):
            open('new_exam_results.txt', 'w+').close()

        if self.content_comparison() is True:
            return False
        else:
            with open('previous_content.txt','w') as f:
                f.write(page_content.text)
            self.filter_for_exams('previous_content.txt', 'previous_exam_results.txt')
            with open('previous_exam_results.txt','r') as firstfile, open('new_exam_results.txt','a') as secondfile:
                for line in firstfile:
                    secondfile.write(line)
                firstfile.close()
                secondfile.close()
            return True


    def run(self):
        log = logging.getLogger(__name__)
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
        log.info("Running Website Monitor")
        while True:
            try:
                if self.page_crawler():
                    log.info("WEBPAGE WAS CHANGED.")
                    self.return_new_exams("./page_tracker/previous_exam_results.txt", "./page_tracker/new_exam_results.txt")


                else:
                    log.info("Webpage was not changed.")
            except:
                log.info("Error checking website.")
            time.sleep(DELAY_TIME_SECONDS)


if __name__ == "__main__":
    tracker = Page_Tracker()
    tracker.run()