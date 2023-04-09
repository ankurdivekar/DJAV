import pandas as pd
import streamlit as st

def generate_invite():
    
    pass


st.sidebar.markdown("""---""")
st.sidebar.title("DJ AV Sets")
st.sidebar.markdown("Built with :heart: by [Ankur](https://instagram.com/raagarock)")
st.sidebar.markdown("""---""")


page_names_to_funcs = {
    "Generate Invite": generate_invite,

}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()