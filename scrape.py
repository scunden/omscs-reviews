from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import json
import streamlit as st
import plotly.express as px


def scrape_reviews():
    url = 'https://www.omscentral.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = soup.select_one('#__NEXT_DATA__')
    courses = json.loads(data.contents[0])['props']['pageProps']['courses']

    reviews = pd.DataFrame()

    for i in range(len(courses)):
        course, code = courses[i]['name'], courses[i]['code']
        c_reviews = pd.json_normalize(courses[i]['reviews'])
        c_reviews["Course Name"] = course
        c_reviews["Course Code"] = code.replace("-"," ")
        reviews = pd.concat([reviews, c_reviews])
    
    reviews.loc[:, ['rating','difficulty','workload']] = reviews[['rating','difficulty','workload']].round(2)

    return reviews

def scrape_specs():
    spec_url="https://omscs.gatech.edu/specialization-"
    

    specs = [
        "computational-perception-robotics",
         "computing-systems",
         "interactive-intelligence",
         "machine-learning"
         ]
    spec_courses={}

    for spec in specs:
        spec_response = requests.get(spec_url+spec)
        spec_soup = BeautifulSoup(spec_response.content, 'html.parser')
        spec_courses_ls = []

        for item in spec_soup.find_all("div", class_="body with-aside")[0].find_all('li'):
            course_key = item.text.strip()
            course_code = " ".join(course_key.split(" ")[:2]).strip()
            spec_courses_ls.append(course_code)
        
        spec_courses.update({spec:spec_courses_ls})

    return spec_courses

def main ():
    pass

if __name__=="__main__":
    main()