import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
import os

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# MAIN ROUTINE
course_type_links = []
each_url = 'https://www.cqu.edu.au/courses/find-a-course?meta_studyLevel_not=%22Short%20Course%22&collection=2019-cqu-courses&fmo=true&query=&meta_studyLevel_or=%22Level%208%3A%20Graduate%20Certificate%22%2C%22Level%208%3A%20Graduate%20Diploma%22%2C%22Level%209%3A%20Masters%20Degree%20(Coursework)%22%2C%22Level%209%3A%20Masters%20Degree%20(Extended)%22%2C%22Level%209%3A%20Masters%20Degree%20(Research)%22%2C%22Level%2010%3A%20Doctoral%20Degree%22'

# LINK EXTRACTOR =============================================================================
course_links = []
course_links_2 = []
pages = set()

pages.add(each_url)
i = 1
while i <= 73:
    cur_url = each_url + '&start_rank=' + str(i) + '&sort=metasortLevel'
    pages.add(cur_url)
    # print(cur_url)
    i += 12

for j in pages:
    browser.get(j)
    time.sleep(0.5)
    pure_url = j.strip()
    each_page = browser.page_source
    soup = bs4.BeautifulSoup(each_page, 'html.parser')

    courses_result = soup.find('div', id='course_results')
    if courses_result:
        courses = courses_result.find_all('div', class_='ct-course-card__header border-left-yellow')
        if courses:
            for course in courses:
                a_tag = course.find('a', href=True)
                if a_tag:
                    link = a_tag['href']
                    # print(link)
                    course_links.append(link)

# FILE
course_links_file_path = os.getcwd().replace('\\', '/') + '/CQU_postgrad_links.txt'
course_links_file = open(course_links_file_path, 'w')
for i in course_links:
    if i is not None and i != "" and i != "\n":
        if i == course_links[-1]:
            course_links_file.write(i.strip())
        else:
            course_links_file.write(i.strip()+'\n')
course_links_file.close()
