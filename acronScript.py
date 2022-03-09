import json
import random
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

UTORID = "<utorid>"
PASSWORD = "<password>"

TARGET_COURSE_CODE = "<course_code>"  # example for CSC108 in UTSG: "CSC108H1"
TARGET_SESSION_CODE = "<session_code>"  # example for summer: "20225"

WAIT_TIME = 60  # Tune the value as needed
# https://acorn.utoronto.ca/sws/rest/enrolment/course/view?acpDuration=1&courseCode=CSC236H1&courseSessionCode=20225&designationCode1=PGM&levelOfInstruction=U&postAcpDuration=2&postCode=ASCRSHBSC&postDescription=A%26S+Bachelor%27s+Degree+Program&primaryOrgCode=ARTSC&sectionCode=Y&sessionCode=20225
COURSE_URL = "https://acorn.utoronto.ca/sws/rest/enrolment/course/view?acpDuration=1&courseCode={courseCode}&courseSessionCode={sessionCode}&designationCode1=PGM&levelOfInstruction=U&postAcpDuration=2&postCode=ASCRSHBSC&postDescription=A%26S+Bachelor%27s+Degree+Program&primaryOrgCode=ARTSC&sectionCode=Y&sessionCode={sessionCode}"
ENROLL_STATUS = False

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


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
    print("Login SUCCESS\n")


def enroll_course():
    # TODO: Enroll course
    pass


def get_course_info():
    course_url = COURSE_URL.format(courseCode=TARGET_COURSE_CODE, sessionCode=TARGET_SESSION_CODE)
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
            display_name = meeting["displayName"]
            if space_available != 0:
                print(f"{TARGET_COURSE_CODE} has {space_available} spaces left (total: {total_space}) for {display_name}")
                enroll_course()
            else:
                print(f"{TARGET_COURSE_CODE} has no space left for {display_name}")


if __name__ == "__main__":
    login()

    print(f"Checking {TARGET_COURSE_CODE} for {TARGET_SESSION_CODE}...")
    retry_count = 0
    while retry_count < 5:
        if ENROLL_STATUS is True:
            break
        get_course_info()
        time.sleep(WAIT_TIME)
        retry_count += 1
