# coding=utf-8
""" Auto-registration for courses """

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import ctypes  # popup window
import time

courseNum = "202.1.5061"
cDept = courseNum[0:3]
cDeg = courseNum[4]
cID = courseNum[6:10]

browser = webdriver.Chrome()
browser.maximize_window()
browser.get('https://bgu4u.bgu.ac.il/html/consulting.html')
main_frame = WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.XPATH, "//frame[@name='main']")))
browser.switch_to.frame(main_frame)
try:
    WebDriverWait(browser, 120).until(ec.presence_of_element_located((By.ID, "mainForm")))
except TimeoutException:
    print("Timed out waiting for page to load")

browser.find_elements_by_xpath("//input[@name='oc_username']")[0].send_keys("shpigeln")     # username
browser.find_elements_by_xpath("//input[@name='oc_password']")[0].send_keys("shpigeL5")     # password
browser.find_elements_by_xpath("//input[@name='rc_id']")[0].send_keys("305388746")          # ID
browser.find_elements_by_xpath("//a[@href='javascript:doit()']")[0].click()                 # send details
browser.find_elements_by_xpath("//img[@src='/images/images-login/button-sign.gif']")[0].click()  # enters searching page

# browser.find_elements_by_xpath("//input[@id='oc_course_name']")[0].send_keys(u"מערכות בסיס נתונים")
browser.find_elements_by_xpath("//input[@id='on_course_department']")[0].send_keys(cDept)   # search by department
browser.find_elements_by_xpath("//input[@id='on_course_degree_level']")[0].send_keys(cDeg)  # search by degree
browser.find_elements_by_xpath("//input[@id='on_course']")[0].send_keys(cID)                # search by course id
browser.find_elements_by_xpath("//img[@src='/images/images-search/icon-search.gif']")[0].click()  # search button
slots = browser.find_elements_by_xpath("//tr/td[@class='BlackText']")[2].text  # checks how many available slots

while int(slots) == 0:  # try to register till a slot is available
    '''
    browser.back()
    main_frame = WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.XPATH, "//frame[@name='main']")))
    browser.switch_to.frame(main_frame)
    cDeg, cID = "2", "4731"
    browser.find_elements_by_xpath("//input[@id='on_course_degree_level']")[0].clear()
    browser.find_elements_by_xpath("//input[@id='on_course_degree_level']")[0].send_keys(cDeg)  # search by degree
    browser.find_elements_by_xpath("//input[@id='on_course']")[0].clear()
    browser.find_elements_by_xpath("//input[@id='on_course']")[0].send_keys(cID)  # search by course id
    WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.XPATH, "//img[@src='/images/images-search/icon-search.gif']")))
    browser.find_elements_by_xpath("//img[@src='/images/images-search/icon-search.gif']")[0].click()  # search button
    WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.XPATH, "//tr/td[@class='BlackText']")))
    slots = browser.find_elements_by_xpath("//tr/td[@class='BlackText']")[2].text
    if int(slots) > 0:
        print("Found slots for IOT course")
        break
    time.sleep(0.5)
    '''
    browser.back()
    main_frame = WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.XPATH, "//frame[@name='main']")))
    browser.switch_to.frame(main_frame)
    '''
    cDeg, cID = "1", "5061"
    browser.find_elements_by_xpath("//input[@id='on_course_degree_level']")[0].clear()
    browser.find_elements_by_xpath("//input[@id='on_course_degree_level']")[0].send_keys(cDeg)  # search by degree
    browser.find_elements_by_xpath("//input[@id='on_course']")[0].clear()
    browser.find_elements_by_xpath("//input[@id='on_course']")[0].send_keys(cID)  # search by course id
    '''
    time.sleep(2)
    try:
        WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.XPATH, "//img[@src='/images/images-search/icon-search.gif']")))
        browser.find_elements_by_xpath("//img[@src='/images/images-search/icon-search.gif']")[0].click()  # search button
    except TimeoutException:
        print("Didn't find search button")
        browser.find_element_by_tag_name("body").send_keys(Keys.ALT + Keys.ARROW_LEFT)
        browser.find_elements_by_xpath("//img[@src='/images/images-search/icon-search.gif']")[0].click()  # search button
    time.sleep(2)
    try:
        WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.XPATH, "//tr/td[@class='BlackText']")))
        slots = browser.find_elements_by_xpath("//tr/td[@class='BlackText']")[2].text
    except TimeoutException:
        print("Didn't find available slots")
        browser.find_element_by_tag_name("body").send_keys(Keys.ALT+Keys.ARROW_LEFT)
    if int(slots) > 0:
        print("Found slots for DB course")
        break

browser.find_elements_by_xpath('//a[@href="javascript:setFormActionAndSubmitOfSearchList(\'' + cID + '\',\'0\',\'' + cDept + '\',\'' + cDeg + '\')"]')[0].click()
lecture = browser.find_elements_by_xpath("//input[@type='radio'][@name='mainSet']")  # mark lecture
for l in lecture:
    l.click()
# browser.find_elements_by_xpath("//input[@type='radio'][@name='Set1_2']")[0].click()  # mark practice
browser.find_elements_by_xpath('//img[@src="/images/icon-send.gif"]')[0].click()  # add course
print "YYYYEEEESSSSS!!!!!!!"
print time.asctime()
MessageBox = ctypes.windll.user32.MessageBoxA
MessageBox(None, 'Registration succeeded!', 'Success!!!!', 0)


