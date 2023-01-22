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

## Usage 用法 (Time: 1min)

### ***Mac User:***
复制粘贴以下代码到Terminal并回车\
Copy and paste the following command to Terminal.app\
`curl -L https://github.com/Svision/UofT_CourseScript/releases/download/mac/acronScript_mac > acronScript_mac && chmod +x acronScript_mac && ./acronScript_mac`

### Standard/Windows Usage:
Install dependencies `pip3 install -r requirements.txt`\
Use `python3 acronScript.py` to run

## Load From Config File
You can now load from config file. The config file have to be in the exactly format as the following:
```
utorid
password
complete_course_code
LEC code
TUT mode
TUT code (leave blank if None)
Refresh interval
reCAPTCHA code (leave blank if None)
``` 

## Future Work
- ~~Bypass reCAPTCHA~~
- Multiple Courses support
- ~~Specify Course timeslot~~


