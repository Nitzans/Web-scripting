# coding=utf-8
""" Getting information about courses at Ben-Gurion university """

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# dept = input("Choose Department: \n")
browser = webdriver.Chrome()
browser.get('https://bgu4u.bgu.ac.il/pls/scwp/!app.gate?app=ann')
time.sleep(1)  # Wait for page to be loaded

browser.switch_to.frame(0)
browser.find_elements_by_xpath("//a[@href='javascript:goType(1)']")[0].click()
# browser.switch_to_frame(0)

find_course = browser.find_elements_by_xpath("//input[@id='on_course_department']")[0]
find_course.clear()
find_course.send_keys("205")
browser.find_elements_by_xpath("//input[@id='GOPAGE2']")[0].click()

course_list = browser.find_elements_by_xpath("//td[@class='SearchFormTextBold']/a")
counter = 0
for i in range(0, len(course_list)):
    course_list[i].click()
    source = browser.page_source
    if u"מדעי המחשב" in source:
        counter += 1
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  Course Number: " + str(counter) + "  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        info = browser.find_element_by_xpath("//ul[@class='props']")
        category = info.find_elements_by_xpath("//p[@class='key']")
        values = info.find_elements_by_xpath("//p[@class='val']")
        for j in range(0, len(values)):
            print "*" + str(category[j].text.encode('utf-8')) + str(values[j].text.encode('utf-8'))
        print "\n"
    browser.find_elements_by_xpath("//img[@name='buttonBack']")[0].click()  # go back
    course_list = browser.find_elements_by_xpath("//td[@class='SearchFormTextBold']/a")  # restore list
