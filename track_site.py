import typing as t
import pytest
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
PAYLOAD_URL: str | None = os.getenv("PAYLOAD_URL")
DELAY_TIME_SECONDS: int = 20


def filter_new_entries(one: t.Iterable[str], other: t.Iterable[str]) -> list[str]:
    """Return elements in `other` which did not appear in `where`.

    Moral equivalent of `set(other) - set(one)`, but
    1. does not kill duplicates and
    2. is stable with respect to the ordering of `other`.
    """
    one_set = set(one)
    return [line for line in other if line not in one_set]


# TODO move to `test.py` to not interfere with main program
@pytest.mark.parametrize("new_entries, expected", [
    (["a", "b", "d", "c"], ["d"]),
    (["a", "b", "d"], ["d"]),  # c is missing, but it doesn't matter
    (["new1", "a", "b", "new2", "c", "d"], ["new1", "new2", "d"]),
    (["new1", "a", "d", "b", "new2", "c", "d"], ["new1", "d", "new2", "d"]),
])
def test_new_filter(new_entries, expected):
    old_entries = ["a", "b", "c"]
    assert filter_new_entries(old_entries, new_entries) == expected


class Page_Tracker:
    """
    A class for monitoring a specific webpage and sending notifications when updates occur.

    Methods:
    --------
    content_comparison(previous: str, new: str) -> bool:
        Compares the content of two files.

    write_content_in_new(content: str):
        Writes the scraped content into `new_exams.txt`.

    page_crawler() -> bool:
        Scrapes the webpage and checks for updates.

    return_new_exams(previous: str, new: str) -> set:
        Filters for any new exam results.

    send_webhook_msg():
        Sends a webhook message with new exam results.

    overwrite_previous_content():
        Overwrites the content of the previous exams file with the new content.

    run():
        Runs the website monitor continuously.
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
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.page_load_strategy = "none"

        # path where webdriver is downlaoded
        chrome_path = "/user/bin/chromedriver"
        chrome_service = Service(chrome_path)
        # pass the defined options and service objects to initialize the web driver
        driver = webdriver.Chrome(options=options, service=chrome_service)
        driver.implicitly_wait(2)

        driver.get(URL_TO_MONITOR)
        time.sleep(2)

        page_content = driver.find_element(By.TAG_NAME, "ul")

        if not os.path.exists("previous_exams.txt"):
            open("previous_exams.txt", "w+").close()

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

        return filter_new_entries(one=old, other=new)  # new \ old

    def send_webhook_msg(self):
        """
        Sends a webhook message with new exam results.
        """

        results = self.return_new_exams(
            "previous_exams.txt",
            "new_exams.txt",
        )
        for result in results:
            webhook = DiscordWebhook(url=PAYLOAD_URL)
            embed = DiscordEmbed(
                title=f" <a:bpG:890945228679299082> Prüfungsergebnis {result} ist nun verfügbar.",
                color=2158112,
            )
            webhook.add_embed(embed)
            time.sleep(1)
            webhook.execute()

    def overwrite_previous_content(self):
        """
        Overwrites the content of the previous exams file with the new content.
        """

        with open("new_exams.txt", "r") as new, open(
            "previous_exams.txt", "w+"
        ) as previous:
            for line in new:
                previous.write(line)

    def run(self):
        """
        Runs the website monitor continuously.
        """

        log = logging.getLogger(__name__)
        logging.basicConfig(
            level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s %(message)s"
        )
        log.info("Running Website Monitor")
        while True:
            try:
                if self.page_crawler():
                    log.info("Webpage has changed.")
                    self.send_webhook_msg()
                    self.overwrite_previous_content()

                else:
                    log.info("Webpage has not changed.")
            except:
                log.info("Error checking website.")
            time.sleep(DELAY_TIME_SECONDS)


if __name__ == "__main__":
    load_dotenv()
    tracker = Page_Tracker()
    tracker.run()
