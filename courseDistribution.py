# coding=utf-8
""" Getting statistics and distributions about any course """

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from tkinter import *
import time

def textbox(title, field1, field2, field3, opt):
    master = Tk()
    master.title(title)
    Label(master, text=field1).grid(row=0)
    Label(master, text=field2).grid(row=1)
    Label(master, text=field3).grid(row=2)
    var1 = Entry(master)
    var2 = Entry(master)
    var3 = Entry(master)
    var1.grid(row=0, column=1)
    var2.grid(row=1, column=1)
    var3.grid(row=2, column=1)
    if opt == 0:
        var2.config(show=u'\u2022')
        Button(master, text="Login", command=master.quit).grid(row=3, column=1, sticky=W, pady=4)
    elif opt == 1:
        var1.insert(10, "XXX.X.XXXX")
        var3.insert(1, "1, 2 or 3")
        Button(master, text="Apply", command=master.quit).grid(row=3, column=1, sticky=W, pady=4)
    mainloop()
    var1, var2, var3 = var1.get(), var2.get(), var3.get()
    master.destroy()
    return var1, var2, var3

logInfo = textbox("Login", "Username", "Password", "ID number", 0)
username, password, idNum = logInfo[0], logInfo[1], logInfo[2]

browser = webdriver.Chrome()
browser.get('https://bgu4u.bgu.ac.il/pls/apex/f?p=104:101:2258666703108:::::')
try:
    WebDriverWait(browser, 60).until(ec.presence_of_element_located((By.XPATH, "//form[@id='wwvFlowForm']")))
except TimeoutException:
    print "Timed out waiting for page to load"

browser.find_element_by_xpath("//input[@name='p_t01']").send_keys(username)     # username
browser.find_element_by_xpath("//input[@name='p_t02']").send_keys(password)     # password
browser.find_element_by_xpath("//input[@name='p_t03']").send_keys(idNum)        # ID
browser.find_element_by_xpath("//button[@id='P101_LOGIN']").click()
browser.find_element_by_xpath("//input[@value='מידע אקדמי']").click()
browser.find_elements_by_xpath("//ul[@id='tabs']/li")[2].click()
browser.find_elements_by_xpath("//ul[@class='largeLinkList']/li")[2].click()
time.sleep(1)
browser.find_element_by_xpath("//button[@id='P3_URL']").click()

go = True
while go:
    browser.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "w")
    coursInfo = textbox("Course info", "Course id", "year", "semester", 1)
    course, year, semester = coursInfo[0], coursInfo[1], coursInfo[2]
    courseDep = course[0:3]
    courseDeg = course[4]
    courseNum = course[6:]
    p_key = browser.page_source.split("p_key=")[1].split("/")[0]  # get the p_key which create only after first request
    browser.get('https://reports4u.bgu.ac.il/GeneratePDF.php?server=rep_aristo4stu4_FRHome1/report=SCRR016w/p_key='+p_key+'/p_year='+year+'/p_semester='+semester+'/out_institution=0/grade=5/list_department=*'+courseDep+'@/list_degree_level=*'+courseDeg+'@/list_course=*'+courseNum+'@/LIST_GROUP=*@/P_FOR_STUDENT=1')

    answer = raw_input("Do you want to check another course?")
    if answer.lower() not in ['yes', 'y', 'yeap']:
        go = False
    else:
        browser.back()
browser.close()
print "GoodBye!"
