import streamlit as st

st.title("About this App")

st.markdown("""
## NYC Taxi Fare Estimator

This app predicts the fare of a New York City taxi ride using a machine learning model
trained on millions of historical NYC taxi trips.

---

### How it works

1. **Enter your pickup and dropoff locations** — type any address or landmark in New York City.
2. **Choose your departure date and time** — fare varies by time of day and day of week.
3. **Select the number of passengers** — up to 6.
4. **Click Estimate Fare** — the app will:
   - Geocode your addresses via OpenStreetMap (Nominatim)
   - Draw the road route on the map via OSRM
   - Call the taxifare prediction API and display the estimated fare

---

### The Model

The underlying model is a neural network trained on the
[NYC Taxi Fare dataset](https://www.kaggle.com/c/new-york-city-taxi-fare-prediction).
It takes into account:

- Pickup and dropoff GPS coordinates
- Haversine distance between the two points
- Date and time of the ride (hour, day of week, month)
- Number of passengers

---

### Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit + Folium |
| Routing | OSRM (OpenStreetMap) |
| Geocoding | Nominatim (OpenStreetMap) |
| Prediction API | FastAPI |
| Model | TensorFlow / Keras |
""")
