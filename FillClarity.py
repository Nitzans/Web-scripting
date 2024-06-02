import time
import sys
import logging
import easygui
import tkinter as tk
from datetime import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import DriverInfrastructure

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
        missing_modules = self.check_missing()
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

    @staticmethod
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
    time.sleep(1)  # This delay is because sometimes the sign button takes time to be visible
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
    open_timesheet = browser.find_elements(by=By.XPATH, value="//*[@id='timeadmin.editTimesheet']")
    open_timesheet[0].click()  # Fill oldest timesheet first
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
        task_name = task_item.find_elements(By.TAG_NAME, "td")[3].text
        task_mapping[task_name] = task_item.find_elements(By.TAG_NAME, "td")[0]
    logging.info("{} available tasks were found:\n\t -{}".format(len(task_mapping), "\n\t- ".join(list(task_mapping.keys()))))
    if task_name in task_mapping:
        task_mapping[task_name].click()
    else:  # task didn't find in list, user may choose another
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
    global browser
    browser = DriverInfrastructure.init_driver()
    if browser is None:
        return

    browser.get("https://www.clarity.philips.com/niku/nu")
    login(user_email, password)
    status = fill_task(task_name, work_days)
    if not status:
        logging.error("Failed to fill task {}.\nYou may continue the procedure manually or fix the command and run it again".format(task_name))
        return
    easygui.msgbox("Task was submitted successfully!", title="Success")
    logging.info("Task was completed on {}\nYou may close the browser now.".format(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
    input("Press any key to close...")
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
