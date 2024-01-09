# UofT_CourseScript
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E0F4Y96)

## DISCLAIMER
***Using the scirpt could result your Utorid Account be blocked by admin!!!***\
***USE AT YOUR OWN RISK!***\
***NOT INTENDED FOR ANY COMMERCIAL USE***

## Description
UofT Course Script is a fully free open-source script written in Python with [Selenium](https://www.selenium.dev/) (automating web applications) to help UofT students get popular courses securely.

## Motivation
There are already some agents who charge students to 'help' them get popular courses, and students usually need to provide their username and password.
This behavior is not only very unsecure to themselves but also unfair for other students.

## Purpose
***This script is intended solely to provide a more fair and secure environment for UofT students' course enrollment.***

## Usage

### Installation

1. Ensure [Python](https://www.python.org/downloads/) is installed on your machine.

2. Clone and navigate to the repository.
   ```bash
   cd path/to/UofT_CourseScript
   ```

3. Install the necessary Python packages.
   ```bash
   pip3 install -r requirements.txt
   ```

4. Run the script.
   ```bash
   python3 acronScript.py
   ```

### First-Time Login

#### Step 1: Update DUO Authentication Settings

- Log into Acorn using your UTORid and password.
- When prompted by DUO Security, click on `My Settings & Devices`.
- Press the 'Send Me a Push' button and approve the notification on your DUO-authorized mobile device.
- For "When I log in:", select "Ask me to choose an authentication method" and click "Save".

#### Step 2: Generate Bypass Code

On your first run of the script, you'll encounter the DUO Security prompt.

#### Step 3: Approve DUO Mobile Request

After generating the bypass code, your DUO-authorized mobile device will receive a request. Approve this to continue. **Note**: This step is a one-time requirement.

### Subsequent Runs

Once the initial setup is complete, the script will operate autonomously without needing DUO mobile approvals.


## Future Work
- ~~Bypass reCAPTCHA~~
- ~~Bypass DUO~~
- ~~Specify Course timeslot~~
- ~~Multiple Courses support~~
- Better UI



