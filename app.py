from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import json
import streamlit as st
import plotly.express as px
import scrape as sc

def agg_reviews():
    reviews = pd.read_csv('OMSHub.csv')

    agg = reviews.groupby(["Course Name","Course Code"]).agg({
        'difficulty':np.nanmean,
        'workload':np.nanmean,
        'rating':np.nanmean,
        'reviews':'sum'}).reset_index()
    agg.loc[:, ['rating','difficulty','workload']] = agg[['rating','difficulty','workload']].round(2)

    agg = agg.rename({
        'difficulty':"Avg. Difficulty",
        'rating':"Avg. Rating",
        'workload':"Avg. Workload (Hrs)",
        'reviews':'No. of Reviews'
    }, axis=1)

    return agg

def main ():
    # Scrape course specialization
    agg = agg_reviews()
    spec_courses = sc.scrape_specs()
    spec_courses_fmt = {spec.replace("-"," ").title():spec for spec in spec_courses.keys()}

    # Add spec to review agg table
    for spec in spec_courses:
        agg[spec] = np.where(agg["Course Code"].isin(spec_courses[spec]),"In-Spec","Out-of-Spec")

    st.title("OMSCS Reviews Visualization")
    st.header("Filter the reviews and select your parameters in the sidebar!")

    ## Filters
    st.sidebar.markdown("## 🎲 Filter Data")
    
    # years = st.sidebar.slider('Filter Years',min_value=2015, max_value=2022, value=(2015,2022))
    specs = st.sidebar.multiselect('Filter Specialization',  spec_courses_fmt, spec_courses_fmt)
    # sample_size = st.sidebar.slider('Filter Minimum Reviews',min_value=0, max_value=500, value=(100,500))
    # semester = st.sidebar.multiselect('Filter Semesters',  ["Fall","Winter","Spring","Summer"], ["Fall","Winter","Spring","Summer"])

    agg["spec_filter"] = 0
    for spec in specs:
        agg["spec_filter"] = np.where(agg[spec_courses_fmt[spec]]=="In-Spec",1,agg["spec_filter"])
    
    agg = agg[agg["spec_filter"]==1]


    ## Parameter Selection
    options = ["Avg. Difficulty","Avg. Rating","Avg. Workload (Hrs)","No. of Reviews"]
    color_options=["No. of Reviews","Avg. Workload (Hrs)","Specialization"]

    st.sidebar.markdown("## 🔧 Select Parameter to Visualize")

    x=st.sidebar.selectbox("Select x-axis parameter",options=options, index=0)
    y=st.sidebar.selectbox("Select y-axis parameter",options=options, index=1)
    size=st.sidebar.selectbox("Select size parameter",options=options+["None"], index=3)
    color=st.sidebar.selectbox("Select legend parameter",options=color_options+["None"], index=1)

    size = None if size=="None" else size

    if color == "Specialization":
        spec_selection=st.sidebar.selectbox("Select specialization for legend",options=spec_courses_fmt)
        color = spec_courses_fmt[spec_selection]
    else:
        color = None if color=="None" else color
    
    fig = px.scatter(agg, 
                    x=x, 
                    y=y,
                    size=size, 
                    color=color,
                    hover_name=agg["Course Name"], 
                    size_max=50,
                    color_continuous_scale=px.colors.sequential.Viridis,
                    )
                    
    fig.update_layout(legend_title_text='Legend')

    if x in ["Avg. Difficulty","Avg. Rating"]: 
        fig.add_vline(x=3,line_dash="dash", line_color="white")
        fig.update_layout(xaxis_range=[1,5])
    if y in ["Avg. Difficulty","Avg. Rating"]: 
        fig.add_hline(y=3, line_dash="dash", line_color="white")
        fig.update_layout(yaxis_range=[1,5])
    
    fig.update_layout(xaxis_title=x, yaxis_title=y)

    st.write(fig)

if __name__=="__main__":
    main()