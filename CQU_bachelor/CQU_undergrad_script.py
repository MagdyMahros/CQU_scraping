"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 28-10-20
    * description:This script extracts the corresponding Postgraduate courses details and tabulate it.
"""

import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/CQU_bachelor_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/CQU_undergrad.csv'

course_data = {'Level_Code': '', 'University': 'Australian Catholic University', 'City': '', 'Country': 'Australia',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '', 'Prerequisite_1': 'IELTS',
               'Prerequisite_2': '', 'Prerequisite_3': '', 'Prerequisite_1_grade': '6.5', 'Prerequisite_2_grade': '',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': '', 'Description': '',
               'Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': '', 'Face_to_Face': '',
               'Blended': '', 'Remarks': ''}

possible_cities = {'albany': 'Albany', 'perth': 'Perth'}
possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    actual_cities = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # SAVE COURSE TITLE
    title_container = soup.find('div', class_='course-details-course-header__container')
    if title_container:
        title = title_container.find('h1')
        course_data['Course'] = title.get_text().strip()
        print('COURSE TITLE: ', title.get_text().strip())

    # DECIDE THE LEVEL CODE
    for i in level_key:
        for j in level_key[i]:
            if j in course_data['Course']:
                course_data['Level_Code'] = i
    print('COURSE LEVEL CODE: ', course_data['Level_Code'])

    # DECIDE THE FACULTY
    for i in faculty_key:
        for j in faculty_key[i]:
            if j.lower() in course_data['Course'].lower():
                course_data['Faculty'] = i
    print('COURSE FACULTY: ', course_data['Faculty'])

    # COURSE DESCRIPTION
    description = soup.find('p', class_='at-a-glance')
    if description:
        course_data['Description'] = description.get_text().strip()
        print('COURSE DESCRIPTION: ', description.get_text().strip())

    # COURSE LANGUAGE
    for language in possible_languages:
        if language in course_data['Course']:
            course_data['Course_Lang'] = language
        else:
            course_data['Course_Lang'] = 'English'
    print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # DURATION & DURATION_TIME
    duration_container = soup.find('span', class_='ct-accordion__title',
                                   text=re.compile('Course Structure', re.IGNORECASE))\
        .find_parent('label', class_='ct-accordion__header')
    if duration_container:
        duration_tag = duration_container.find_next('div', class_='ct-accordion__content').\
            find('b', text=re.compile('Duration', re.IGNORECASE))
        if duration_tag:
            duration_p = duration_tag.find_next_sibling('p')
            if duration_p:
                condv_duration = dura.convert_duration(duration_p.get_text().strip())
                if condv_duration is not None:
                    duration_list = list(condv_duration)
                    duration_ = duration_list[0]
                    duration_time = duration_list[1]
                    if duration_ == 1 and 'Years' in duration_time:
                        duration_time = 'Year'
                    if duration_ == 1 and 'Months' in duration_time:
                        duration_time = 'Month'
                    course_data['Duration'] = duration_
                    course_data['Duration_Time'] = duration_time
                    print('DURATION / DURATION TIME: ',
                          str(course_data['Duration']) + ' / ' + str(course_data['Duration_Time']))
                else:
                    course_data['Duration'] = 'Not available'
                    course_data['Duration_Time'] = 'Not available'
                    print('DURATION / DURATION TIME: ',
                          str(course_data['Duration']) + ' / ' + str(course_data['Duration_Time']))

