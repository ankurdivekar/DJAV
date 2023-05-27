# streamlit_app.py

import streamlit as st
import pandas as pd
from google.oauth2 import service_account
# from shillelagh.backends.apsw.db import connect
from gsheetsdb import connect
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.colored_header import colored_header

st.set_page_config(layout="wide", page_title="DJ AV's Sets", page_icon=":headphones:", initial_sidebar_state="auto", menu_items=None)

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

# Perform SQL query on the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1).fetchall()
    return pd.DataFrame.from_dict(data=rows)

with st.spinner("Connecting to GSheets..."):
    with connect(credentials=credentials) as conn:
        # st.write(conn)

        sheet_url = st.secrets["geolocations_url"]
        df_geoloc = run_query(f'SELECT * FROM "{sheet_url}"')

        sheet_url = st.secrets["sets_url"]
        df_sets = run_query(f'SELECT * FROM "{sheet_url}"')
        
        df = (df_sets.merge(df_geoloc, on=["Venue", "Area"], how='left'))

        df['latitude'] = pd.to_numeric(df.Latitude, errors='coerce')
        df['longitude'] = pd.to_numeric(df.Longitude, errors='coerce')
        df = df.drop(columns=["Comments", "Payments", "Latitude", "Longitude"])
        # st.dataframe(df)

colored_header(
    label=":headphones: DJ AV's sets",
    description="Built with :heart: by [DJ AV](https://instagram.com/raagarock)",
    color_name="red-70",
)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="Sets played", value=df.shape[0])
col2.metric(label="Venues played at", value=df.VenueFullName.nunique())
col3.metric(label="Events played at", value=df.Event.nunique())
col4.metric(label="Organizers worked with", value=df.Organizer.nunique())
# col5.metric(label="Organizers worked with", value=df.Organizer.nunique())
style_metric_cards()
# st.write(df.columns)
# st.write(df.dtypes)
# st.dataframe(df.query("latitude.isna()"))
# st.dataframe(df.query("longitude.isna()"))

st.markdown("### By Location")
st.map(df, use_container_width=True)