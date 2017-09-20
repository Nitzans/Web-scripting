# coding=utf-8
""" Fills google form automatically with random details.
    Note that Editing should be done according to the form structs (mostly in order of inputs and submit button) """

from selenium import webdriver
import time
import random
from faker import Faker

def name():
    names = [u"דן", u"תומר", u"דנה", u"רון", u"חן", u"יניב", u"מור", u"עדי", u"אופיר", u"ספיר", u"עדן", u"נעמה",
             u"מיכל", u"אביב", u"גיל", u"ניצן", u"דניאל", u"שרה", u"אבי", u"איתי", u"רונן", u"אור", u"שני", u"יובל",
             u"מאיר", u"רותם", u"אלון", u"שגיא", u"נתי"]
    return names[random.randint(0, len(names) - 1)]

def fname():
    fnames = [u"ישראלי", u"רוזנברג", u"ביטון", u"אשכנזי", u"מזרחי", u"חדד", u"שרון", u"עוז", u"כהן", u"לוי",
              u"ברגר", u"סגל", u"בראון", u"לייבוביץ'", u"מיכאלשווילי", u"אליאס", u"שמעוני", u"קליינשטיין", u"שטיין",
              u"רגב", u"רוזן"]
    return fnames[random.randint(0, len(fnames) - 1)]

def city():
    cities = [u"תל אביב", u"ירושלים", u"חיפה", u"באר שבע", u"אילת", u"מודיעין", u"אשדוד", u"אשקלון", u"קריית שמונה",
              u"נתניה", u"חדרה", u"רמת גן", u"נתניה", u"כפר סבא", u"הוד השרון", u"הרצליה", u"פתח תקווה", u"גבעתיים"]
    return cities[random.randint(0, len(cities) - 1)]

def age():
    return random.randint(21, 40)

def phone():
    return random.choice(["0504", "0520", "0545", "0573"]) + str(''.join(map(str, random.sample(xrange(0, 9), 6))))

def email():
    fake = Faker()
    return fake.email()

def money():
    return random.randrange(2000, 8000, 200)


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.get('https://docs.google.com/forms/d/e/1FAIpQLScZghfyFqyvu80S5U4YzyaXX-cnne-wV45RptRWaAL1i_qa0g/viewform')
time.sleep(1)  # Wait for whole page to be loaded

''' Text Input '''
textbox = browser.find_elements_by_xpath("//input[@type='text']")
textbox[0].send_keys("None")                    # free text
textbox[1].send_keys(money())                   # Money
textbox[2].send_keys(name() + " " + fname())    # name + family name
textbox[3].send_keys(age())                     # age
textbox[4].send_keys(city())                    # city
textbox[5].send_keys(phone())                   # phone

''' Choices '''
choices = browser.find_elements_by_xpath("//input[@type='radio']")
for c in choices:
    c.click()  # marks all last options

''' Submit '''
#submit = browser.find_elements_by_xpath("//div[@role='button']")[1].click()
#browser.close()

"""
browser.find_element_by_class_name("ss-q-radio").click()  # single choice
browser.find_element_by_class_name("ss-q-checkbox").click()  # multiply choice
value = browser.find_elements_by_xpath("//select/option[2]")[0].click()  # choose from list
"""
