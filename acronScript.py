import json
import random
import time
from datetime import datetime

import webbrowser

import requests
import ssl
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from helper import *
from twocaptcha import TwoCaptcha

UTORID = ""
PASSWORD = ""

TARGET_COURSE_CODE = ""  # example for CSC108 in UTSG: "CSC108H1"
TARGET_SESSION_CODE = f"{datetime.now().year}{datetime.now().month}"  # options are "yyyym" m is one of 1, 5, 9
TARGET_SECTION_CODE = ""  # example for Full Session: "Y", options are "Y", "F", "S"

# Extension
TARGET_COURSE_SECTION = ""
MODIFY_TUT_MODE = False
TARGET_TUT_SECTION_CODES = []  # TUT ["1001", "1002"]
TARGET_LEC_SECTION_CODES = []
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
    try:
        Wait(driver, 60).until(AnyEc(
            EC.url_to_be(ACORN_URL),
            EC.url_to_be(hCaptcha_URL)
        ))
    except TimeoutException:
        print("Time out, retrying...")
        driver.quit()
        submit()
    check_captcha()


def check_captcha():
    if driver.current_url == hCaptcha_URL:
        bypass_hCaptcha()
        try:
            Wait(driver, 600).until(EC.url_to_be(ACORN_URL))
            script_prompt()
        except TimeoutException:
            print("Time out, retrying...")
            driver.quit()
            submit()
        print("Bypass SUCCESS!")
    else:
        try:
            Wait(driver, 60).until(EC.url_to_be(ACORN_URL))
            script_prompt()
        except TimeoutException:
            print("Time out, retrying...")
            driver.quit()
            submit()
        print("Login SUCCESS!\n")


def create_session_request(url, body, method='post'):
    session = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-CA,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "content-type": "text/plain",
        "sec-ch-ua": '\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-xsrf-token": driver.get_cookie('XSRF-TOKEN')['value'],
        "Referer": "https://acorn.utoronto.ca/sws/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    if method == 'post':
        return session.post(url, headers=headers, data=body)
    else:
        return session.get(url, headers=headers, data=body)


def bypass_hCaptcha():
    if SOLVER_2CAPTCHA is None:
        print("Waiting manually bypass hCaptcha...")
        driver.switch_to.window(driver.current_window_handle)
    else:
        try:
            Wait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        except TimeoutException:
            print("Time out, retrying...")
            driver.quit()
            submit()
        site_key_element = driver.find_element(By.TAG_NAME, "iframe")
        site_src = site_key_element.get_attribute("src")
        start_idx = site_src.index('sitekey=') + 8
        end_idx = site_src.index('&theme')
        site_key = site_src[start_idx:end_idx]
        print('Solving Captcha ' + site_key)

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
        body = result['code']
        verify = create_session_request("https://acorn.utoronto.ca/sws/rest/captcha/verify", body)
        if verify.status_code == 200:
            driver.get(ACORN_URL)


def script_prompt():
    driver_body = driver.find_element(By.XPATH, value="/html/body")
    driver.execute_script("arguments[0].innerText = 'Script working... DO NOT TURN OFF Chrome! Check Terminal for Detail.'", driver_body)


def enroll_modify(sectionNo):
    session = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-CA,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "content-type": "application/json;charset=UTF-8",
        "sec-ch-ua": '\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-xsrf-token": driver.get_cookie('XSRF-TOKEN')['value']
    }
    tutorial = {}
    lecture = {}
    if MODIFY_TUT_MODE:
        tutorial = {"sectionNo": f"TUT,{sectionNo}"}
    else:
        lecture = {"sectionNo": f"LEC,{sectionNo}"}

    body = {
        "activeCourse": {
            "course": {
                "code": TARGET_COURSE_CODE,
                "sessionCode": TARGET_SESSION_CODE,
                "sectionCode": TARGET_SECTION_CODE,
                "primaryTeachMethod": "LEC",
                "enroled": False
            },
            "lecture": tutorial,
            "tutorial": lecture,
            "practical": {}
        },
        "eligRegParams": {
            "postCode": "ASCRSHBSC",
            "postDescription": "A&S Bachelor\\'s Degree Program",
            "sessionCode": TARGET_SESSION_CODE,
            "sessionDescription": "",
            "status": "REG",
            "assocOrgCode": "",
            "acpDuration": "2",
            "levelOfInstruction": "U",
            "typeOfProgram": "BACS",
            "subjectCode1": "SCN",
            "designationCode1": "PGM",
            "primaryOrgCode": "ARTSC",
            "secondaryOrgCode": "",
            "collaborativeOrgCode": "",
            "adminOrgCode": "ARTSC",
            "coSecondaryOrgCode": "",
            "yearOfStudy": "",
            "postAcpDuration": "2",
            "useSws": "Y"
        }
    }
    enroll = create_session_request('https://acorn.utoronto.ca/sws/rest/enrolment/course/modify', body)
    if enroll.status_code == 200:
        enroll_success()
    else:
        print(f"Enroll failed ({enroll.status_code}), retrying...")
        print("Using UI to retry:")
        # find tab
        type = "LEC" if not MODIFY_TUT_MODE else "TUT"
        index = 0
        if 1 < datetime.now().month < 9:
            index = 1
        course_session_url = COURSE_SESSION_URL.format(
            index=index)  # Currently, have Fall/Winter and Summer session tabs
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
        try:
            driver.find_element(By.ID, f"{TARGET_COURSE_CODE}-courseBox")
            enroll_success()
        except:
            print("Enroll failed, retrying...")


def enroll_success():
    global ENROLL_STATUS
    ENROLL_STATUS = True
    print("Enrollment SUCCESS!")
    driver.get("https://ko-fi.com/svision")
    messagebox.showinfo("Donation", "SUCCESS! Buy me a coffee ☕️: https://ko-fi.com/svision")


def get_course_info():
    course_url = COURSE_URL.format(courseCode=TARGET_COURSE_CODE, sectionCode=TARGET_SECTION_CODE,
                                   sessionCode=TARGET_SESSION_CODE)
    response = create_session_request(course_url, None, 'get')
    if response.status_code == 200:
        data = json.loads(response.text)
    else:
        print("hCaptcha detected!")
        driver.get(hCaptcha_URL)
        bypass_hCaptcha()
        return

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
        if (not MODIFY_TUT_MODE and teachMethod == "LEC" and (TARGET_LEC_SECTION_CODES == [] or
                                                              sectionNo in TARGET_LEC_SECTION_CODES)) or (
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
    global TARGET_LEC_SECTION_CODES
    if fields['specify_lec'].get() != "" and fields['specify_lec'].get() != "ALL":
        TARGET_LEC_SECTION_CODES = fields['specify_lec'].get().split(',')
        print(f'Checking LEC {TARGET_LEC_SECTION_CODES}')

    global TARGET_SECTION_CODE
    TARGET_SECTION_CODE = selected_section.get()

    # 2Captcha
    global API_2CAPTCHA
    global SOLVER_2CAPTCHA
    if fields['2captcha'].get() != "" and fields['2captcha'].get() != "Enter API to bypass hCaptcha":
        API_2CAPTCHA = fields['2captcha'].get()
    if API_2CAPTCHA != "":
        SOLVER_2CAPTCHA = TwoCaptcha(API_2CAPTCHA)
        print("Solver created!")

    global driver
    driver = uc.Chrome(chrome_options=chrome_options)
    try:
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
        if str(e).strip() == "ERROR_WRONG_USER_KEY":
            print("API Key is not right!")
            API_2CAPTCHA = ""
        if RETRY_TIME > 0:
            print(str(e))
            print("Retrying...")
            driver.quit()
            if str(e).strip() != "Expecting value: line 1 column 1 (char 0)":
                RETRY_TIME -= 1
            submit()
        else:
            print(str(e))
            exit(1)


def donation():
    webbrowser.open("https://ko-fi.com/svision")


if __name__ == "__main__":
    ssl._create_default_https_context = ssl._create_unverified_context
    window = Tk()
    window.title("Acron Enrollment Helper")

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
    fields['specify_lec_label'] = Label(window, text="Specify Lec Sections:")
    fields['specify_lec_tip_label'] = Label(window, text="Code only (No 'LEC'), separated by ','")
    fields['specify_lec'] = EntryWithPlaceholder(window, 'ALL', width=10)

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
    if datetime.now().month == 1:
        section = "S"
    else:
        section = "F"
    selected_section = StringVar(None, section)
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

    signature = Label(window, text="Made with ❤️ by Changhao Song")
    signature.pack()

    donation = Button(window, text="Buy me a coffee ☕️", command=donation)
    donation.pack()

    window.mainloop()
