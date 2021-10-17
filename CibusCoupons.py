import traceback
from webbot import Browser
from time import sleep
from tkinter import messagebox


PLACE_NAME = 'ויקטורי - רמת גן'
COUPON_VALUE = 30
DAILY_BUDGET = 30
USER_NAME = 'nitzan.shpigel@philips.com'
PASSWORD = 'Nizans1!'

web = Browser(True)  # When false - browser window will be hidden

''' Login '''
try:
    web.go_to("https://www.mysodexo.co.il/")
    web.type(USER_NAME, into='שם משתמש')
    web.type(PASSWORD, into='סיסמה')
    web.click('כניסה', tag='span')
    print("Logged in")
    sleep(1)
except BaseException:
    print("Failed to login")
    messagebox.showinfo("Failure", "Failed to login")
    exit(1)

''' Check budget '''
budget = web.find_elements(f'{str(DAILY_BUDGET)}.00', tag='span')
if len(budget) == 0:
    print(f"Budget of {DAILY_BUDGET} could not be found. Are you sure you have enough money")
    messagebox.showinfo("Abort", "Not enough money")
    exit(1)
print("Yeah, enough money")

''' Find restaurant '''
try:
    web.click('איסוף ממסעדה', tag='span')
    web.type(PLACE_NAME, id='ctl00_cphMain_right_bar_txtSearchRest')
    web.type(web.Key.ENTER)
    sleep(3)
    # Sometimes, this search opens a pop-up, so we need to return the original tab
    if web.get_total_tabs() > 1:
        web.switch_to_tab(1)
    web.click(PLACE_NAME, tag='th', classname='ellipsis')

    ''' Complete order '''
    web.click(f'₪{COUPON_VALUE}', tag='big')
    web.find_elements(tag='a', classname='submit')[0].click()
    sleep(2)
    web.find_elements('אישור ההזמנה', tag='a', classname='send')[0].click()
except BaseException:
    messagebox.showinfo("Failure", "Unknown reason caused the script to fail.\n"
                                   "One-time errors might occur so it is recommended to try again.")
    traceback.print_exc()
    exit(1)

''' Finishing '''
print("Finished!")
messagebox.showinfo("Success", "Check email to verify the charge was done")
sleep(7)
web.driver.quit()
