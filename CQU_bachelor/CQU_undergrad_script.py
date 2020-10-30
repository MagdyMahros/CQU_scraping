"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 28-10-20
    * description:This script extracts the corresponding undergraduate courses details and tabulate it.
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

course_data = {'Level_Code': '', 'University': 'CQ University', 'City': '', 'Country': 'Australia',
               'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD', 'Currency_Time': 'year',
               'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '', 'Prerequisite_1': '',
               'Prerequisite_2': 'IELTS', 'Prerequisite_3': '', 'Prerequisite_1_grade': '', 'Prerequisite_2_grade': '6.0',
               'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '', 'Availability': '', 'Description': '',
               'Career_Outcomes': '', 'Online': '', 'Offline': '', 'Distance': '', 'Face_to_Face': '',
               'Blended': '', 'Remarks': ''}

possible_cities = {'rockhampton': 'Rockhampton', 'cairns': 'Cairns', 'bundaberg': 'Bundaberg', 'townsville': 'Townsville',
                   'online': 'Online', 'gladstone': 'Gladstone', 'mackay': 'Mackay', 'mixed': 'Online', 'yeppoon': 'Yeppoon',
                   'brisbane': 'Brisbane', 'sydney': 'Sydney', 'queensland': 'Queensland', 'melbourne': 'Melbourne',
                   'albany': 'Albany', 'perth': 'Perth', 'adelaide': 'Adelaide', 'noosa': 'Noosa', 'emerald': 'Emerald'}
possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    actual_cities = []
    remarks_list = []
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

    # DURATION & DURATION_TIME / PART-TIME & FULL-TIME
    # for bachelor
    duration_span_tag = soup.find('span', class_='course-info-highlight', text=re.compile('DURATION', re.IGNORECASE))
    if duration_span_tag:
        duration_p_1 = duration_span_tag.find_next('p')
        if duration_p_1:
            if 'part-time' in duration_p_1.get_text().lower():
                course_data['Part_Time'] = 'yes'
            else:
                course_data['Part_Time'] = 'no'
            if 'full-time' in duration_p_1.get_text().lower():
                course_data['Full_Time'] = 'yes'
            else:
                course_data['Full_Time'] = 'no'
            converted_duration = dura.convert_duration(duration_p_1.get_text().strip())
            if converted_duration is not None:
                duration_list_1 = list(converted_duration)
                duration_1 = duration_list_1[0]
                duration_time_1 = duration_list_1[1]
                if duration_1 == 1 and 'Years' in duration_time_1:
                    duration_time_1 = 'Year'
                if duration_1 == 1 and 'Months' in duration_time_1:
                    duration_time_1 = 'Month'
                course_data['Duration'] = duration_1
                course_data['Duration_Time'] = duration_time_1
                print('DURATION / DURATION TIME: ',
                      str(course_data['Duration']) + ' / ' + str(course_data['Duration_Time']))
            else:
                # for certificate
                duration_container = soup.find('span', class_='ct-accordion__title',
                                               text=re.compile('Course Structure', re.IGNORECASE))\
                    .find_parent('label', class_='ct-accordion__header')
                if duration_container:
                    duration_tag = duration_container.find_next('div', class_='ct-accordion__content').\
                        find('b', text=re.compile('Duration', re.IGNORECASE))
                    if duration_tag:
                        duration_p = duration_tag.find_next_sibling('p')
                        if duration_p:
                            if 'part-time' in duration_p.get_text().lower().strip():
                                course_data['Part_Time'] = 'yes'
                            else:
                                course_data['Part_Time'] = 'no'
                            if 'full-time' in duration_p.get_text().lower().strip():
                                course_data['Full_Time'] = 'yes'
                            else:
                                course_data['Full_Time'] = 'no'
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
                                # if not found at all
                                course_data['Duration'] = 'Not available'
                                course_data['Duration_Time'] = 'Not available'
                                print('DURATION / DURATION TIME: ',
                                      str(course_data['Duration']) + ' / ' + str(course_data['Duration_Time']))
            print('PART-TIME/FULL-TIME: ', course_data['Part_Time'] + ' / ' + course_data['Full_Time'])

        # DELIVERY
        delivery_title = soup.find('span', class_='course-info-highlight', text=re.compile('STUDY MODES', re.IGNORECASE))
        if delivery_title:
            delivery_p = delivery_title.find_next('p')
            if delivery_p:
                delivery_ = delivery_p.get_text().__str__().strip().lower()
                delivery__ = re.findall(r"[\w']+", delivery_)
                if 'on' in delivery__ and 'campus' in delivery__:
                    course_data['Offline'] = 'yes'
                    course_data['Face_to_Face'] = 'yes'
                else:
                    course_data['Offline'] = 'no'
                    course_data['Face_to_Face'] = 'no'
                if 'off' in delivery__ and 'campus' in delivery__:
                    course_data['Distance'] = 'yes'
                else:
                    course_data['Distance'] = 'no'
                if 'online' in delivery__:
                    course_data['Online'] = 'yes'
                else:
                    course_data['Online'] = 'no'
                if 'mixed' in delivery__ and 'mode' in delivery__:
                    course_data['Blended'] = 'yes'
                    course_data['Offline'] = 'yes'
                    course_data['Online'] = 'yes'
                    course_data['Face_to_Face'] = 'yes'
                else:
                    course_data['Blended'] = 'no'
            print('DELIVERY: online: ' + course_data['Online'] + ' offline: ' + course_data[
                'Offline'] + ' face to face: ' +
                  course_data['Face_to_Face'] + ' blended: ' + course_data['Blended'] + ' distance: ' + course_data[
                      'Distance'])

        # AVAILABILITY
        tabs_container = soup.find('div', class_='ct-tabs__wrapper')
        if tabs_container:
            avail_tabs = tabs_container.find_all('a', class_='tabs-button')
            if avail_tabs:
                tabs_text = [text.get_text().lower() for text in avail_tabs]
                if 'domestic' in tabs_text:
                    course_data['Availability'] = 'D'
                if 'international' in tabs_text:
                    course_data['Availability'] = 'I'
                if 'domestic' in tabs_text and 'international' in tabs_text:
                    course_data['Availability'] = 'A'
                print('AVAILABILITY: ' + course_data['Availability'])
    # CITY
    availability_tag = soup.find('span', class_='course-info-highlight', text=re.compile('AVAILABILITY', re.IGNORECASE))
    if availability_tag:
        availability_p = availability_tag.find_next_sibling('p')
        if availability_p:
            av_text = availability_p.get_text().strip().lower()
            av_text_list = re.findall(r"[\w']+", av_text)
            if av_text_list:
                if 'rockhampton' in av_text_list:
                    actual_cities.append('rockhampton')
                if 'cairns' in av_text_list:
                    actual_cities.append('cairns')
                if 'bundaberg' in av_text_list:
                    actual_cities.append('bundaberg')
                if 'townsville' in av_text_list:
                    actual_cities.append('townsville')
                if 'online' in av_text_list:
                    actual_cities.append('online')
                if 'gladstone' in av_text_list:
                    actual_cities.append('gladstone')
                if 'mackay' in av_text_list:
                    actual_cities.append('mackay')
                if 'mixed' in av_text_list:
                    actual_cities.append('online')
                if 'brisbane' in av_text_list:
                    actual_cities.append('brisbane')
                if 'yeppoon' in av_text_list:
                    actual_cities.append('yeppoon')
                if 'sydney' in av_text_list:
                    actual_cities.append('sydney')
                if 'melbourne' in av_text_list:
                    actual_cities.append('melbourne')
                if 'queensland' in av_text_list:
                    actual_cities.append('queensland')
                if 'albany' in av_text_list:
                    actual_cities.append('albany')
                if 'perth' in av_text_list:
                    actual_cities.append('perth')
                if 'adelaide' in av_text_list:
                    actual_cities.append('adelaide')
                if 'noosa' in av_text_list:
                    actual_cities.append('noosa')

            else:
                actual_cities.append('rockhampton')
            print('CITY: ', actual_cities)

    # PREREQUISITE_1/PREREQUISITE_TIME
    rank_tag = soup.find('span', class_='course-info-highlight', text=re.compile('RANK CUT OFF', re.IGNORECASE))
    if rank_tag:
        rank_p = rank_tag.find_next_sibling('p')
        if rank_p:
            atar_ = rank_p.get_text().strip().split('ATAR:')
            if atar_:
                atar = atar_[1]
                if atar:
                    course_data['Prerequisite_1_grade'] = atar
                    course_data['Prerequisite_1'] = 'year 12'
    else:
        course_data['Prerequisite_1'] = 'N/A'
        course_data['Prerequisite_1_grade'] = 'N/A'
    print('ATAR: ', course_data['Prerequisite_1_grade'])

    # CAREER OUTCOMES
    career_container = soup.find('span', class_='ct-accordion__title',
                                   text=re.compile('Career Opportunities and Outcomes', re.IGNORECASE)) \
        .find_parent('label', class_='ct-accordion__header')
    if career_container:
        career_p = career_container.find_next('div', class_='ct-accordion__content').find('p')
        if career_p:
            career_text = career_p.get_text().strip()
            print('CAREER: ', career_text)
        else:
            career_div = career_container.find_next('div', class_='ct-accordion__content')
            if career_div:
                career_div_text = career_div.get_text().strip()
                print('CAREER: ', career_div_text)

    # FEES
    # for domestic
    fees_tag = soup.find('span', class_='course-info-highlight', text=re.compile('FULL COURSE COST', re.IGNORECASE))
    if fees_tag:
        fees_p = fees_tag.find_next('p')
        if fees_p:
            # print(fees_p.get_text())
            fees = re.compile(r'(.+)\(2021\)')
            fee = fees.search(fees_p.get_text())
            if fee:
                fee_n = fee.group(1).replace('$', '')
                course_data['Local_Fees'] = fee_n
                remarks_list.append('The local fees are for the full course')
            else:
                course_data['Local_Fees'] = 'Not available for 2021'
        print('LOCAL FEES: ', course_data['Local_Fees'])
    # for international
    # navigate to International tab
    tabs_container_1 = soup.find('div', class_='ct-tabs__wrapper')
    if tabs_container_1:
        avail_tabs_1 = tabs_container_1.find_all('a', class_='tabs-button', href=True)
        if avail_tabs_1:
            tabs_text_1 = [text.get_text().lower() for text in avail_tabs_1]
            if 'international' in tabs_text_1:
                try:
                    browser.execute_script("arguments[0].click();", WebDriverWait(browser, 5).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    '//*[@id="main"]/div[1]/div/article/div[3]/div/div/a[2]'))))
                except TimeoutException:
                    print('Timeout Exception')
                    pass
                # grab the price
                fees_tag_1 = soup.find('div', class_='ct-tabs__wrapper')
                if fees_tag_1:
                    fees_p_1 = fees_tag_1.find_next('p')
                    if fees_p_1:
                        fees_1 = re.compile(r'(.+)\(2021\)')
                        fee_1 = fees_1.search(fees_p_1.get_text())
                        if fee_1:
                            fee_n_1 = fee_1.group(1).replace('$', '')
                            course_data['Int_Fees'] = fee_n_1
                            remarks_list.append('The international fees are for the full course')
                        else:
                            course_data['Int_Fees'] = 'Not available for 2021'
                        print('INTERNATIONAL FEE: ', course_data['Int_Fees'])

    course_data['Remarks'] = remarks_list
    del remarks_list

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities

    # TABULATE THE DATA
    desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                          'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                          'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                          'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance', 'Face_to_Face',
                          'Blended', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('CQU_undergrad_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)
