# UofT_CourseScript
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E0F4Y96)
## Description
UofT Course Script is a fully free open-source script written in Python with [Selenium](https://www.selenium.dev/) (automating web applications) to help UofT students get popular courses securely.

## Motivation
There are already some agents who charge students to 'help' them get popular courses, and students usually need to provide their username and password.
This behavior is not only very unsecure to themselves but also unfair for other students.

## Purpose
***This script is intended solely to provide a more fair and secure environment for UofT students' course enrollment.***

## Warning
***NOT INTENDED FOR ANY COMMERCIAL USE***

## Demo
![scriptExample](https://user-images.githubusercontent.com/12111913/157550594-e9bcbc86-1dd9-41a8-95d9-6dc47d6b0984.gif)


## Usage
### Pre-requisite:
- Python3.8+

- `pip3 install -r /path/to/requirements.txt`
- OR
- `pip3 install selenium`
- `pip3 install selenium-requests`
- `pip3 install webdriver-manager`
#### For Non-developers (Time: 5min):
The only lines to change for acronScript.py are in angle brackets `<>` (need to remove the brackets too), the naming are self-explanatory.
```
UTORID = "<utorid>"
PASSWORD = "<password>"

TARGET_COURSE_CODE = "<course_code>"  # example for CSC108 in UTSG: "CSC108H1", DON'T forget H1
TARGET_SESSION_CODE = "<session_code>"  # example for 2022 Summer: "20225", options are "yyyym" where m can be one of 1, 5, 9
TARGET_SECTION_CODE = "<section_code>"  # example for Full Session: "Y", options are "Y", "F", "S"
```
***After changing the acronScript.py, open 'terminal' and cd to this script directory***\
***run `python3 acronScript.py`***
> Please refer to this video if you do not know how to change directory (cd) in terminal: https://www.youtube.com/watch?v=1rUFqkRQkok
>> OR find kind CS students or developers to help you :)

> NOTE: If any package is missing please install the packages by running pre-requiste three `pip3 install ...` command one-by-one.
##### Example:
```
UTORID = "songcha8"
PASSWORD = "***************"

TARGET_COURSE_CODE = "CSC108H1"  # example for CSC108 in UTSG: "CSC108H1", DON'T forget H1
TARGET_SESSION_CODE = "20225"  # example for 2022 Summer: "20225", options are "yyyym" where m can be one of 1, 5, 9
TARGET_SECTION_CODE = "Y"  # example for Full Session: "Y", options are "Y", "F", "S"
```

#### For Developers (Time: 2min):
In addition to the guide above, you can try to configure `RETRY_LIMIT` and `WAIT_TIME` to bypass reCAPTCHA

## Future Work
- Bypass reCAPTCHA
- Multiple Courses support
- Specify Course timeslot
