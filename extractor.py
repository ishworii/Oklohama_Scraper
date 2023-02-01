from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import logging
import utility
import sys
import json

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


def setup():
    # Headless/incognito Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    logging.info("Webdriver setup done.")

    driver.get("https://www.google.com/")

    sleep(3)

    return driver


def main(driver, filename):
    with open(filename, "r") as file:
        data = json.load(file)

    scraped = 0
    for each_data in data:
        if each_data["scraped"]:
            scraped += 1
    logging.info(f"Scraped {scraped}/{len(data)}")

    # start the main loop
    for index, each_data in enumerate(data):
        if each_data["scraped"]:
            continue
        logging.info(f"Scraping {index+1}/{len(data)} datasets..")

        # get the url
        driver.get(each_data["link"])
        sleep(3)
        # find the csv links
        csv_links = utility.extract_list(driver)
        if not csv_links:
            logging.info("CSV links not found...skipping")
            continue
        for each_link in csv_links:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            # get the new url
            driver.get(each_link)
            sleep(3)
            try:
                retval = utility.extract_details(driver)
                if retval:
                    table_name, table_description, table_url, download_link = retval
                    os.chdir("/home/ik-pc/Desktop/upwork/oklohama/data")
                    utility.save_everything(
                        table_name, table_description, table_url, download_link
                    )
            except Exception as e:
                logging.info(f"Exception {e} occured...")
                break

            # close and switch back to the original tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])


if __name__ == "__main__":
    filename = "tmp.json"
    driver = setup()
    main(driver, filename)
