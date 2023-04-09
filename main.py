import pandas as pd
import streamlit as st

def generate_invite():
    
    # Read in data from the Google Sheet.
    # Uses st.cache_data to only rerun when the query changes or after 10 min.
    # @st.cache_data(ttl=600)
    def load_data(sheets_url):
        csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
        return pd.read_csv(csv_url)

    df_sets = load_data(st.secrets["sets_url"])
    df_venues = load_data(st.secrets["venues_url"])
    df = df_sets.merge(df_venues, on=["Venue", "Area"], how='left').rename(columns={"Latitude": 'latitude', "Longitude": 'longitude'})

    st.markdown("# DJ AV's Sets")

    st.markdown("### By Location")

    st.map(df, use_container_width=True)


st.sidebar.markdown("""---""")
st.sidebar.title("DJ AV Sets")
st.sidebar.markdown("Built with :heart: by [Ankur](https://instagram.com/raagarock)")
st.sidebar.markdown("""---""")


page_names_to_funcs = {
    "Generate Invite": generate_invite,

}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()