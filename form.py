# coding=utf-8
""" Fills google form automatically """

from selenium import webdriver
import time
import random

names = ["Dan", "Tomer", "Dana", "Ron", "Chen", "Yaniv", "Mor", "Adi", "Ofir", "Sapir", "Eden"]
fnames = ["Israeli", "Rozenberg", "Biton", "Ashkenazi", "Mizrahi", "Haddad", "Sharon", "Oz", "Cohen", "Levi", "Berger"]

browser = webdriver.Chrome()
""" Good example of form which use all abilities"""
browser.get('https://docs.google.com/forms/d/e/1FAIpQLSefsV3eQqDp7Cl0u9sM2j7H2WSFoS09Ns7oCF-h2cGGc2YyiQ/viewform?hl=en&formkey=dDliTk5XU1R4RUMtb2c1WDZxWHNENmc6MQ&fbzx=3205651701266619319#gid=0')
time.sleep(2)  # Wait for page to be loaded

browser.find_element_by_class_name("ss-q-short").send_keys(names[random.randint(0,10)])  # one line input
browser.find_element_by_class_name("ss-q-long").send_keys(fnames[random.randint(0,10)])  # text box input
browser.find_element_by_class_name("ss-q-checkbox").click()  # multiply choice
browser.find_element_by_class_name("ss-q-radio").click()  # single choice
value = browser.find_elements_by_xpath("//select/option[2]")[0].click()  # choose from list

boxes = browser.find_elements_by_xpath("//*[@role='radio']")
for i in range(0, len(boxes)-2):
    i = i + random.randint(0, 2)  # random choice, one of the 3 last options
    boxes[i].click()
"""
submit = browser.find_elements_by_xpath("//*[@type='submit']")
for s in submit:
     s.click()
"""


