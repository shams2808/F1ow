import streamlit as st
import boto3
import pandas as pd
from io import BytesIO

BUCKET_NAME = "f1ow-data-417521971713"

st.set_page_config(
    page_title="F1ow Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_driver_performance():
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=BUCKET_NAME, Key="gold/driver_performance/driver_performance.parquet")
    return pd.read_parquet(BytesIO(response['Body'].read()))

@st.cache_data
def load_constructor_performance():
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=BUCKET_NAME, Key="gold/constructor_performance/constructor_performance.parquet")
    return pd.read_parquet(BytesIO(response['Body'].read()))

df_drivers = load_driver_performance()
df_constructors = load_constructor_performance()

st.title("🏎️ F1ow Dashboard")
st.markdown("### Formula 1 Data Analytics — 2023 to 2025")
st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🗓️ Seasons", "3")
with col2:
    st.metric("🏁 Total Races", "70")
with col3:
    st.metric("👤 Drivers", df_drivers['driverid'].nunique())
with col4:
    st.metric("🏎️ Constructors", df_constructors['constructorid'].nunique())

st.divider()
st.markdown("### 📌 Navigate using the sidebar to explore:")
st.markdown("""
- 🏆 **Driver Performance** — wins, points, podiums per driver
- 🏎️ **Constructor Performance** — team comparison across seasons  
- 🏁 **Race Results** — race winners by season and round
""")