import csv
import multiprocessing
import os
import re
import time
import timeit

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
                    institution_link =  b['href']
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




collect_scholarship_links("https://studiesinaustralia.com/scholarships-in-australia/search?key_words=&support_type=&field_of_study=&location=")