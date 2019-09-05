import csv
import multiprocessing
import os
import re
import time
import timeit
import pandas as pd

# install xlrd
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from fake_useragent import UserAgent
from selenium import webdriver
from unidecode import unidecode

# dynamic pathname based on different device, instead of hard coding the pathname
uniqueLinkList_path = os.path.join(os.getcwd(), 'UniqueLinkList.csv')
extractedData_path = os.path.join(os.getcwd(), 'ExtractedData.csv')

# Setup Chrome display
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")

user = UserAgent().random
headers = {'User-Agent': user}

# obtaining links for all the institutions by region
def collect_scholarship_links(str_link):
    print("opening unique link list file")
    with open(uniqueLinkList_path, 'wt', encoding='utf-8', newline='') as Linklist:
        writer2 = csv.writer(Linklist)
        options.add_argument(f'user-agent={user}')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options,
                                executable_path=r'C:\Users\Nicholas\Documents\Summer intern @ Seeka\chromedriver.exe')

        driver.get(str_link)


        print("done")
        total_link_info = ['']
        print("driver done, getting page source")
        while True:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            for a in soup.find_all('div', class_='row row-search-result'):
                for x in a.find_all('div', class_='col-md-12'):
                    b = x.find('a')
                    institution_link = b['href']
                    total_link_info[0] = institution_link
                    print(total_link_info)
                    writer2.writerow(total_link_info)
                    time.sleep(1)
            try:
                driver.find_element_by_link_text('»').click()
                print("Moving on to the next page")
                continue
            except:
                print("This is the last page")
                break


# multiprocessing structure
def multi_pool(func, input_name_list, procs):
    templist = []
    # counter = len(input_name_list)
    pool = multiprocessing.Pool(processes=procs)
    # print('Total number of processes: ' + str(procs))
    for a in pool.imap(func, input_name_list):
        templist.append(a)
        # print('Number of links left: ' + str(counter - len(templist)))
    pool.terminate()
    pool.join()
    return templist


# retrieving all relevant information from the institution's profile page
def collect_scholarship_data(str_scholarship_link):
    complete_scholarship_details = {}
    page = requests.get(str_scholarship_link[0])
    soup = BeautifulSoup(page.content, 'lxml')

    # obtaining the name and funder
    try:
        complete_scholarship_details['Scholarship Name'] = soup.find('div', class_='header').h1.get_text()
    except:
        pass

    complete_scholarship_details['Scholarship Sponsor'] = soup.find('div', class_='header').h2.get_text()
    complete_scholarship_details['Description'] = soup.find('div', class_='col-md-9 description').get_text().lstrip().rstrip()

    for rows in soup.find('table', class_='table table-glance table-striped-blue table-scholarship').find_all('tr'):
        if rows.find('th') != None:
            requirement_header = rows.find('th').get_text()
            text = rows.find('td').get_text().split(",")
            final_list = []
            for items in text:
                items = items.lstrip().rstrip()
                final_list.append(items)
            requirement_description = ', '.join(list(filter(None, final_list)))
            complete_scholarship_details[requirement_header] = requirement_description


    #print(complete_scholarship_details)

    try:
        x = soup.find('table', class_='table table-glance table-striped-blue table-scholarship').find('a')
        complete_scholarship_details['Scholarship website'] = x['href']
    except:
        pass

    print("Done with " + str(str_scholarship_link[0]) + " ", complete_scholarship_details)
    return complete_scholarship_details

    # print(str_scholarship_link[0] + " has " + str(len(complete_scholarship_details.keys())) + ' keys.' + str(complete_scholarship_details.keys()))


if __name__ == '__main__':

    print("start")
   # collect_scholarship_links("https://www.goodschools.com.au/compare-schools/search?state=NSW")
   # print("begin collecting institution data")

    rawdata = pd.read_csv(uniqueLinkList_path)
    scholarship_links = rawdata.values.tolist()

    # 'Scholarship Name', 'Scholarship Sponsor', 'Description', 'Eligibility:', 'Application closing date:', 'Support Type:', 'Level of Study:', 'Gender:', 'Frequency of Offer:', 'Fields of Study:', 'Location of Study:', 'No Offered Per Year:', 'Target Group:', 'Subjects:', 'Scholarship website'])
    columns = ['Scholarship Name', 'Scholarship Sponsor', 'Description', 'Eligibility:', 'Application closing date:',
               'Support Type:', 'Level of Study:', 'Gender:', 'Frequency of Offer:', 'Fields of Study:',
               'Location of Study:', 'No Offered Per Year:', 'Target Group:', 'Subjects:', 'Scholarship website']

    all_data = multi_pool(collect_scholarship_data, scholarship_links, 5)
    print("done all")
    print(all_data)

    print("Writing to csv file now")
    with open('scholarship_data.csv', 'wt', newline='') as f:
        w = csv.writer(f)
        w.writerow(columns)
        for items in all_data:
            w.writerow([items.get(col, None) for col in columns])

# collect_scholarship_links("https://studiesinaustralia.com/scholarships-in-australia/search?key_words=&support_type=&field_of_study=&location=")

#collect_scholarship_data("https://studiesinaustralia.com/scholarships-in-australia/9350/american-association-of-university-women/aauw-educational-foundation-international-fellowship")