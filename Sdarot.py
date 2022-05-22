import os
import sys
import time
import requests

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
# from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.chrome.options import Options


from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


def main():
    url_input = input("Please enter the url of the series, without the season or episode: \n")
    season_input = int(input("Please enter the requested season number: \n"))
    episode_input = int(input("Please enter the first episode to be downloaded: \n"))
    all_input = input("Do you want to download all other episodes, starting of the selected episode? (Yes/No)\n")
    download_all = True if all_input.upper() == "YES" else False

    executable_path = "C:\\Users\\user\\PycharmProjects\\WebScripting\\chromedriver.exe"
    os.environ["webdriver.chrome.driver"] = executable_path
    chrome_options = Options()
    # chrome_options.add_extension('C:\\Users\\user\\PycharmProjects\\WebScripting\\Flash Video Downloader.crx')
    browser = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
    download_series(browser, url_input, season_input, episode_input, download_all)


def download_series(browser, base_url, season, episode, download_all):
    if download_all:
        print(f"Selected all episodes in season {season}, starting of episode {episode}...")
    else:
        print("Selected single episode " + str(episode) + "...")

    full_url = base_url + '/season/' + str(season) + '/episode/' + str(episode)
    browser.get(full_url)
    episodes_list = browser.find_elements_by_xpath("//ul[contains(@id,'episode')]/li")
    while episode <= len(episodes_list):
        full_url = base_url + '/season/' + str(season) + '/episode/' + str(episode)  # with the next episode
        episode_available = is_episode_available(browser, full_url)
        if episode_available:
            get_episode(browser, episode)
            # download_episode(browser)
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
    attempts = 3
    ready = False
    while attempts > 0:
        browser.get(full_url)
        try:
            WebDriverWait(browser, 35).until(
                cond.element_to_be_clickable((By.XPATH, "//span[contains(.,'נגן את הפרק')]"))).click()
            ready = True
        except TimeoutException:
            err_msg = browser.find_element_by_xpath("//h3[contains(.,'שגיאה 2!')]")
            if err_msg.text == "שגיאה 2!":
                attempts -= 1
                continue
        break
    if ready:
        print("Episode is ready")
    return ready


def get_episode(browser, episode):
    time.sleep(2)
    video_src = browser.find_elements_by_tag_name("video")[0].get_attribute("src")
    if not video_src or video_src == "":
        print("Probably encountered an ad, will try again when it will be finished")
        time.sleep(33)
        video_src = browser.find_elements_by_tag_name("video")[0].get_attribute("src")

    cookies = browser.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    response = s.get(video_src, stream=True)
    if response.status_code == 200:
        print(f"Start downloading episode {episode}. "
              f"It might take a while and no progress will be visible until download is completed.")
        with open(f'{episode}.mp4', 'wb') as f:
            f.write(response.content)
        # browser.execute_script("window.open('" + video_src + "')")
    else:
        print(f"Video url for episode {episode} is not accessible, skipping it")


def download_episode(browser):
    # 1st step - click on extension
    try:
        ######
        # rob = Robot()
        # click_on_gui("C:\\Users\\user\\PycharmProjects\\WebScripting\\flashIcon.png")
        # time.sleep(2)
        # rob.key_press('tab')
        # time.sleep(3)
        # rob.key_press('tab')
        # time.sleep(3)
        # rob.key_press('enter')
        # time.sleep(3)
        # browser.switch_to.window(browser.window_handles[-1])
        #######
        # video = browser.find_element_by_tag_name("source")
        # video.send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(
        #     Keys.TAB).send_keys(Keys.ENTER).send_keys(Keys.ARROW_UP).send_keys(Keys.ENTER)
       #  video = browser.find_element_by_tag_name("body")
       # # video.send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.ENTER).send_keys(Keys.ARROW_UP).send_keys(Keys.ENTER)
       #
       # # video.key_down(Keys.CONTROL).send_keys('S').key_up(Keys.CONTROL).send_keys(
       #  #    'MyDocumentName').key_down(Keys.ALT).send_keys('S').key_up(Keys.ALT)
       #  ActionChains(video).context_click(browser.find_element_by_tag_name("body").send_keys(Keys.ARROW_DOWN)).perform()

        '''
        # 2nd step - click on download button
        rob.key_press('tab')
        time.sleep(2)
        rob.key_press('tab')
        time.sleep(2)
        rob.key_press('tab')
        time.sleep(2)
        rob.key_press('enter')
        time.sleep(3)
        global allow_flag
        # 3rd step - click on allow
        if not allow_flag:
            print("Clicking on allow")
            rob.key_press('tab')
            time.sleep(2)
            rob.key_press('enter')
            time.sleep(3)
            allow_flag = True
            '''
    except TypeError as e:
        print("Error in pyautogui: " + str(e))


if __name__ == '__main__':
    main()
