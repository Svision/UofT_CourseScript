import json
import random
import time
from datetime import datetime

import selenium.common.exceptions
from seleniumrequests import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from helper import *
from PIL import ImageTk, Image

UTORID = ""
PASSWORD = ""

TARGET_COURSE_CODE = ""  # example for CSC108 in UTSG: "CSC108H1"
TARGET_SESSION_CODE = "20229"  # example for 2022 Summer: "20225", options are "yyyym" where m can be one of 1, 5, 9
TARGET_SECTION_CODE = ""  # example for Full Session: "Y", options are "Y", "F", "S"

# Extension
TARGET_COURSE_SECTION = ""
TARGET_TUT_SECTION = ""

ERRNO = -1
WAIT_TIME = 60  # Tune the value as needed to bypass reCAPTCHA
RETRY_LIMIT = 20
COURSE_URL = "https://acorn.utoronto.ca/sws/rest/enrolment/course/view?acpDuration=1&courseCode={courseCode}&courseSessionCode={sessionCode}&designationCode1=PGM&levelOfInstruction=U&postAcpDuration=2&postCode=ASCRSHBSC&postDescription=A%26S+Bachelor%27s+Degree+Program&primaryOrgCode=ARTSC&sectionCode={sectionCode}&sessionCode={sessionCode}"
COURSE_SESSION_URL = "https://acorn.utoronto.ca/sws/#/courses/{index}"
ENROLL_STATUS = False

driver = None


def login():
    driver.get("https://acorn.utoronto.ca/sws/#/")
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

    # Check dashboard present to identify login status
    Wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Dashboard')]")))
    print("Login SUCCESS!\n")


def enroll_course(sectionNo):
    # find tab
    course_session_url = COURSE_SESSION_URL.format(index=0)  # Currently, have Fall/Winter and Summer session tabs
    driver.get(course_session_url)
    search = driver.find_element(By.ID, value="typeaheadInput")
    search.send_keys(TARGET_COURSE_CODE)
    time.sleep(random.randint(1, 3))

    # find course
    course_span = driver.find_element(By.XPATH, value=f"//span[contains(text(), '{TARGET_COURSE_CODE} {TARGET_SECTION_CODE}')]")
    course_span.click()
    time.sleep(random.randint(1, 3))

    # choose section
    course_section = driver.find_element(By.ID, value=f"courseLEC{sectionNo}")
    course_section.click()

    # enroll
    enroll_btn = driver.find_element(By.ID, value="enrol")
    enroll_btn.click()
    time.sleep(random.randint(2, 4))

    # check enrollment
    try:
        driver.find_element(By.ID, f"{TARGET_COURSE_CODE}-courseBox")
        global ENROLL_STATUS
        ENROLL_STATUS = True
        print("Enrollment SUCCESS!")
    except selenium.common.exceptions.NoSuchElementException:
        print("Enroll failed, retrying...")


def get_course_info():
    course_url = COURSE_URL.format(courseCode=TARGET_COURSE_CODE, sectionCode=TARGET_SECTION_CODE, sessionCode=TARGET_SESSION_CODE)
    driver.get(course_url)
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
        if meeting["teachMethod"] == "LEC":  # check lec or tut
            space_available = meeting["enrollmentSpaceAvailable"]
            total_space = meeting["totalSpace"]
            sectionNo = meeting["sectionNo"]
            display_name = meeting["displayName"]
            if space_available != 0:
                print(f"{TARGET_COURSE_CODE} has {space_available} spaces left (total: {total_space}) for {display_name}")
                enroll_course(sectionNo)
                if ENROLL_STATUS is True:
                    return
            else:
                print(f"{TARGET_COURSE_CODE} has no space left for {display_name}")


def submit():
    global ERRNO

    global UTORID
    UTORID = fields['utorid'].get()
    global PASSWORD
    PASSWORD = fields['password'].get()
    if UTORID == "" or PASSWORD == "":
        messagebox.showerror("Auth Error", "Both utorid and password cannot be empty")
        return
    global TARGET_COURSE_CODE
    TARGET_COURSE_CODE = fields['course_code'].get()
    if not len(TARGET_COURSE_CODE) == 8:
        messagebox.showerror("Course Code Error", "Example course code for CSC108 in UTSG: \n\nCSC108H1")
        return
    global TARGET_SECTION_CODE
    TARGET_SECTION_CODE = selected_section.get()
    window.quit()

    global driver
    driver = Chrome(ChromeDriverManager().install())
    login()

    print(f"Checking {TARGET_COURSE_CODE} for {TARGET_SESSION_CODE}...")
    retry_count = 0
    while retry_count < RETRY_LIMIT:
        get_course_info()
        if ENROLL_STATUS is True:
            break
        time.sleep(WAIT_TIME)
        retry_count += 1


if __name__ == "__main__":
    window = Tk()
    window.eval('tk::PlaceWindow . center')
    window.geometry('280x400')
    window.title("Acron Enrollment Helper")
    img = ImageTk.PhotoImage(Image.open("U-of-T-logo.png"))
    logo = Label(window, image=img)
    logo.pack()

    fields = {}
    fields['utorid_label'] = Label(window, text="Utorid:")
    fields['utorid'] = Entry(window, width=10)

    fields['password_label'] = Label(window, text="Password:")
    fields['password'] = Entry(window, width=10, show='*')

    fields['course_code_label'] = Label(window, text="Course Code:")
    fields['course_code'] = EntryWithPlaceholder(window, 'CSC108H1', width=10)

    fields['session_code_label'] = Label(window, text="Session Code:")
    fields['session_code_rads'] = Frame(window)
    selected_section = StringVar(None, "F")
    rads = [
        Radiobutton(fields['session_code_rads'], text='F', value="F", variable=selected_section),
        Radiobutton(fields['session_code_rads'], text='S', value="S", variable=selected_section),
        Radiobutton(fields['session_code_rads'], text='Y', value="Y", variable=selected_section)
    ]

    for field in fields:
        fields[field].pack(anchor=W, padx=10, pady=5, fill=X)
    for rad in rads:
        rad.pack(expand=True, side=LEFT)

    fields['submit'] = Button(window, text="Submit", command=submit)
    fields['submit'].pack()

    window.mainloop()
