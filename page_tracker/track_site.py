from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from discord_webhook import DiscordWebhook, DiscordEmbed

import os
import time
import logging
import filecmp
from dotenv import load_dotenv

load_dotenv()

URL_TO_MONITOR: str = "https://jexam.inf.tu-dresden.de/de.jexam.web.v5/spring/welcome"
PAYLOAD_URL: str = os.getenv("PAYLOARD_URL")
DELAY_TIME_SECONDS: int = 20


class Page_Tracker:
    def content_comparison(self, previous, new):
        if not os.path.exists(new):
            return False
        return filecmp.cmp(previous, new)

    def return_new_exams(self, File1, File2):
        with open(File1, "r") as f:
            old = set(f.readlines())

        with open(File2, "r") as f:
            new = set(f.readlines())

        return list(new.intersection(old))

    def write_content_in_previous(self, content):
        if not os.path.exists("previous_exams.txt"):
            open("previous_exams.txt", "w+").close()

        filehandle = open("previous_exams.txt", "w")
        filehandle.write(content)
        filehandle.close()

        if not os.path.exists("new_exams.txt"):
            open("new_exams.txt", "w+").close()

    def page_crawler(self):

        ### Configurations
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.page_load_strategy = "none"

        # # returns the path web driver downloaded
        chrome_path = "/user/bin/chromedriver"
        chrome_service = Service(chrome_path)
        # # pass the defined options and service objects to initialize the web driver
        driver = webdriver.Chrome(options=options, service=chrome_service)
        driver.implicitly_wait(2)

        driver.get(URL_TO_MONITOR)
        time.sleep(2)

        page_content = driver.find_element(By.TAG_NAME, "ul")

        # check if the file exists, ran on the first iteration
        self.write_content_in_previous(page_content.text)

        if self.content_comparison("./previous_exams.txt", "./new_exams.txt"):
            return False

        with open("previous_exams.txt", "r") as firstfile, open(
            "new_exams.txt", "a"
        ) as secondfile:
            for line in firstfile:
                secondfile.write(line)
        return True

    def run(self):
        log = logging.getLogger(__name__)
        logging.basicConfig(
            level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s %(message)s"
        )
        log.info("Running Website Monitor")
        while True:
            try:
                if self.page_crawler():
                    log.info("Webpage has changed.")
                    results = self.return_new_exams(
                        "previous_exams.txt",
                        "new_exams.txt",
                    )

                    for result in results:
                        webhook = DiscordWebhook(url=PAYLOAD_URL)
                        embed = DiscordEmbed(
                            title=f" <a:bpG:890945228679299082> Prüfungserbegnis {result} ist nun verfügbar.",
                            color=2158112,
                        )
                        webhook.add_embed(embed)
                        time.sleep(1)
                        webhook.execute()
                else:
                    log.info("Webpage has not changed.")
            except:
                log.info("Error checking website.")
            time.sleep(DELAY_TIME_SECONDS)


if __name__ == "__main__":
    tracker = Page_Tracker()
    tracker.run()
