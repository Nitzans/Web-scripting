
import os
import sys
import shutil
import logging
import requests
import zipfile
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
# import chromedriver_autoinstaller

def init_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.headless = False  # Console windows

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    chromedriver_dir = os.path.join(base_path, "driver")
    is_updated = check_chrome_version(chromedriver_dir)
    if not is_updated:
        return None

    driver_path = os.path.join(chromedriver_dir, 'chromedriver-win64', 'chromedriver.exe')
    if "PATH" not in os.environ:
        os.environ["PATH"] = chromedriver_dir
    elif chromedriver_dir not in os.environ["PATH"]:
        os.environ["PATH"] += ";" + chromedriver_dir

    try:
        print("Checking if driver need to be updated...")
        browser = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        # browser = webdriver.Chrome(ChromeDriverManager(get_latest_driver_version()).install(), options=chrome_options)
        # browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        # browser = webdriver.Chrome(service=chrome_path, options=chrome_options)  # use this with suitable version if updating from url was failed

        # A good way to update the driver, but it has a bug if Chrome is not installed in Program Files:
        # chromedriver_autoinstaller.install()
        # browser = webdriver.Chrome(options=chrome_options)
    except BaseException as e:
        logging.error("Failed to initialize browser, due to the following error: " + str(e))
        return None
    if browser is None:
        logging.error("Webdriver could not be initialized. Please update your chrome browser and your chrome driver to be the same version.")
        return None

    browser_version = browser.capabilities['browserVersion']
    driver_version = browser.capabilities['chrome']['chromedriverVersion'].split(" ")[0]
    logging.debug(f"Your chromedriver version is {driver_version}, and your browser version is {browser_version}. Everything is fine")
    return browser

def check_chrome_version(chrome_driver_path):
    browser_version = get_chrome_version()
    driver_version = get_version_from_driver(chrome_driver_path + "/chromedriver.exe")
    logging.info(f"Browser version: {browser_version}, driver version: {driver_version}")

    if browser_version is None:
        logging.info("Could not get browser version, possibly that google changed the version directory location (not your fault)."
                     "Process will continue anyway, but if browser and driver version aren't match you will get an error and then you have to run the python script instead")
        return True
    if driver_version is None:
        logging.warning("Driver wasn't found, probably because you are running this script as standalone executable. "
                     "Process will continue anyway, but if browser version doesn't match the driver you will get an error and then you have to run the python script instead")
        return True
    if int(browser_version.split('.')[0]) < int(driver_version.split('.')[0]):
        logging.warning("Chrome browser is too old. It is recommended to update the browser or downgrade the driver and then try again")
        return False
    elif int(browser_version.split('.')[0]) > int(driver_version.split('.')[0]):
        logging.info("Chrome drive isn't updated, trying to update...")
        if not update_chromedriver(chrome_driver_path):
            logging.error("Updating chrome driver failed, please update manually by replacing 'chromedriver' file with the latest version from here: https://chromedriver.chromium.org/downloads")
            return False
        logging.info("chrome driver has successfully updated")
    else:
        logging.debug("Browser and driver version matches, no need to update")
    return True


def get_chrome_version():
    paths = [r"C:\Program Files\Google\Chrome\Application",
             r"C:\Program Files (x86)\Google\Chrome\Application"]
    browser_version = list(filter(None, [get_version_from_folder_name(p) for p in paths]))
    if len(browser_version) == 0:
        logging.error("Could not find where chrome browser installed or find its version directory")
        return None
    return browser_version[0]


def get_version_from_folder_name(chrome_folder):
    try:
        list_of_files = os.listdir(chrome_folder)
        current_version = sorted(list_of_files)[0]
    except Exception:
        return None
    return current_version


def get_version_from_driver(path):
    if not os.path.exists(path):
        logging.warning("chromedriver.exe could be found in local folder, unable to get its version")
        return None
    p = subprocess.Popen(f"{path} --version", shell=True, stdout=subprocess.PIPE)
    stream = p.stdout.read()
    version = stream.split(b' ')[1]
    return version.decode("utf-8")


def get_latest_driver_version():
    get_latest_ver = requests.get("https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE")
    if get_latest_ver and len(get_latest_ver.text) > 3:
        logging.error(f"Latest driver version available online: {get_latest_ver.text}")
        return get_latest_ver.text
    else:
        logging.error("Failed to get latest version")
        return False


def update_chromedriver(driver_dir):
    newest_version = get_latest_driver_version()
    if not os.path.exists(driver_dir):
        os.mkdir(driver_dir)
    download_link = f"https://storage.googleapis.com/chrome-for-testing-public/{newest_version}/win64/chromedriver-win64.zip"
    req = requests.get(download_link)
    zip_path = os.path.join(driver_dir, "chromedriver.zip")
    try:
        with open(zip_path, "wb") as zip_file:
            zip_file.write(req.content)
    except IOError as e:
        logging.error("Failed to create zip file - {}. Make sure you have the 'driver' folder".format(e))
    unzip_content(driver_dir, zip_path)
    write_driver_info(driver_dir, newest_version)
    return True

def unzip_content(driver_dir, zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(driver_dir)
        os.unlink(zip_path)
    except PermissionError as e:
        logging.error("Failed to extract the chromedriver zip, make sure you are running as administrator - {}".format(e))
        os.unlink(zip_path)
        return False
    except BaseException as e:
        logging.error("Failed to extract zip file or deleting it, make sure the file isn't being used by another program - {}".format(e))
        return False
    extracted_dir = [name for name in os.listdir(driver_dir) if os.path.isdir(os.path.join(driver_dir, name)) and name.startswith("chromedriver")].pop()
    shutil.copy2(os.path.join(driver_dir, extracted_dir, 'chromedriver.exe'), driver_dir)


def write_driver_info(driver_dir, newest_version):
    # Writing text file with driver's information
    try:
        driver_dir_content = os.listdir(driver_dir)
        for item in driver_dir_content:
            if item.endswith(".txt"):
                os.remove(os.path.join(driver_dir, item))
        with open(os.path.join(driver_dir, "chormedriver-" + newest_version + ".txt"), 'w') as ver_info:
            ver_info.write("Chromedriver version is: {} \nUpdated in {}".format(newest_version, datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
    except IOError as e:
        logging.error("Failed to write into chrome version info file. {} - Not so bad :)".format(e))