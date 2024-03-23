# streamlit_app.py

import pandas as pd
import plotly.express as px
import streamlit as st
from google.oauth2 import service_account

# from shillelagh.backends.apsw.db import connect
from gsheetsdb import connect
from streamlit_extras.colored_header import colored_header
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.let_it_rain import rain
from streamlit_extras.metric_cards import style_metric_cards

print("Streamlit version:", st.__version__)
st.set_page_config(
    layout="wide",
    page_title="DJ AV's Sets",
    page_icon=":headphones:",
    initial_sidebar_state="auto",
    menu_items=None,
)

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)


# Perform SQL query on the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=60)
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

        df = df_sets.merge(df_geoloc, on=["Venue", "Area"], how="left")

        df["latitude"] = pd.to_numeric(df.Latitude, errors="coerce")
        df["longitude"] = pd.to_numeric(df.Longitude, errors="coerce")
        df = df.drop(columns=["Comments", "Payments", "Latitude", "Longitude"])

        df.Date = pd.to_datetime(
            df.Date,
            format="%Y-%m-%d %H:%M:%S",
            errors="raise",
        )

        df = df.sort_values(by="Date").reset_index(drop=True)
        df["SetNo"] = df.index + 1
        df.index = df.SetNo

        for col in [
            "Event",
            "Organizer",
            # "EventType",
            "VenueFullName",
        ]:
            df[col] = df[col].astype("category")

        # print(
        #     f"No sets for locations:{[v for v in df_geoloc.VenueFullName if v not in df.VenueFullName.unique()]}"
        # )

colored_header(
    label=":headphones: DJ AV's sets",
    description="Built with :heart: by [DJ AV](https://instagram.com/raagarock)",
    color_name="red-70",
)

# Make headphone emojis rain!
rain(
    emoji="🎧",
    font_size=15,
    falling_speed=10,
    animation_length="infinite",
)

# st.write(df.columns)
# st.write(df.head(5))
# print(df.tail(5))
# print(df.dtypes)

err = df.query("latitude.isna() or longitude.isna()")
if len(err):
    st.dataframe(err)
# st.dataframe(df.query("longitude.isna()"))

df_viz = df.drop(columns=["Venue", "Area"])

filtered_df = dataframe_explorer(df_viz, case=False)

if len(filtered_df) > 0:
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    f_col1.metric(label="Sets played", value=filtered_df.shape[0])
    f_col2.metric(label="Venues played at", value=filtered_df.VenueFullName.nunique())
    f_col3.metric(label="Events played at", value=filtered_df.Event.nunique())
    f_col4.metric(label="Organizers worked with", value=filtered_df.Organizer.nunique())
    style_metric_cards()

    st.markdown("## Count of sets by Month & Year")
    dff = (
        filtered_df.assign(
            YearMonth=lambda x: x.Date.dt.strftime("%Y-%m"),
            # MonthYear=lambda x: x.index.strftime("%m-%Y"),
        )
        .groupby(["YearMonth", "EventType"])
        .SetNo.count()
        .reset_index(drop=False)
        .rename(columns={"SetNo": "SetsCount"})
    )
    fig1 = px.bar(
        dff,
        x="YearMonth",
        y="SetsCount",
        color="EventType",
        barmode="stack",
        hover_data=["EventType"],
    )
    # fig1.update_xaxes(tickangle=45)
    st.plotly_chart(fig1, use_container_width=True)

    # # Create distplot with custom bin_size
    # fig2 = px.scatter(
    #     data_frame=filtered_df,
    #     x=filtered_df.index,
    #     y="SetNo",
    #     color="EventType",
    #     # hover_data=["Event"],
    # )
    # st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## Sets by Location")
    st.map(filtered_df, use_container_width=True)

    st.markdown("## Sets Data")
    st.dataframe(
        filtered_df.set_index("SetNo")
        .drop(columns=["latitude", "longitude"])
        .sort_values(by="Date", ascending=False),
        use_container_width=True,
    )
