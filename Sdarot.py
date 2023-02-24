import os
import sys
import time

import requests
from os import path
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
USERNAME = "USERNAME"
PASSWORD = "PASS"
BASE_URL = "https://www.sdarot.tw"
DEFAULT_TARGET_PATH = os.path.expandvars("%userprofile%\\Downloads")


class StartWindow:
    def __init__(self, series_input, season_input, episode_input):
        self.root = tk.Tk()
        self.root.title("Sdarot")
        self.root.geometry("350x190")

        # Series name
        self.series_var = tk.StringVar(self.root, value=series_input)
        tk.Label(self.root, text='Series Name', font=('calibre', 10, 'bold')).place(x=20, y=10, width=90, height=20)
        tk.Entry(self.root, textvariable=self.series_var, width=15).place(x=120, y=10, width=140, height=25)

        # Season
        self.season_var = tk.StringVar(self.root, value=season_input)
        tk.Label(self.root, text='Season No.', font=('calibre', 10, 'bold')).place(x=20, y=50, width=90, height=20)
        tk.Entry(self.root, textvariable=self.season_var, width=5).place(x=120, y=50, width=25, height=25)

        # Episode
        self.episode_var = tk.StringVar(self.root, value=episode_input)
        tk.Label(self.root, text='Episode', font=('calibre', 10, 'bold')).place(x=150, y=50, width=90, height=20)
        tk.Entry(self.root, textvariable=self.episode_var, width=5).place(x=230, y=50, width=25, height=25)

        # All episodes
        self.all_var = tk.BooleanVar()
        self.all_var.set(True)
        label_text = 'Download all episodes from the selected until the last?'
        tk.Checkbutton(self.root, text=label_text, variable=self.all_var).place(x=10, y=80, width=350, height=25)

        # Browse
        self.target_path = tk.StringVar(self.root, value=DEFAULT_TARGET_PATH)
        path_entry = tk.Entry(self.root, textvariable=self.target_path, width=30)
        path_entry.place(x=30, y=110, width=290, height=25)
        tk.Button(self.root, text="...", command=lambda: self.browse(path_entry)).place(x=320, y=110, width=20, height=25)

        # Run
        tk.Button(self.root, text='Run', command=self.submit).place(x=150, y=150, width=30, height=30)
        self.root.mainloop()

    def submit(self):
        self.root.destroy()

    def browse(self, path_entry):
        target_path = filedialog.askdirectory(initialdir=DEFAULT_TARGET_PATH)
        self.target_path = target_path
        path_entry.delete(0, len(path_entry.get()))
        path_entry.insert(0, target_path)
        dir_name = path_entry.get()
        print("Destination path is: " + dir_name)


def is_episode_available(full_url):
    attempts = 5
    ready = False
    while attempts > 0:
        browser.get(full_url)
        try:
            WebDriverWait(browser, 40).until(
                cond.element_to_be_clickable(("xpath", "//span[contains(.,'נגן את הפרק')]"))).click()
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


def get_episode(episode):
    time.sleep(2)
    video_src = browser.find_elements(By.TAG_NAME, "video")[0].get_attribute("src")
    if not video_src or video_src == "":
        print("Probably encountered an ad, will try again in 30 seconds when it will be finished")
        time.sleep(33)
        video_src = browser.find_elements(By.TAG_NAME, "video")[0].get_attribute("src")
    send_request(video_src, episode)


def send_request(video_src, episode):
    cookies = browser.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    head = s.head(video_src)
    file_size = int(head.headers["Content-Length"])
    response = s.get(video_src, stream=True)
    if response.status_code == 200:
        download(response, episode, file_size)
    else:
        print(f"Video url for episode {episode} is not accessible, skipping it")


def download(response, episode, file_size):
    print(f"Start downloading episode {episode}, it might take a while...")
    with tqdm.wrapattr(open(f'{dir_name}\\{episode}.mp4', 'wb'), "write",
                       miniters=1, desc=str(episode), total=file_size) as fout:
        for chunk in response:
            fout.write(chunk)
    print(f"Episode {episode} was downloaded successfully")


def start_browser():
    global browser
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    browser.get(BASE_URL)


def main(series_name, season_number, episode_number, all_episodes):
    if all_episodes:
        print(f"Selected all episodes in season {season_number}, starting of episode {episode_number}...")
    else:
        print("Selected single episode " + episode_number + "...")
    print("Destination path is: " + dir_name)
    query_search = "/search?term="
    series_url = BASE_URL + query_search + series_name
    browser.get(BASE_URL + query_search + series_name)
    series_url = browser.current_url.rstrip('/')
    full_url = series_url + '/season/' + season_number + '/episode/' + episode_number
    browser.get(full_url)
    # series_name = browser.find_element("xpath", "//span[@class='ltr']").text
    # series_name = series_name.replace(':', '-').replace('?', ' ').replace('\"', '\'')
    global dir_name
    dir_name = DEFAULT_TARGET_PATH + "\\" + series_name
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    episodes_list = browser.find_elements("xpath", "//ul[contains(@id,'episode')]/li")
    episode_number = int(episode_number)
    while episode_number <= len(episodes_list):
        full_url = series_url + '/season/' + str(season_number) + '/episode/' + str(episode_number)  # with the next episode
        episode_available = is_episode_available(full_url)
        if episode_available:
            get_episode(episode_number)
        else:
            print("Too many attempts without a success, stop downloading.")
            return
        if not all_episodes:
            break
        time.sleep(1)
        episode_number = episode_number + 1
        browser.execute_script("window.open('" + series_url + '/season/' + str(season_number) + "')")
        browser.switch_to.window(browser.window_handles[-1])

    print("Done! If no other active downloads, you may close the browser")


def login(username, password):
    print("Logging...")
    browser.implicitly_wait(5)
    WebDriverWait(browser, 10).until(cond.element_to_be_clickable(("xpath", "//button[@data-target='#loginForm']"))).click()
    browser.implicitly_wait(5)
    WebDriverWait(browser, 10).until(cond.element_to_be_clickable(("xpath", "//input[@name='username']"))).send_keys(username)
    browser.find_element("xpath", "//input[@name='password']").send_keys(password)
    browser.find_element("xpath", "//button[@name='submit_login']").click()
    print("Logged in successfully")


if __name__ == '__main__':
    # Init GUI Window
    app = StartWindow(sys.argv[1] if len(sys.argv) > 1 else "", "1", "1")

    # Set values from GUI
    series_output = app.series_var.get()
    season_output = app.season_var.get()
    episode_output = app.episode_var.get()
    get_all = app.all_var.get()

    start_browser()
    login(USERNAME, PASSWORD)
    main(series_output, season_output, episode_output, get_all)


