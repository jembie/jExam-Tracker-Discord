import shutil
import typing as t
import os
import time
import logging
import filecmp

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv

load_dotenv()

URL_TO_MONITOR: str = "https://jexam.inf.tu-dresden.de/de.jexam.web.v5/spring/welcome"
PAYLOAD_URL: str | None = os.getenv("PAYLOAD_URL")
CHROME_PATH: str = os.getenv("CHROME_PATH", "/user/bin/chromedriver")
DELAY_TIME_SECONDS: int = 20


log = logging.getLogger(__name__)


def filter_new_entries(one: t.Iterable[str], other: t.Iterable[str]) -> list[str]:
    """Return elements in `other` which did not appear in `where`.

    Moral equivalent of `set(other) - set(one)`, but
    1. does not kill duplicates and
    2. is stable with respect to the ordering of `other`.
    """
    one_set = set(one)
    return [line for line in other if line not in one_set]


def report_new_result(result: str, url: str) -> None:
    """Report new exam result via discord webhook"""
    webhook = DiscordWebhook(url=url)
    embed = DiscordEmbed(
        title=f" <a:bpG:890945228679299082> Prüfungsergebnis {result} ist nun verfügbar.",
        color=2158112,
    )
    webhook.add_embed(embed)
    time.sleep(1)
    webhook.execute()


class Page_Tracker:
    """
    A class for monitoring a specific webpage and sending notifications when updates occur.
    """

    def content_comparison(self, previous: str, new: str) -> bool:
        """
        Compares the content of two files.

        Args:
            previous: The path of the file with previous content of the web page.
            new: The path of the file with the updated content of the web page.

        Returns:
            bool: A boolean indicating whether the two files have identical content.
        """

        return filecmp.cmp(previous, new)

    def write_content_in_new(self, content: str) -> None:
        """
        Writes the scraped content into`new_exams.txt`.

        Args:
            content: The content to be written to the file.
        """

        with open("new_exams.txt", "w+") as new:
            new.write(content)

    def page_crawler(self) -> bool:
        """
        Scrapes the webpage and checks for updates.

        Returns:
            bool: A boolean indicating whether updates were found.
        """

        ### Configurations
        log.debug("Setting up chrome driver %r", CHROME_PATH)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.page_load_strategy = "none"

        # returns the path web driver downloaded
        chrome_service = Service(CHROME_PATH)
        # pass the defined options and service objects to initialize the web driver
        driver = webdriver.Chrome(options=options, service=chrome_service)
        driver.implicitly_wait(2)

        log.debug("Fetching url %r", URL_TO_MONITOR)
        driver.get(URL_TO_MONITOR)
        time.sleep(2)

        page_content = driver.find_element(By.ID, "news-wrapper").find_element(
            By.TAG_NAME, "ul"
        )

        if not os.path.exists("previous_exams.txt"):
            with open("previous_exams.txt", "w+"):
                pass

        if not os.path.exists("new_exams.txt"):
            with open("new_exams.txt", "w+") as new:
                new.write(page_content.text)
            return True

        self.write_content_in_new(page_content.text)

        return not self.content_comparison("previous_exams.txt", "new_exams.txt")

    def return_new_exams(self, previous: str, new: str) -> list[str]:
        """
        This method filters for any new exam results.

        Args:
            previous (str): The path of the first file.
            new (str): The path of the second file.

        Returns:
            set: A set containing the difference between the contents of two files.
        """

        with open(previous, "r") as f:
            old = f.read().split("\n")

        with open(new, "r") as f:
            new = f.read().split("\n")

        return filter_new_entries(one=old, other=new)[::-1]  # new \ old

    def send_webhook_msg(self) -> None:
        """
        Sends a webhook message with new exam results.
        """

        results = self.return_new_exams(
            "previous_exams.txt",
            "new_exams.txt",
        )
        log.info("Found %d new results", len(results))
        log.debug("new results:\n%s", "\n".join(f"    {r}" for r in results))
        for result in results:
            report_new_result(result, url=PAYLOAD_URL)

    def overwrite_previous_content(self) -> None:
        """
        Overwrites the content of the previous exams file with the new content.
        """
        shutil.copy("new_exams.txt", "previous_exams.txt")

    def run(self) -> None:
        """
        Runs the website monitor continuously.
        """
        logging.basicConfig(
            level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s %(message)s"
        )
        log.info("Starting up Website Monitor")
        while True:
            try:
                log.info("Checking Webpage...")
                if self.page_crawler():
                    log.info("...Webpage has changed!")
                    self.send_webhook_msg()
                    self.overwrite_previous_content()

                else:
                    log.info("...Webpage has not changed.")
            except Exception as e:
                log.info("Error checking website: %r", e)
            time.sleep(DELAY_TIME_SECONDS)


if __name__ == "__main__":
    tracker = Page_Tracker()
    tracker.run()
