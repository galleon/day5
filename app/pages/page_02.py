import os
from datetime import date, datetime, time

import folium
import requests
import streamlit as st
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

NYC_CENTER = [40.7580, -73.9855]  # Times Square


@st.cache_data(show_spinner=False)
def geocode(address: str):
    geolocator = Nominatim(user_agent="taxifare-day5")
    location = geolocator.geocode(f"{address}, New York City")
    if location:
        return location.latitude, location.longitude
    return None


@st.cache_data(show_spinner=False)
def get_road_route(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon):
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{pickup_lon},{pickup_lat};{dropoff_lon},{dropoff_lat}"
        f"?overview=full&geometries=geojson"
    )
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    coords = r.json()["routes"][0]["geometry"]["coordinates"]
    return [[lat, lon] for lon, lat in coords]  # OSRM returns [lon, lat], folium needs [lat, lon]


st.title("NYC Taxi Fare Estimator")

col1, col2 = st.columns(2)
with col1:
    pickup_address = st.text_input("Pickup location", "Times Square, Manhattan")
with col2:
    dropoff_address = st.text_input("Dropoff location", "JFK Airport, Queens")

col3, col4, col5 = st.columns([2, 1, 1])
with col3:
    pickup_date = st.date_input("Date", date.today())
with col4:
    pickup_time = st.time_input("Time", time(9, 0))
with col5:
    passengers = st.slider("Passengers", 1, 6, 1)

pickup_datetime = datetime.combine(pickup_date, pickup_time)

if st.button("Estimate Fare", type="primary", use_container_width=True):
    with st.spinner("Finding locations..."):
        pickup_coords = geocode(pickup_address)
        dropoff_coords = geocode(dropoff_address)

    if not pickup_coords:
        st.error(f"Could not find: {pickup_address}")
        st.stop()
    if not dropoff_coords:
        st.error(f"Could not find: {dropoff_address}")
        st.stop()

    st.session_state["pickup_coords"] = pickup_coords
    st.session_state["dropoff_coords"] = dropoff_coords

    with st.spinner("Computing road route..."):
        try:
            route = get_road_route(*pickup_coords, *dropoff_coords)
            st.session_state["route"] = route
        except Exception as e:
            st.session_state["route"] = None
            st.warning(f"Could not fetch route: {e}")

    api_url = os.environ.get("API_URL", "http://localhost:8080")
    with st.spinner("Estimating fare..."):
        try:
            resp = requests.get(
                f"{api_url}/predict",
                params={
                    "pickup_datetime": pickup_datetime.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "pickup_longitude": pickup_coords[1],
                    "pickup_latitude": pickup_coords[0],
                    "dropoff_longitude": dropoff_coords[1],
                    "dropoff_latitude": dropoff_coords[0],
                    "passenger_count": passengers,
                },
                timeout=10,
            )
            resp.raise_for_status()
            st.session_state["fare"] = resp.json().get("fare")
        except Exception as e:
            st.session_state["fare"] = None
            st.warning(f"API unavailable — is the taxifare API running? ({e})")

if st.session_state.get("fare") is not None:
    st.success(f"Estimated fare: **${st.session_state['fare']:.2f}**")

# Map
m = folium.Map(location=NYC_CENTER, zoom_start=12, tiles="CartoDB positron")

if "pickup_coords" in st.session_state:
    folium.Marker(
        st.session_state["pickup_coords"],
        tooltip="Pickup",
        icon=folium.Icon(color="green", icon="flag"),
    ).add_to(m)

if "dropoff_coords" in st.session_state:
    folium.Marker(
        st.session_state["dropoff_coords"],
        tooltip="Dropoff",
        icon=folium.Icon(color="red", icon="flag"),
    ).add_to(m)

if st.session_state.get("route"):
    folium.PolyLine(
        st.session_state["route"],
        color="#2563eb",
        weight=5,
        opacity=0.85,
    ).add_to(m)
    m.fit_bounds([
        st.session_state["pickup_coords"],
        st.session_state["dropoff_coords"],
    ])

st_folium(m, width="100%", height=520, returned_objects=[])
