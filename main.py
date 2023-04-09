import pandas as pd
import streamlit as st

from streamlit_extras.metric_cards import style_metric_cards

st.set_page_config(page_title="DJ AV Sets", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None,)
    
# Read in data from the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

df_sets = load_data(st.secrets["sets_url"])
df_venues = load_data(st.secrets["venues_url"])
df = (df_sets.merge(df_venues, on=["Venue", "Area"], how='left')
.rename(columns={"Latitude": 'latitude', "Longitude": 'longitude'})
)

st.markdown("# DJ AV's Sets")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="Sets played", value=df.shape[0])
col2.metric(label="Venues played at", value=df.VenueFullName.nunique())
col3.metric(label="Events played at", value=df.Event.nunique())
col4.metric(label="Organizers worked with", value=df.Organizer.nunique())
# col5.metric(label="Organizers worked with", value=df.Organizer.nunique())
style_metric_cards()

st.write(df.columns)

st.markdown("### By Location")
st.map(df, use_container_width=True)