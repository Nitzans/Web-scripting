""" Prints search results from Google """

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

browser = webdriver.Chrome()
browser.get('https://www.google.com')
assert 'Google' in browser.title

string ="Wikipedia"
element = browser.find_element_by_name('q')  # Find the search box
element.send_keys(string + Keys.RETURN)  # Type the string and press Enter

time.sleep(1)  # Wait for results to be load

page_results = browser.find_elements(By.XPATH, "//div/h3/a")  # Find all elements with those tags

for link in page_results:
    print (link.text)
    print (link.get_attribute("href"))  # The link inside 'a' is 'href'
    print ("\n")

browser.quit()
