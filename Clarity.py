import os
import subprocess
import time
import sys
import logging
import easygui
import tkinter as tk
from datetime import datetime
import requests
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = None


''' GUI for the login details'''
class LoginWindow:
    def __init__(self, user, code1, task):
        self.root = tk.Tk()
        self.root.title("Philips Login")
        self.root.geometry("320x180")
        self.name_var = tk.StringVar(self.root, value=user)
        self.pass_var = tk.StringVar(self.root, value=code1)
        self.task_var = tk.StringVar(self.root, value=task)
        self.days = [tk.StringVar(self.root, value="8.4"), tk.StringVar(self.root, value="8.4"), tk.StringVar(self.root, value="8.4"), tk.StringVar(self.root, value="8.4"), tk.StringVar(self.root, value="8.4")]

        tk.Label(self.root, text='Username', font=('calibre', 10, 'bold')).grid(row=0, column=0)
        tk.Label(self.root, text='Code1', font=('calibre', 10, 'bold')).grid(row=1, column=0)
        tk.Label(self.root, text='Task', font=('calibre', 10, 'bold')).grid(row=2, column=0)
        tk.Label(self.root, text='Mon', font=('calibre', 10)).place(relx=0.25, y=100)
        tk.Label(self.root, text='Tue', font=('calibre', 10)).place(relx=0.4, y=100)
        tk.Label(self.root, text='Wed', font=('calibre', 10)).place(relx=0.55, y=100)
        tk.Label(self.root, text='Thu', font=('calibre', 10)).place(relx=0.7, y=100)
        tk.Label(self.root, text='Sun', font=('calibre', 10)).place(relx=0.85, y=100)

        self.name_entry = tk.Entry(self.root, textvariable=self.name_var, font=('calibre', 10, 'normal'), width=30)
        self.pass_entry = tk.Entry(self.root, textvariable=self.pass_var, show="\u2022", font=('calibre', 10, 'normal'), width=30)
        self.task_entry = tk.Entry(self.root, textvariable=self.task_var, font=('calibre', 10, 'normal'), width=30)

        self.entry_days = \
            [tk.Entry(self.root, font=('calibre', 10, 'normal'), width=3, textvariable=self.days[0]),
             tk.Entry(self.root, font=('calibre', 10, 'normal'), width=3, textvariable=self.days[1]),
             tk.Entry(self.root, font=('calibre', 10, 'normal'), width=3, textvariable=self.days[2]),
             tk.Entry(self.root, font=('calibre', 10, 'normal'), width=3, textvariable=self.days[3]),
             tk.Entry(self.root, font=('calibre', 10, 'normal'), width=3, textvariable=self.days[4])]
        login_btn = tk.Button(self.root, text='Login', command=self.submit)
        relx = 0.25
        for d in self.entry_days:
            d.place(relx=relx, y=120)
            relx += 0.15

        self.name_entry.grid(row=0, column=1)
        self.pass_entry.grid(row=1, column=1)
        self.task_entry.grid(row=2, column=1)

        login_btn.grid(row=4, column=1)
        self.root.mainloop()

    # update the values from box to their variables
    def submit(self):
        self.name_var.set(self.name_entry.get())
        self.pass_var.set(self.pass_entry.get())
        self.task_var.set(self.task_entry.get())
        for day, entry_day in zip(self.days, self.entry_days):
            day.set(entry_day.get())
        self.root.destroy()


''' GUI for the choose task menu '''
class TasksWindow:
    def __init__(self, tasks):
        self.root = tk.Tk()
        self.selection, self.chosen_task = "", ""
        self.root.title("Available tasks")
        self.root.geometry("250x{}".format(str(40 * len(tasks))))

        self.var = tk.StringVar(value="None")
        task_obj = []

        for index, name in enumerate(tasks):
            radio = tk.Radiobutton(self.root, text=name, variable=self.var, value=name, command=self.apply)
            task_obj.append(radio)
            radio.grid(row=index, column=0, sticky=tk.W)

        login_btn = tk.Button(self.root, text='Confirm', command=self.submit)
        login_btn.grid(row=len(tasks)+1, column=0)

        self.root.mainloop()

    def apply(self):
        self.selection = self.var.get()

    # update the values from box to their variables
    def submit(self):
        self.chosen_task = self.selection
        self.root.destroy()


''' Install modules for running the script '''
class SetupModules(object):
    def __init__(self):
        missing_modules = check_missing()
        for mod in missing_modules:
            print("Module {} is missing. Installing...".format(mod))
            self.install_and_import(mod)

    @staticmethod
    def install_and_import(package):
        import importlib
        need_import = False
        try:
            importlib.import_module(package)
        except ImportError:
            need_import = True

        if need_import:
            need_import = False
            import pip
            pip.main(['install', package])

        try:
            importlib.import_module(package)
        except ImportError:
            need_import = True

        if need_import:
            print("install " + package + " FAILED, make sure you are running as administrator")
            exit()
        globals()[package] = importlib.import_module(package)


def check_missing():
    """ Check for missing modules """
    import pkg_resources
    required = {'selenium', 'requests', 'tkinter', 'easygui', 'zipfile'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    return required - installed


def login(user_email, password):
    # Fill Microsoft email
    try:
        WebDriverWait(browser, 180).until(EC.presence_of_element_located((By.ID, 'idSIButton9')))
    except TimeoutException:
        logging.error("Timeout error: Microsoft login page wasn't loaded for too much time")
        return False
    submit_next = browser.find_element(by=By.XPATH, value="//*[@id='i0116']")
    submit_next.send_keys(user_email)
    submit_next.send_keys(Keys.ENTER)

    # Fill Microsoft Code1
    try:
        WebDriverWait(browser, 180).until(EC.presence_of_element_located((By.ID, 'idSIButton9')))
    except TimeoutException:
        logging.error("Timeout error: Microsoft password page wasn't loaded for too much time")
        return False

    pass_label = browser.find_element(by=By.XPATH, value="//*[@id='i0118']")
    pass_label.send_keys(password)
    time.sleep(2)  # This delay is because sometimes the sign button takes time to be visible
    sign = browser.find_element(by=By.XPATH, value="//input[@type='submit']")
    time.sleep(1)
    if not sign.is_displayed():
        logging.error("Sign button is not displayable. Probably didn't wait enough time before clicking.")
        return False
    sign.send_keys(Keys.ENTER)

    # Wait for main screen after login
    try:
        WebDriverWait(browser, 300).until(EC.presence_of_element_located((By.ID, 'timeadmin.editTimesheet')))
        logging.info("{} logged in successfully!".format(user_email))
    except TimeoutException:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "Session timed out! please re-run the script", "Timeout", 1)
        logging.error("Timeout error: Didn't receive login details for too much time!")
        browser.close()
        return False
    

def fill_task(task_name, work_days):
    logging.info("Start filling task " + task_name)
    # Click edit timesheet
    browser.find_element(by=By.XPATH, value="//*[@id='timeadmin.editTimesheet']").click()
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@id='ppm-portlet-grid-content-timeadmin.editTimesheet']/div/button")))
    except TimeoutException:
        logging.error("Didn't find 'edit timesheet' button")
        return False
    browser.find_element(by=By.XPATH, value="//*[@id='ppm-portlet-grid-content-timeadmin.editTimesheet']/div/button").click()

    # Find relevant task from list
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, "//tbody[@class='ppm_grid_content']/tr/td")))
        logging.debug("Tasks list is ready!")
    except TimeoutException:
        logging.error("Didn't find add task button")
        return False
    all_tasks = browser.find_elements(by=By.XPATH, value="//tbody[@class='ppm_grid_content']/tr")
    task_mapping = {}
    for task_item in all_tasks:
        task_mapping[task_item.find_elements_by_tag_name("td")[3].text] = task_item.find_elements_by_tag_name("td")
    logging.info("{} available tasks were found:\n\t -{}".format(len(task_mapping), "\n\t- ".join(list(task_mapping.keys()))))
    if task_name in task_mapping:
        task_mapping[task_name][0].click()
    else:  # task didn't found in list, user may choose another
        available_tasks = list(task_mapping.keys())
        logging.warning("Task {} didn't found in the tasks list, please select again among the following: {}".format(task_name, available_tasks))
        new_task = TasksWindow(available_tasks)
        logging.info("You selected task: {}".format(new_task.chosen_task))
        task_mapping[new_task.chosen_task][0].click()
    # Select the task
    browser.find_element(by=By.XPATH, value="//*[@id='ppm-portlet-grid-content-timeadmin.selectTimesheetTask']/div/button[1]").click()

    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, "portlet-table-timeadmin.editTimesheet")))
    except TimeoutException:
        logging.error("Didn't find task table")
        return False

    # Fill hours
    days_div = browser.find_elements(by=By.XPATH, value="//tbody[@class='ppm_list_content']/tr[2]/td/input[@type='text'][@class='ppm_field formFieldNoWidth']")[:-2]  # remove the total days column
    for d in days_div:
        day_name = d.get_attribute("title")[:3]
        if day_name in work_days:
            d.send_keys(work_days[day_name])
            logging.debug("Filled {} with {} hours".format(day_name, work_days[day_name]))
        else:
            d.send_keys("")  # If you reached here it means the title format was changed

    browser.find_elements(by=By.XPATH, value="//*/button[@class='ppm_button button']")[0].click()  # Save
    logging.debug("Task was saved")
    time.sleep(3)
    browser.find_elements(by=By.XPATH, value="//*/button[@class='ppm_button button']")[1].click()  # Submit
    logging.debug("Task was submitted")

    # Verify completion and return to home page
    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, "ppm-portlet-grid-content-timeadmin.timesheetBrowser")))
    except TimeoutException:
        logging.error("Task {} did not submitted successfully".format(task_name))
        return False
    logging.info("Task {} was submitted successfully".format(task_name))

    browser.find_element(by=By.XPATH, value="//button[@id='ppm_home_go']").click()  # go to home page
    return True


def check_chrome_version(chrome_driver_path):
    browser_version = get_chrome_version()
    driver_version = get_version_from_driver(chrome_driver_path + "/chromedriver.exe")
    logging.info(f"Browser version: {browser_version}, driver version: {driver_version}")
    if browser_version is None:
        logging.info("Could not get browser version, possibly that google changed the version directory location (not your fault)."
                     "Process will continue anyway, but if browser and driver version aren't match you will get an error and then you have to run the python script instead")
        return True
    if driver_version is None:
        logging.info("driver wasn't found, probably because you are running the executable. "
                     "Process will continue anyway, but if browser version isn't match the driver you will get an error and then you have to run the python script instead")
        return True
    if int(browser_version.split('.')[0]) < int(driver_version.split('.')[0]):
        logging.warning("chrome browser is too old. It is recommended to update the browser or downgrade the driver")
        return False
    elif int(browser_version.split('.')[0]) > int(driver_version.split('.')[0]):
        logging.debug("chrome drive isn't updated, trying to update...")
        if not update_chromedriver(chrome_driver_path):
            logging.error("Updating chrome driver failed, please update manually by replacing 'chromedriver' file with the latest version from here: https://chromedriver.chromium.org/downloads")
            return False
        logging.debug("chrome driver has successfully updated")
    else:
        logging.debug("Version matches")
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


def update_chromedriver(driver_dir):
    chrome_url = "https://chromedriver.storage.googleapis.com"
    get_latest_ver = requests.get(chrome_url + "/LATEST_RELEASE")
    if get_latest_ver:
        newest_version = get_latest_ver.text
    else:
        logging.error("Failed to get latest version")
        return False
    if not os.path.exists(driver_dir):
        os.mkdir(driver_dir)
    zip_path = driver_dir + "/chromedriver.zip"
    download_link = "{}/{}/chromedriver_win32.zip".format(chrome_url, newest_version)
    req = requests.get(download_link)
    try:
        with open(zip_path, "wb") as zip_file:
            zip_file.write(req.content)
    except IOError as e:
        logging.error("Failed to create zip file - {}. Make sure you have the 'driver' folder".format(e))
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
    try:
        driver_dir_content = os.listdir(driver_dir)
        for item in driver_dir_content:
            if item.endswith(".txt"):
                os.remove(os.path.join(driver_dir, item))
        with open(driver_dir + "\\chormedriver-" + newest_version + ".txt", 'w') as ver_info:
            ver_info.write("Chromedriver version is: {} \nUpdated in {}".format(newest_version, datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
    except IOError as e:
        logging.error("Failed to write into chrome version info file. {} - Not so bad :)".format(e))
    return True


def set_logger():
    logging.basicConfig(
        filename='fill_clarity.log',
        format='%(asctime)s \t [%(levelname)s] %(lineno)s:%(funcName)s\t %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] %(lineno)s:%(funcName)s\t %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)


def main(user_email, password, task_name, work_days):
    logging.info("Start running with the following arguments:\nTask name={}, Username={}, days={}".format(task_name, user_email, work_days))
    chrome_options = Options()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.headless = False  # Console windows
    global browser
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    is_updated = check_chrome_version(base_path + "/driver")
    if not is_updated:
        return False
    chrome_path = os.path.join(base_path, 'driver/chromedriver.exe')
    """
    try:
        print("Checking if driver need to be updated...")
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except BaseException as e:
        logging.error("Failed to initialize browser, due to the following error: " + str(e))
    if browser is None:
        logging.error("Webdriver could not be initialized. Please update your chrome browser and your chrome driver to be the same version.\n"
                      "chromedriver can be downloaded from web or by running this script in its python version with '--update' argument. chromedrive is located in: " + str(chrome_path))
        return

    browser_version = browser.capabilities['browserVersion']
    driver_version = browser.capabilities['chrome']['chromedriverVersion'].split(" ")[0]
    logging.debug("Your chromedriver version is {}, and your browser version is {}. Everything is fine".format(driver_version, browser_version))

    browser.get("https://www.clarity.philips.com/niku/nu")
    login(user_email, password)
    """
    keep_alive_code = r'function keepAlive() {    ' \
                      r'    var httpRequest = new XMLHttpRequest();    ' \
                      r'    console.log("KeepAlive");    ' \
                      r'    httpRequest.open("GET", "/niku/nu");    ' \
                      r'    httpRequest.send(null);' \
                      r'}' \
                      r'setInterval(keepAlive, 600000);'
    browser.execute_script(keep_alive_code)
    """

    status = fill_task(task_name, work_days)
    if not status:
        logging.error("Failed to fill task {}.\nYou may continue the procedure manually or fix the command and run it again".format(task_name))
        return
    logging.info("Task was completed on {}\nYou may close the browser now.".format(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
    easygui.msgbox("Task was submitted successfully!", title="Success")
    return


if __name__ == "__main__":
    set_logger()
    arg_user, arg_task, arg_pass = "", "", ""
    arguments = [i for i in sys.argv]
    if "--update" in arguments:
        arguments.remove("--update")  # Update argumnet is deprecated
    if len(arguments) >= 4:
        arg_user = arguments[1]
        arg_pass = arguments[2]
        arg_task = arguments[3]
    elif len(arguments) >= 3:
        arg_user = arguments[1]
        arg_pass = arguments[2]
    elif len(arguments) >= 2:
        arg_user = arguments[1]

    app = LoginWindow(arg_user, arg_pass, arg_task)
    user = app.name_var.get()
    password = app.pass_var.get()
    task = app.task_var.get()
    days_list = [d.get() for d in app.days]
    days = {"Mon": days_list[0], "Tue": days_list[1], "Wed": days_list[2], "Thu": days_list[3], "Sun": days_list[4]}

    main(user, password, task, days)
