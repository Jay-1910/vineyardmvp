import geopandas as gpd
import folium
from streamlit_folium import st_folium
import streamlit as st
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
import pytz
from datetime import datetime, timedelta
import plotly.graph_objects as go
from shapely.geometry import Point

st.set_page_config(layout="wide",page_title="Vineyard MVP")

padding_top = 0
st.markdown(f"""
    <style>
        .reportview-container .main .block-container{{
            padding-top: {padding_top}rem;
        }}
    </style>""",
    unsafe_allow_html=True,
)
reduce_header_height_style = """
    <style>
        div.block-container {padding-top:1rem;}
    </style>
"""
st.markdown(reduce_header_height_style, unsafe_allow_html=True)
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

hide_deploy_button_style = """
    <style>
        .stDeployButton {
            display: none !important;
        }
    </style>
"""
st.markdown(hide_deploy_button_style, unsafe_allow_html=True)


df_m = gpd.read_file("bm10.geojson")
df_l = gpd.read_file("bl9.geojson")
df_p = gpd.read_file("bp13.geojson")

df_m = df_m.to_crs(epsg=4326)
df_l = df_l.to_crs(epsg=4326)
df_p = df_p.to_crs(epsg=4326)

dfm = gpd.read_file("bm10.geojson")
dfl = gpd.read_file("bl9.geojson")
dfp = gpd.read_file("bp13.geojson")

dfm = dfm.to_crs(epsg=4326)
dfl = dfl.to_crs(epsg=4326)
dfp = dfp.to_crs(epsg=4326)

def mean_loc(df):
    if len(df) == 0:
        raise ValueError("Null data")

    lat_sum = 0
    lon_sum = 0
    total_coords = 0

    for geometry in df['geometry']:
        if isinstance(geometry, Polygon):
            coordinates = list(geometry.exterior.coords)
            for lat, lon in coordinates:
                lat_sum += lat
                lon_sum += lon
                total_coords += 1

    if total_coords == 0:
        raise ValueError("No valid coordinates found.")

    mean_lat = lat_sum / total_coords
    mean_lon = lon_sum / total_coords

    return mean_lat, mean_lon

def show_map(df_x, m_x):
    for _, r in df_x.iterrows():
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        if r["name"] == "Block M10 CHA":
            geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "red", "fillOpacity": 0.2})
        else:
            geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "green", "fillOpacity": 0.1})
        geo_j.add_to(m_x)
    return m_x

def show_map_1(df_x, m_x):
    for _, r in df_x.iterrows():
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        if r["name"] == "Block M10 CHA":
            geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "red", "fillOpacity": 0.3})
        else:
            geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "green", "fillOpacity": 0.1})
        folium.Popup(r["name"]).add_to(geo_j)
        geo_j.add_to(m_x)
          
        df_x = df_x.to_crs(epsg=2263)
        df_x["centroid"] = df_x.centroid
        df_x = df_x.to_crs(epsg=4326)
        df_x["centroid"] = df_x["centroid"].to_crs(epsg=4326)
    
    for _, r in df_x.iterrows():
        lat = r["centroid"].y
        lon = r["centroid"].x
        iframe = folium.IFrame('Area:' + str(r['name']))
        popup = folium.Popup(iframe, min_width=90, max_width=90)
        folium.Marker(
            location=[lat, lon],
            popup=popup,
        ).add_to(m_x)
    return m_x

def get_pos(lat, lng):
    return lat, lng

column1, column2 = st.columns([1,3])

with column1:
    st.header("🍇Vineyard MVP")

with column2:
    col1, col2, col3, col4, col5 = st.columns(5)    
    with col2:
        st.metric("Current Temperature", f"{21} °C", f"{3} °C")        
    with col3:
        st.metric("Current Humidity", f"{60} %", f"{-5} %")       
    with col4:
        st.metric("Current Pressure", f"{14.7} PSI", f"{0.7} PSI")
    with col5:
        st.metric("Current UV Index", f"{7}", f"{2}")
        
cc1, cc2, cc3, cc4, cc5, cc6, cc7 = st.columns(7)
sa_timezone = pytz.timezone('Australia/Adelaide')
current_datetime = datetime.now(sa_timezone)
date_format = current_datetime.strftime("%d of %B, %Y")
time_format = current_datetime.strftime("%I:%M %p")
am_or_pm = current_datetime.strftime("%p")
am_or_pm = am_or_pm.lower()

with cc1:
    st.markdown(f"**Date:** {date_format}")
with cc2:
    st.markdown(f"**Time:** {time_format}")

    st.markdown(" ")

config = {'displayModeBar': False}
coll1, coll2 = st.columns([5.9, 4.1]) 

with coll1: 
    st.subheader("🗺️Map")
    
with coll2: 
    st.subheader("💧Soil Moisture Forecasts") 
    
coll11, coll22 = st.columns([5.5, 4.5]) 
with coll11:
    c1, c2, c3 = st.columns(3)
    with c1:    
        b1 = st.checkbox("Block M10", value=True)
    with c2:    
        b2 = st.checkbox("Block L9", value=True)
    with c3:    
        b3 = st.checkbox("Block P13", value=True)

selected_dfs = []
if b1:
    selected_dfs.append(df_m)
if b2:
    selected_dfs.append(df_l)
if b3:
    selected_dfs.append(df_p)

if len(selected_dfs) == 0:
    st.warning("Please select at least one Block.")

else:
    merged_df = pd.concat(selected_dfs)
    x, y = mean_loc(merged_df)

    if len(merged_df) == 4:
        y, x = -34.816, 138.9805

    m = folium.Map(location=[y,x], zoom_start=16, tiles="https://api.mapbox.com/styles/v1/jay3119/cln17raax003h01rc4uc243dc/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamF5MzExOSIsImEiOiJjbGoyZnN1Mmkwb3J1M2htZWRsZjI0dXM0In0.ymSU9tFH2HwFDOlIcY9pLg", attr='Mapbox Light')

if b1:
    show_map(df_m, m)
if b2:
    show_map(df_l, m)
if b3:
    show_map(df_p, m)

b = None
if len(selected_dfs) > 0:
    bbox = merged_df.total_bounds
    m.fit_bounds([[bbox[1], bbox[0]], [bbox[3], bbox[2]]])
    if b is None:
        with coll1:
            map = st_folium(m, height=350, width=700)
            lat = None
            long = None
            if map.get("last_clicked"):
                lat, long = get_pos(map["last_clicked"]["lat"], map["last_clicked"]["lng"])

            if lat is not None and long is not None:
                p = Point(long, lat)
                for index, row in df_m.iterrows():
                    polygon = row['geometry']
                    if polygon.contains(p):
                        b = "m"
                for index, row in df_l.iterrows():
                    polygon = row['geometry']
                    if polygon.contains(p):
                        b = "l"
                for index, row in df_p.iterrows():
                    polygon = row['geometry']
                    if polygon.contains(p):
                        b = "p"
#     if b is not None:
#         map = None
#         if b == "m":
#             st.write("inside")
#             x, y = mean_loc(dfm)
#             m1 = folium.Map(location=[y,x], zoom_start=16, tiles="https://api.mapbox.com/styles/v1/jay3119/cln17raax003h01rc4uc243dc/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamF5MzExOSIsImEiOiJjbGoyZnN1Mmkwb3J1M2htZWRsZjI0dXM0In0.ymSU9tFH2HwFDOlIcY9pLg", attr='Mapbox Light')
#             show_map_1(dfm, m1)
            
#         if b == "l":
#             x, y = mean_loc(dfl)
#             m1 = folium.Map(location=[y,x], zoom_start=16, tiles="https://api.mapbox.com/styles/v1/jay3119/cln17raax003h01rc4uc243dc/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamF5MzExOSIsImEiOiJjbGoyZnN1Mmkwb3J1M2htZWRsZjI0dXM0In0.ymSU9tFH2HwFDOlIcY9pLg", attr='Mapbox Light')
#             show_map_1(dfl, m1)
            
#         if b == "p":
#             x, y = mean_loc(dfp)
#             m1 = folium.Map(location=[y,x], zoom_start=16, tiles="https://api.mapbox.com/styles/v1/jay3119/cln17raax003h01rc4uc243dc/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamF5MzExOSIsImEiOiJjbGoyZnN1Mmkwb3J1M2htZWRsZjI0dXM0In0.ymSU9tFH2HwFDOlIcY9pLg", attr='Mapbox Light')
#             show_map_1(dfp, m1)
            
#         with coll1:
#             map = st_folium(m1, height=350, width=700)
            
            
                
    
if len(selected_dfs) > 0:
    st.subheader("🚨Alerts")
    st.markdown("**1. Zone M10 needs water**")
    st.markdown("**2. Zone L9 will need water after 5 hours**")
    sa_timezone = pytz.timezone('Australia/Adelaide')
    current_datetime = datetime.now(sa_timezone)
    date_format = current_datetime.strftime("%d of %B, %Y")
    time_format = current_datetime.strftime("%I:%M %p")
    am_or_pm = current_datetime.strftime("%p")
    am_or_pm = am_or_pm.lower()
    
    
    soil_moisture_data_m = {
    'Soil Moisture (%)': [72, 64, 52, 46, 39]}
    soil_moisture_df_m = pd.DataFrame(soil_moisture_data_m)
    time_differences = [current_datetime - timedelta(hours=i * 2) for i in range(len(soil_moisture_df_m))]
    time_differences = time_differences[::-1]
    soil_moisture_df_m['time'] = [time.strftime('%H:%M:%S') for time in time_differences]
    forecast_time_differences = [current_datetime] + [current_datetime + timedelta(hours=i * 2) for i in range(1, 4)]
    forecasted_soil_moisture_data_m = {
    'Soil Moisture (%)': [39, 34, 27, 21]}
    forecasted_soil_moisture_df_m = pd.DataFrame(forecasted_soil_moisture_data_m)
    forecasted_soil_moisture_df_m['time'] = [time.strftime('%H:%M:%S') for time in forecast_time_differences]
    
    soil_moisture_data_l = {
    'Soil Moisture (%)': [90, 87, 70, 63, 54]}
    soil_moisture_df_l = pd.DataFrame(soil_moisture_data_l)
    time_differences = [current_datetime - timedelta(hours=i * 2) for i in range(len(soil_moisture_df_l))]
    time_differences = time_differences[::-1]
    soil_moisture_df_l['time'] = [time.strftime('%H:%M:%S') for time in time_differences]
    forecast_time_differences = [current_datetime] + [current_datetime + timedelta(hours=i * 2) for i in range(1, 4)]
    forecasted_soil_moisture_data_l = {
    'Soil Moisture (%)': [54,47,41,28]}
    forecasted_soil_moisture_df_l = pd.DataFrame(forecasted_soil_moisture_data_l)
    forecasted_soil_moisture_df_l['time'] = [time.strftime('%H:%M:%S') for time in forecast_time_differences]
    
    soil_moisture_data_p = {
    'Soil Moisture (%)': [93, 88, 80, 74, 66]}
    soil_moisture_df_p = pd.DataFrame(soil_moisture_data_p)
    time_differences = [current_datetime - timedelta(hours=i * 2) for i in range(len(soil_moisture_df_p))]
    time_differences = time_differences[::-1]
    soil_moisture_df_p['time'] = [time.strftime('%H:%M:%S') for time in time_differences]
    forecast_time_differences = [current_datetime] + [current_datetime + timedelta(hours=i * 2) for i in range(1, 4)]
    forecasted_soil_moisture_data_p = {
    'Soil Moisture (%)': [66,59,53,44]}
    forecasted_soil_moisture_df_p = pd.DataFrame(forecasted_soil_moisture_data_p)
    forecasted_soil_moisture_df_p['time'] = [time.strftime('%H:%M:%S') for time in forecast_time_differences]
    
    if b=="m":
        fig = go.Figure()
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_m['time'],
            y=soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block M',
            line=dict(color='blue') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_m['time'],
            y=forecasted_soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block M',
            line=dict(dash='dot', color='blue') 
            )
        )
        fig.add_shape(
        dict(
            type='line',
            x0=soil_moisture_df_m['time'].iloc[0],
            x1=forecasted_soil_moisture_df_m['time'].iloc[-1], 
            y0=40,
            y1=40,
            line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)
     
    elif b=="l":
        fig = go.Figure()
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_l['time'],
            y=soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block L',
            line=dict(color='green') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_l['time'],
            y=forecasted_soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block L',
            line=dict(dash='dot', color='green') 
            )
        )
        fig.add_shape(
        dict(
            type='line',
            x0=soil_moisture_df_l['time'].iloc[0],
            x1=forecasted_soil_moisture_df_l['time'].iloc[-1], 
            y0=40,
            y1=40,
            line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)
        
    elif b=="p":       
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=soil_moisture_df_p['time'],
                y=soil_moisture_df_p['Soil Moisture (%)'],
                mode='lines',
                name='Soil Moisture for Block P',
                line=dict(color='purple') 
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecasted_soil_moisture_df_p['time'],
                y=forecasted_soil_moisture_df_p['Soil Moisture (%)'],
                mode='lines+markers',  
                name='Forecasted Soil Moisture for Block P',
                line=dict(dash='dot', color='purple') 
            )
        )
        fig.add_shape(
            dict(
                type='line',
                x0=soil_moisture_df_p['time'].iloc[0],
                x1=forecasted_soil_moisture_df_p['time'].iloc[-1], 
                y0=40,
                y1=40,
                line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)
    
                        
    elif b1 and b2 and b3:
        fig = go.Figure()
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_m['time'],
            y=soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block M',
            line=dict(color='blue') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_m['time'],
            y=forecasted_soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block M',
            line=dict(dash='dot', color='blue') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_l['time'],
            y=soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block L',
            line=dict(color='green') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_l['time'],
            y=forecasted_soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block L',
            line=dict(dash='dot', color='green') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_p['time'],
            y=soil_moisture_df_p['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block P',
            line=dict(color='purple') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_p['time'],
            y=forecasted_soil_moisture_df_p['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block P',
            line=dict(dash='dot', color='purple') 
            )
        )
        
        fig.add_shape(
        dict(
            type='line',
            x0=soil_moisture_df_m['time'].iloc[0],
            x1=forecasted_soil_moisture_df_m['time'].iloc[-1], 
            y0=40,
            y1=40,
            line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)
        
    elif b1 and b2:
        fig = go.Figure()
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_m['time'],
            y=soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block M',
            line=dict(color='blue') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_m['time'],
            y=forecasted_soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block M',
            line=dict(dash='dot', color='blue') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_l['time'],
            y=soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block L',
            line=dict(color='green') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_l['time'],
            y=forecasted_soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block L',
            line=dict(dash='dot', color='green') 
            )
        )
        
        fig.add_shape(
        dict(
            type='line',
            x0=soil_moisture_df_m['time'].iloc[0],
            x1=forecasted_soil_moisture_df_m['time'].iloc[-1], 
            y0=40,
            y1=40,
            line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)
        
    elif b2 and b3:
        fig = go.Figure()
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_l['time'],
            y=soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block L',
            line=dict(color='green') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_l['time'],
            y=forecasted_soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block L',
            line=dict(dash='dot', color='green') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_p['time'],
            y=soil_moisture_df_p['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block P',
            line=dict(color='purple') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_p['time'],
            y=forecasted_soil_moisture_df_p['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block P',
            line=dict(dash='dot', color='purple') 
            )
        )
        
        fig.add_shape(
        dict(
            type='line',
            x0=soil_moisture_df_l['time'].iloc[0],
            x1=forecasted_soil_moisture_df_l['time'].iloc[-1], 
            y0=40,
            y1=40,
            line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)
            
    elif b1 and b3:
        fig = go.Figure()
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_m['time'],
            y=soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block M',
            line=dict(color='blue') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_m['time'],
            y=forecasted_soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block M',
            line=dict(dash='dot', color='blue') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_p['time'],
            y=soil_moisture_df_p['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block P',
            line=dict(color='purple') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_p['time'],
            y=forecasted_soil_moisture_df_p['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block P',
            line=dict(dash='dot', color='purple') 
            )
        )
        
        fig.add_shape(
        dict(
            type='line',
            x0=soil_moisture_df_m['time'].iloc[0],
            x1=forecasted_soil_moisture_df_m['time'].iloc[-1], 
            y0=40,
            y1=40,
            line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)
            
        
    elif b1:
        fig = go.Figure()
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_m['time'],
            y=soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block M',
            line=dict(color='blue') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_m['time'],
            y=forecasted_soil_moisture_df_m['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block M',
            line=dict(dash='dot', color='blue') 
            )
        )
        fig.add_shape(
        dict(
            type='line',
            x0=soil_moisture_df_m['time'].iloc[0],
            x1=forecasted_soil_moisture_df_m['time'].iloc[-1], 
            y0=40,
            y1=40,
            line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)
        
    elif b2:
        fig = go.Figure()
        fig.add_trace(
        go.Scatter(
            x=soil_moisture_df_l['time'],
            y=soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines',
            name='Soil Moisture for Block L',
            line=dict(color='green') 
            )
        )
        fig.add_trace(
        go.Scatter(
            x=forecasted_soil_moisture_df_l['time'],
            y=forecasted_soil_moisture_df_l['Soil Moisture (%)'],
            mode='lines+markers',  
            name='Forecasted Soil Moisture for Block L',
            line=dict(dash='dot', color='green') 
            )
        )
        fig.add_shape(
        dict(
            type='line',
            x0=soil_moisture_df_l['time'].iloc[0],
            x1=forecasted_soil_moisture_df_l['time'].iloc[-1], 
            y0=40,
            y1=40,
            line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)
        
    elif b3:       
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=soil_moisture_df_p['time'],
                y=soil_moisture_df_p['Soil Moisture (%)'],
                mode='lines',
                name='Soil Moisture for Block P',
                line=dict(color='purple') 
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecasted_soil_moisture_df_p['time'],
                y=forecasted_soil_moisture_df_p['Soil Moisture (%)'],
                mode='lines+markers',  
                name='Forecasted Soil Moisture for Block P',
                line=dict(dash='dot', color='purple') 
            )
        )
        fig.add_shape(
            dict(
                type='line',
                x0=soil_moisture_df_p['time'].iloc[0],
                x1=forecasted_soil_moisture_df_p['time'].iloc[-1], 
                y0=40,
                y1=40,
                line=dict(color='red', width=2),
            )
        )
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title='Soil Moisture (%)',
            height=400,
            width=600,
            margin={
                'l': 60,
                'r': 10,
                'b': 0,
                't': 10,
                'pad': 2
            }
        )
        st.markdown("""
        <style>
        h1 {
            margin: 0px;
        }
        </style>
        """, unsafe_allow_html=True)
        with coll2:
            st.plotly_chart(fig, config=config)

    