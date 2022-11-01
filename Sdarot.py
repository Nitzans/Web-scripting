import os
import sys
import time
import requests

from os import path
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
# from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
USERNAME = "borozoz12@gmail.com"
PASSWORD = "zozorob"
DOWNLOAD_PATH = "C:\\Users\\User\\Downloads"

def main():
    url_input = input("Please enter the url of the series, without the season or episode: \n")
    season_input = int(input("Please enter the requested season number: \n"))
    episode_input = int(input("Please enter the first episode to be downloaded: \n"))
    all_input = input("Do you want to download all other episodes, starting of the selected episode? (Yes/No)\n")
    download_all = True if all_input.upper().startswith('Y') else False

    # executable_path = "C:\\Users\\User\\Desktop\\Sdarot script\\chromedriver.exe"
    # os.environ["webdriver.chrome.driver"] = executable_path
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # chrome_options.add_extension('C:\\Users\\user\\PycharmProjects\\WebScripting\\Flash Video Downloader.crx')
    # browser = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    download_series(browser, url_input, season_input, episode_input, download_all)


def download_series(browser, base_url, season, episode, download_all):
    if download_all:
        print(f"Selected all episodes in season {season}, starting of episode {episode}...")
    else:
        print("Selected single episode " + str(episode) + "...")

    full_url = base_url + '/season/' + str(season) + '/episode/' + str(episode)
    browser.get(full_url)
  
    episodes_list = browser.find_elements("xpath", "//ul[contains(@id,'episode')]/li")
    login(browser, USERNAME, PASSWORD)
    while episode <= len(episodes_list):
        full_url = base_url + '/season/' + str(season) + '/episode/' + str(episode)  # with the next episode
        episode_available = is_episode_available(browser, full_url)
        if episode_available:
            get_episode(browser, episode)
        else:
            print("Error loading episode " + str(episode) + ", skipping it...")
        if not download_all:
            break
        time.sleep(1)
        episode = episode + 1
        browser.execute_script("window.open('" + base_url + '/season/' + str(season) + "')")
        browser.switch_to.window(browser.window_handles[-1])

    print("Done! If no other active downloads, you may close the browser")


def is_episode_available(browser, full_url):
    attempts = 5
    ready = False
    while attempts > 0:
        browser.get(full_url)
        try:
            WebDriverWait(browser, 40).until(
                cond.element_to_be_clickable((By.XPATH, "//span[contains(.,'נגן את הפרק')]"))).click()
            ready = True
        except TimeoutException:
            err_msg = browser.find_element("xpath", "//h3[contains(.,'שגיאה 2!')]")
            if err_msg.text == "שגיאה 2!":
                attempts -= 1
                print(f"Servers are busy, will try again...")
                continue
        break
    if ready:
        print("Episode is available")
    return ready


def get_episode(browser, episode):
    time.sleep(2)
    video_src = browser.find_elements(By.TAG_NAME, "video")[0].get_attribute("src")
    if not video_src or video_src == "":
        print("Probably encountered an ad, will try again when it will be finished")
        time.sleep(33)
        video_src = browser.find_elements(By.TAG_NAME, "video")[0].get_attribute("src")

    cookies = browser.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    head = s.head(video_src)
    file_size = int(head.headers["Content-Length"])
    response = s.get(video_src, stream=True)
    if response.status_code == 200:
        print(f"Start downloading episode {episode}, it might take a while...")
              
        with tqdm.wrapattr(open(f'{DOWNLOAD_PATH}\\{episode}.mp4', 'wb'), "write",
                   miniters=1, desc=str(episode),
                   total=file_size) as fout:
            for chunk in response:
                fout.write(chunk)
        print(f"Episode {episode} was downloaded successfully")
    else:
        print(f"Video url for episode {episode} is not accessible, skipping it")


def login(browser, username, password):
    print("Logging...")
    browser.implicitly_wait(15)
    browser.find_element("xpath", "//button[@data-target='#loginForm']").click()
    browser.implicitly_wait(5)
    browser.find_element("xpath", "//input[@name='username']").send_keys(username)
    browser.find_element("xpath", "//input[@name='password']").send_keys(password)
    browser.find_element("xpath", "//button[@name='submit_login']").click()
    print("Logged in successfully")


if __name__ == '__main__':
    main()