import pandas as pd
import streamlit as st


    
# Read in data from the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
# @st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

df_sets = load_data(st.secrets["sets_url"])
df_venues = load_data(st.secrets["venues_url"])
df = (df_sets.merge(df_venues, on=["Venue", "Area"], how='left')
.rename(columns={"Latitude": 'latitude', "Longitude": 'longitude'})
)

st.markdown("# DJ AV's Sets")

st.write(f"Total sets played: {df.shape[0]}")
st.write(f"Unique venues played at: {df.VenueFullName.nunique()}")
st.write(f"Unique events played at: {df.Event.nunique()}")
st.write(f"Total organizers worked with: {df.Organizer.nunique()}")
st.write(df.columns)

st.markdown("### By Location")

st.map(df, use_container_width=True)