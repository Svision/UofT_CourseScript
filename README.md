# UofT_CourseScript

## Description
UofT Course Script is a fully free open-source script written in Python with [Selenium](https://www.selenium.dev/) (automating web applications) to help UofT students get popular courses securely.

## Motivation
There are already some agents who charge students to 'help' them get popular courses, and students usually need to provide their username and password.
This behavior is not only very unsecure to themselves but also unfair for other students.

## Purpose
***This script is intended solely to provide a more fair and secure environment for UofT students' course enrollment.***

## Warning
***NOT INTENDED FOR COMMERCIAL USE***

## Usage
#### For Non-developers (Time: 5min):
The only lines to change in acronScript.py are in angle brackets `<>` (need to remove the brackets too), the naming are self-explanatory.
```
UTORID = "<utorid>"
PASSWORD = "<password>"

TARGET_COURSE_CODE = "<course_code>"  # example for CSC108 in UTSG: "CSC108H1", DON'T forget H1
TARGET_SESSION_CODE = "<session_code>"  # example for 2022 Summer: "20225", options are "yyyym" where m can be one of 1, 5, 9
TARGET_SECTION_CODE = "<section_code>"  # example for Full Session: "Y", options are "Y", "F", "S"
```
***After changing the acronScript.py, open 'terminal' and cd to this script directory***\
***run `python3 acronScript.py`***
> NOTE: Please refer to this video if you do not know how to change directory (cd) in terminal: https://www.youtube.com/watch?v=1rUFqkRQkok
>> OR find kind CS students or developers to help you :)
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
