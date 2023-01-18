import json
import random
import time
from datetime import datetime

import webbrowser

import requests
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from helper import *
from PIL import ImageTk, Image
from twocaptcha import TwoCaptcha

UTORID = ""
PASSWORD = ""

TARGET_COURSE_CODE = ""  # example for CSC108 in UTSG: "CSC108H1"
TARGET_SESSION_CODE = "20231"  # example for 2022 Summer: "20225", options are "yyyym" where m can be one of 1, 5, 9
TARGET_SECTION_CODE = ""  # example for Full Session: "Y", options are "Y", "F", "S"

# Extension
TARGET_COURSE_SECTION = ""
MODIFY_TUT_MODE = False
TARGET_TUT_SECTION_CODES = []  # TUT ["1001", "1002"]
API_2CAPTCHA = ""
SOLVER_2CAPTCHA: TwoCaptcha = None

ERRNO = -1
WAIT_TIME = 5  # Tune the value as needed to bypass hCaptcha
ACORN_URL = "https://acorn.utoronto.ca/sws/#/"
COURSE_URL = "https://acorn.utoronto.ca/sws/rest/enrolment/course/view?courseCode={courseCode}&courseSessionCode={sessionCode}&postCode=ASCRSHBSC&sectionCode={sectionCode}&sessionCode={sessionCode}"
COURSE_SESSION_URL = "https://acorn.utoronto.ca/sws/#/courses/{index}"
hCaptcha_URL = "https://acorn.utoronto.ca/sws/#/captcha"
ENROLL_STATUS = False
RETRY_TIME = 5

driver: uc.Chrome = None
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")


def login():
    driver.get(ACORN_URL)
    print("Logging in...")

    # Input utorid
    utorid = driver.find_element(by=By.ID, value="username")
    utorid.send_keys(UTORID)
    time.sleep(random.randint(1, 2))

    # Input password
    utorid = driver.find_element(by=By.ID, value="password")
    utorid.send_keys(PASSWORD)
    time.sleep(random.randint(1, 2))

    # Submit
    login_btn = driver.find_element(by=By.NAME, value="_eventId_proceed")
    login_btn.click()
    time.sleep(random.randint(1, 2))

    # Check login status
    Wait(driver, 10).until(AnyEc(
        EC.url_to_be(ACORN_URL),
        EC.url_to_be(hCaptcha_URL)
    ))

    if driver.current_url == hCaptcha_URL:
        bypass_hCaptcha()
        Wait(driver, 600).until(EC.url_to_be(ACORN_URL))
        driver.minimize_window()
        print("Bypass SUCCESS!")
    else:
        Wait(driver, 10).until(EC.url_to_be(ACORN_URL))
        print("Login SUCCESS!\n")


def bypass_hCaptcha():
    if SOLVER_2CAPTCHA is None:
        print("Waiting manually bypass hCaptcha...")
        driver.switch_to.window(driver.current_window_handle)
    else:
        Wait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        site_key_element = driver.find_element(By.TAG_NAME, "iframe")
        site_src = site_key_element.get_attribute("src")
        start_idx = site_src.index('sitekey=') + 8
        end_idx = site_src.index('&theme')
        site_key = site_src[start_idx:end_idx]
        print('Solving ' + site_key)

        result = SOLVER_2CAPTCHA.hcaptcha(
            sitekey=site_key,
            url='https://acorn.utoronto.ca/sws/#/captcha'
        )
        print('Captcha solved!')
        cookies = driver.get_cookies()
        s = requests.Session()
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        # submit
        hcaptcha_response = driver.find_element(By.CSS_SELECTOR, value="[data-hcaptcha-response]")
        driver.execute_script(f"arguments[0].setAttribute('data-hcaptcha-response', '{result['code']}');", hcaptcha_response)
        response = driver.find_element(By.NAME, value="g-recaptcha-response")
        response.submit()
        submit_btn = driver.find_element(By.XPATH, value="//button[@class='btn btn-primary']")
        submit_btn.click()
        driver.get(ACORN_URL)


def enroll_modify(sectionNo):
    # find tab
    type = "LEC" if not MODIFY_TUT_MODE else "TUT"
    course_session_url = COURSE_SESSION_URL.format(index=0)  # Currently, have Fall/Winter and Summer session tabs
    driver.get(course_session_url)
    search = Wait(driver, 10).until(EC.element_to_be_clickable((By.ID, "typeaheadInput")))
    search.send_keys(TARGET_COURSE_CODE)
    time.sleep(random.randint(1, 3))

    # find course
    course_span = driver.find_element(By.XPATH,
                                      value=f"//span[contains(text(), '{TARGET_COURSE_CODE} {TARGET_SECTION_CODE}')]")
    course_span.click()
    time.sleep(random.randint(1, 3))

    # choose section
    course_section = driver.find_element(By.ID, value=f"course{type}{sectionNo}")
    course_section.click()

    # modify_enrol
    modify_enrol_btn = driver.find_element(By.ID, value="enrol" if not MODIFY_TUT_MODE else "modify")
    modify_enrol_btn.click()
    time.sleep(random.randint(2, 4))

    # check enrollment
    try:
        driver.find_element(By.ID, f"{TARGET_COURSE_CODE}-courseBox")
        global ENROLL_STATUS
        ENROLL_STATUS = True
        print("Enrollment SUCCESS!")
        messagebox.showinfo("Donation", "Buy me a coffee https://ko-fi.com/svision")
    except selenium.common.exceptions.NoSuchElementException:
        print("Enroll failed, retrying...")


def get_course_info():
    course_url = COURSE_URL.format(courseCode=TARGET_COURSE_CODE, sectionCode=TARGET_SECTION_CODE,
                                   sessionCode=TARGET_SESSION_CODE)
    driver.get(course_url)
    Wait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
    content = driver.find_element(By.TAG_NAME, value="pre").text
    data = json.loads(content)

    errors = data["messages"]["errors"]
    if errors:
        print("Error getting course info")
        exit(-1)

    print(f"\n{datetime.today()}")
    print("----------------------------")
    meetings = data["responseObject"]["meetings"]
    for meeting in meetings:
        teachMethod = meeting["teachMethod"]
        space_available = meeting["enrollmentSpaceAvailable"]
        total_space = meeting["totalSpace"]
        sectionNo = meeting["sectionNo"]
        display_name = meeting["displayName"]
        if (not MODIFY_TUT_MODE and teachMethod == "LEC") or (
                teachMethod == "TUT" and sectionNo in TARGET_TUT_SECTION_CODES):
            if space_available != 0:
                print(
                    f"{TARGET_COURSE_CODE} has {space_available} spaces left (total: {total_space}) for {display_name}")
                enroll_modify(sectionNo)
                if ENROLL_STATUS is True:
                    return
            else:
                print(f"{TARGET_COURSE_CODE} has no space left for {display_name}")


def submit():
    global ERRNO
    global RETRY_TIME
    global UTORID
    UTORID = fields['utorid'].get()
    global PASSWORD
    PASSWORD = fields['password'].get()
    if UTORID == "" or PASSWORD == "":
        messagebox.showerror("Auth Error", "Both utorid and password cannot be empty")
        return
    if MODIFY_TUT_MODE:
        global TARGET_TUT_SECTION_CODES
        TARGET_TUT_SECTION_CODES = fields['tut'].get().split(',')

    global WAIT_TIME
    if not fields['wait_time'].get().isnumeric() and int(fields['wait_time'].get()) <= 0:
        messagebox.showerror("Wait Time Error", "Wait time must be a number greater than 0")
        return
    WAIT_TIME = int(fields['wait_time'].get())
    global TARGET_COURSE_CODE
    TARGET_COURSE_CODE = fields['course_code'].get()
    if not len(TARGET_COURSE_CODE) == 8:
        messagebox.showerror("Course Code Error", "Example course code for CSC108 in UTSG: \n\nCSC108H1")
        return
    global TARGET_SECTION_CODE
    TARGET_SECTION_CODE = selected_section.get()

    # 2Captcha
    global API_2CAPTCHA
    global SOLVER_2CAPTCHA
    API_2CAPTCHA = fields['2captcha'].get()
    if API_2CAPTCHA != "":
        SOLVER_2CAPTCHA = TwoCaptcha(API_2CAPTCHA)
        print("Solver created!")

    try:
        global driver
        driver = uc.Chrome(chrome_options=chrome_options)

        login()

        print(f"Checking {TARGET_COURSE_CODE} for {TARGET_SESSION_CODE}...")
        while True:
            get_course_info()
            if ENROLL_STATUS is True:
                window.destroy()
                driver.quit()
                exit(0)
            time.sleep(WAIT_TIME)
    except Exception as e:
        if str(e) == "ERROR_WRONG_USER_KEY":
            print("API Key error")
            API_2CAPTCHA = ""
        if RETRY_TIME > 0:
            print(str(e))
            print("Retrying...")
            RETRY_TIME -= 1
            submit()
        else:
            print(str(e))
            exit(1)


def donation():
    webbrowser.open("https://ko-fi.com/svision")


if __name__ == "__main__":
    window = Tk()
    window.title("Acron Enrollment Helper")
    try:
        img = ImageTk.PhotoImage(Image.open("U-of-T-logo.png"))
        logo = Label(window, image=img)
        logo.pack()
    except:
        window.geometry('240x550')

    fields = {}
    fields['utorid_label'] = Label(window, text="Utorid:")
    fields['utorid'] = Entry(window, width=10)

    fields['password_label'] = Label(window, text="Password:")
    fields['password'] = Entry(window, width=10, show='*')

    if 8 <= datetime.today().month <= 12:
        TARGET_SECTION_CODE = f'{datetime.today().year}9'
    elif 1 <= datetime.today().month <= 3:
        TARGET_SECTION_CODE = f'{datetime.today().year}1'
    else:
        TARGET_SECTION_CODE = f'{datetime.today().year}5'
    fields['session_code_label'] = Label(window, text=f"Session Code: {TARGET_SECTION_CODE}")

    fields['course_code_label'] = Label(window, text="Course Code:")
    fields['course_code'] = EntryWithPlaceholder(window, 'CSC108H1', width=10)

    fields['tut_label'] = Label(window, text="Modify TUT Mode")


    def toggle():
        global MODIFY_TUT_MODE
        if fields['tut_toggle'].config('text')[-1] == 'ON':
            fields['tut_toggle'].config(text='OFF')
            MODIFY_TUT_MODE = False
        else:
            fields['tut_toggle'].config(text='ON')
            messagebox.showinfo("TUT Example", "TUT sections example (only valid if you already enrolled the course) "
                                               "\nNO SPACE:\n\n1001,1002")
            MODIFY_TUT_MODE = True


    fields['tut_toggle'] = Button(text="OFF", width=10, command=toggle)
    fields['tut'] = EntryWithPlaceholder(window, "Enter TUT sections separate by ','", width=10)

    fields['wait_time_label'] = Label(window, text="Refresh interval (in sec):")
    fields['wait_time'] = EntryWithPlaceholder(window, '5', width=10)

    fields['course_session_code_label'] = Label(window, text="Course Session Code:")
    fields['course_session_code_rads'] = Frame(window)
    selected_section = StringVar(None, "F")
    rads = [
        Radiobutton(fields['course_session_code_rads'], text='F', value="F", variable=selected_section),
        Radiobutton(fields['course_session_code_rads'], text='S', value="S", variable=selected_section),
        Radiobutton(fields['course_session_code_rads'], text='Y', value="Y", variable=selected_section)
    ]

    fields['2captcha_label'] = Label(window, text="2Captcha API Key:")
    fields['2captcha'] = EntryWithPlaceholder(window, 'Enter API to bypass hCaptcha', width=10)

    for field in fields:
        fields[field].pack(anchor=W, padx=10, pady=5, fill=X)
    for rad in rads:
        rad.pack(expand=True, side=LEFT)

    fields['submit'] = Button(window, text="Submit", command=submit)
    fields['submit'].pack(side=BOTTOM)

    signature = Label(window, text="Made by @Changhao Song")
    signature.pack()

    donation = Button(window, text="Buy me a coffee ☕️", command=donation)
    donation.pack()

    window.mainloop()
