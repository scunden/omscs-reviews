from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import string
import json
import streamlit as st
import plotly.express as px


def scrape_data():
    url = 'https://www.omscentral.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = soup.select_one('#__NEXT_DATA__')
    courses = json.loads(data.contents[0])['props']['pageProps']['courses']

    reviews = pd.DataFrame()

    for i in range(len(courses)):
        course, code = courses[i]['name'], courses[i]['code']
        c_reviews = pd.json_normalize(courses[i]['reviews'])
        c_reviews["Course"] = course
        c_reviews["Code"] = code.replace("-"," ")
        c_reviews["Course Key"] = c_reviews["Code"]+" "+c_reviews["Course"]
        reviews = pd.concat([reviews, c_reviews])
    
    return reviews

def main ():
    reviews = scrape_data()
    agg = reviews.groupby(["Course Key"]).agg({'difficulty':np.nanmean,'workload':np.nanmean,'rating':np.nanmean,'id':'count'})
    agg["None"]=1

    st.title("🎲 OMSCS Reviews Visualization")
    st.header("Filter the reviews and select your parameters in the sidebar!")

    ## Filters
    st.sidebar.markdown("## Filter Data")
    years = st.sidebar.slider('Filter Years',min_value=2015, max_value=2022, value=(2015,2022))
    spec = st.sidebar.multiselect('Filter Specialization',  ["ML","CS"], ["ML","CS"])
    semester = st.sidebar.multiselect('Filter Semesters',  ["Fall","Winter","Spring","Summer"], ["Fall","Winter","Spring","Summer"])

    ## Parameter Selection
    options = ["Avg. Difficulty","Avg. Rating","Avg. Workload (Hrs)","No. of Reviews"]
    color_options=["No. of Reviews","Avg. Workload (Hrs)","Specialization"]
    options_mapping = {
        "Avg. Difficulty":"difficulty",
        "Avg. Rating":"rating",
        "Avg. Workload (Hrs)":"workload",
        "No. of Reviews":"id",
        "Specialization":"difficulty",
        "None":None,

        }
    st.sidebar.markdown("## Select Parameter to Visualize")

    x=st.sidebar.selectbox("Select x-axis parameter",options=options, index=0)
    y=st.sidebar.selectbox("Select y-axis parameter",options=options, index=1)
    size=st.sidebar.selectbox("Select size parameter",options=options+["None"], index=3)
    color=st.sidebar.selectbox("Select color parameter",options=color_options+["None"], index=1)

    x_mapped = options_mapping[x]
    y_mapped = options_mapping[y]
    size_mapped = options_mapping[size]
    color_mapped = options_mapping[color]

    

    fig = px.scatter(agg, 
                    x=x_mapped, 
                    y=y_mapped,
                    size=size_mapped, 
                    color=color_mapped,
                    hover_name=agg.index, 
                    size_max=50,
                    color_continuous_scale=px.colors.sequential.Viridis,
                    )
    if x in ["Avg. Difficulty","Avg. Rating"]: 
        fig.add_vline(x=3,line_dash="dash", line_color="white")
        fig.update_layout(xaxis_range=[1,5.5])
    if y in ["Avg. Difficulty","Avg. Rating"]: 
        fig.add_hline(y=3, line_dash="dash", line_color="white")
        fig.update_layout(yaxis_range=[1,5.5])
    
    fig.update_layout(xaxis_title=x, yaxis_title=y)
    st.write(fig)

if __name__=="__main__":
    main()