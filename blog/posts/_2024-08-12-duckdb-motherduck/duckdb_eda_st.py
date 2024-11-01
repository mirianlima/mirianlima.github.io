# TODOs
    # 1. Bulk downloads: WDI, COMTRADE, UN
    # 2. Add agg.: by region cats (UN ones )



#Importing the necessary packages
import duckdb
import pandas as pd
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer
from itables.streamlit import interactive_table
import ydata_profiling
from streamlit_pandas_profiling import st_profile_report

# SETUP

st.set_page_config(page_title="🦆 DuckDB Explorer | Streamlit", page_icon=None, layout="wide")

con = duckdb.connect()

# SIDEBAR

ft = st.sidebar.selectbox("Select a Dataset",[
    "Country-level Demographic Data (premium labor)",
    "Country-level Demographic Data", 
    "Country and Single Age Fertility Data"
])

start_year, end_year = st.sidebar.slider("Select a year range", min_value=2020, max_value=2060, step=1, value=(2024, 2030))

regions = st.sidebar.multiselect("Select regions", ["Africa", "Americas", "Asia", "Europe", "Oceania"], default=["Africa"])

vis_select = st.sidebar.checkbox("Add visual exploration")

profile_select = st.sidebar.checkbox("Add data profile")

# DATA

@st.cache_data
def duckdb(tbl, start_year, end_year, regions):

    if not regions:
        return pd.DataFrame()

    regions_str = ", ".join(f"'{region}'" for region in regions)

    ### SQL version

    # data = con.execute(f"""
    #     SELECT *
    #     FROM read_csv_auto('{base_path}{tbl}.csv')
    #     WHERE "time" BETWEEN {start_year} AND {end_year}
    #     AND "region" IN ({regions_str})
    # """).df()

    ### Relational API version
    
    data = con.read_csv(f'data/{tbl}.csv') \
        .filter(f'time BETWEEN {start_year} AND {end_year}') \
        .filter(f"region IN ({regions_str})") \
        .df()
    
    return data

if ft == "Country-level Demographic Data (premium labor)":
    data = duckdb('c_dem_premium', start_year, end_year, regions)
elif ft == "Country-level Demographic Data":
    data = duckdb('c_dem', start_year, end_year, regions)
elif ft == "Country and Single Age Fertility Data":
    data = duckdb('c_age1', start_year, end_year, regions)

# MAIN PANEL

st.header("Explore Large Files with 🦆db")

st.write("## 1. Download Data")

interactive_table(data, 
                buttons=["pageLength","copyHtml5", "csvHtml5", "excelHtml5", "colvis"],
                classes=["display", "nowrap", "compact", "cell-border", "stripe"],
                style="table-layout:auto;width:auto;margin:auto;caption-side:bottom")

if vis_select:

    st.write( '## 3. Visual Insights ')

    pyg_app = StreamlitRenderer(data)
    pyg_app.explorer()

if profile_select:

    st.write( '## 4. Data Profile Report')

    pr = data.profile_report()
    st_profile_report(pr, navbar=True)