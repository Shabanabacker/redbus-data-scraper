import mysql.connector
import streamlit as st
import pandas as pd
from datetime import timedelta

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="REDBUS"
    )

def get_data(query):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    con.close()
    return pd.DataFrame(rows)

def format_timedelta(td):
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}"
    return td

st.title("Redbus Routes Data")

query = "SELECT * FROM bus_route"
data = get_data(query)

# Convert departingtime and reachingtime
data['departingtime'] = data['departingtime'].apply(format_timedelta)
data['reachingtime'] = data['reachingtime'].apply(format_timedelta)

# Filters
routes = data['routename'].unique()
bus_names = data['busname'].unique()
bus_types = data['bustype'].unique()
star_ratings = data['starrating'].unique()

selected_route = st.sidebar.multiselect('Select Route', routes)
selected_bus_name = st.sidebar.multiselect('Select Bus Name', bus_names)
selected_bus_type = st.sidebar.multiselect('Select Bus Type', bus_types)

price_range = st.sidebar.slider('Select Price Range', 
                                min_value=int(data['price'].min()), 
                                max_value=int(data['price'].max()), 
                                value=(int(data['price'].min()), int(data['price'].max())))
selected_star_rating_range = st.sidebar.slider('Select Star Rating Range', 
                                               min_value=float(data['starrating'].min()), 
                                               max_value=float(data['starrating'].max()), 
                                               value=(float(data['starrating'].min()), float(data['starrating'].max())))
availability = st.sidebar.slider('Select Seat Availability', 
                                 min_value=int(data['seatavailable'].min()), 
                                 max_value=int(data['seatavailable'].max()), 
                                 value=(int(data['seatavailable'].min()), int(data['seatavailable'].max())))

# Apply filters
query = "SELECT * FROM bus_route WHERE 1=1"
if selected_bus_type:
    query += f" AND bustype IN ({', '.join([f'\'{bt}\'' for bt in selected_bus_type])})"
if selected_route:
    query += f" AND routename IN ({', '.join([f'\'{route}\'' for route in selected_route])})"
if selected_bus_name:
    query += f" AND busname IN ({', '.join([f'\'{busname}\'' for busname in selected_bus_name])})"
query += f" AND price BETWEEN {price_range[0]} AND {price_range[1]}"
query += f" AND starrating BETWEEN {selected_star_rating_range[0]} AND {selected_star_rating_range[1]}"
query += f" AND seatavailable BETWEEN {availability[0]} AND {availability[1]}"

filtered_data = get_data(query)

# Convert departingtime and reachingtime for filtered data
filtered_data['departingtime'] = filtered_data['departingtime'].apply(format_timedelta)
filtered_data['reachingtime'] = filtered_data['reachingtime'].apply(format_timedelta)

st.dataframe(filtered_data)