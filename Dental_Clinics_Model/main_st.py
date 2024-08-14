import streamlit as st
from pages.dental_streamlit import app as page1_app
from pages.batch_run_streamlit import app as page2_app
from pages.fitting_distribution_streamlit import app as page3_app



PAGES = {
    "Dental Clinic Simulation": page1_app,
    "Batch Run Simulation": page2_app,
    "Data Fitting": page3_app
}

st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

page = PAGES[selection]
page()
