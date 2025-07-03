import requests
import pandas as pd
import numpy as np
from datetime import date
import os

API_KEY = os.getenv("API_KEY")
BASE_URL_CURRENT = os.getenv("BASE_URL_CURRENT")
BASE_URL_FORECAST = os.getenv("BASE_URL_FORECAST")

def get_continents(df):
    return list(df['continent'].unique())

def get_countries(df):
    return list(df['country'].unique())

def get_countries_by_continent(df, selected_continent):
    if not selected_continent:
        return []
    countries = sorted(df[df["continent"] == selected_continent]["country"].unique())
    return [{"label": c.title(), "value": c} for c in countries]

def get_regions_by_country(df, selected_country):
    if not selected_country:
        return []
    regions = sorted(df[df["country"] == selected_country]["region"].unique())
    return [{"label": c.title(), "value": c} for c in regions]

def get_cities_by_region(df, selected_country, selected_region):
    if not selected_country or not selected_region:
        return []
    cities = sorted(df[np.logical_and(df["country"] == selected_country, df['region'] == selected_region)]["city"].unique())
    return [{"label": c.title(), "value": c} for c in cities]

def extract_row(data):
    new_data = {
        "city":data['location']['name'],
        "region":data["location"]["region"],
        "country":data["location"]["country"],
        "lat":data["location"]["lat"],
        "lon":data["location"]["lon"],
        "date":date.today().isoformat(),
        "temp_c":data["current"]["temp_c"],
        "temp_f":data["current"]["temp_f"],
        "is_day":data["current"]["is_day"],
        "condition_text":data["current"]["condition"]["text"],
        "condition_icon":data["current"]["condition"]["icon"],
        "wind_mph":data["current"]["wind_mph"],
        "wind_kph":data["current"]["wind_kph"],
        "wind_degree":data["current"]["wind_degree"],
        "wind_dir":data["current"]["wind_dir"],
        "pressure_mb":data["current"]["pressure_mb"],
        "pressure_in":data["current"]["pressure_in"],
        "precip_mm":data["current"]["precip_mm"],
        "precip_in":data["current"]["precip_in"],
        "humidity":data["current"]["humidity"],
        "cloud":data["current"]["cloud"],
        "feelslike_c":data["current"]["feelslike_c"],
        "feelslike_f":data["current"]["feelslike_f"],
        "windchill_c":data["current"]["windchill_c"],
        "windchill_f":data["current"]["windchill_f"],
        "heatindex_c":data["current"]["heatindex_c"],
        "heatindex_f":data["current"]["heatindex_f"],
        "dewpoint_c":data["current"]["dewpoint_c"],
        "dewpoint_f":data["current"]["dewpoint_f"],
        "vis_km":data["current"]["vis_km"],
        "vis_miles":data["current"]["vis_miles"],
        "uv":data["current"]["uv"],
        "gust_mph":data["current"]["gust_mph"],
        "gust_kph":data["current"]["gust_kph"]
    }
    return new_data

def extract_hourly_forecast(json_data):
    hours_data = []

    forecast_days = json_data.get("forecast", {}).get("forecastday", [])
    for day in forecast_days:
        date = day.get("date")
        for hour in day.get("hour", []):
            condition = hour.pop("condition", {})
            hour_data = {
                "forecast_date": date,
                "time_epoch": hour.get("time_epoch"),
                "time": hour.get("time"),
                "temp_c": hour.get("temp_c"),
                "temp_f": hour.get("temp_f"),
                "is_day": hour.get("is_day"),
                "condition_text": condition.get("text"),
                "condition_icon": condition.get("icon"),
                "condition_code": condition.get("code"),
                "wind_mph": hour.get("wind_mph"),
                "wind_kph": hour.get("wind_kph"),
                "wind_degree": hour.get("wind_degree"),
                "wind_dir": hour.get("wind_dir"),
                "pressure_mb": hour.get("pressure_mb"),
                "pressure_in": hour.get("pressure_in"),
                "precip_mm": hour.get("precip_mm"),
                "precip_in": hour.get("precip_in"),
                "humidity": hour.get("humidity"),
                "cloud": hour.get("cloud"),
                "feelslike_c": hour.get("feelslike_c"),
                "feelslike_f": hour.get("feelslike_f"),
                "windchill_c": hour.get("windchill_c"),
                "windchill_f": hour.get("windchill_f"),
                "heatindex_c": hour.get("heatindex_c"),
                "heatindex_f": hour.get("heatindex_f"),
                "dewpoint_c": hour.get("dewpoint_c"),
                "dewpoint_f": hour.get("dewpoint_f"),
                "will_it_rain": hour.get("will_it_rain"),
                "chance_of_rain": hour.get("chance_of_rain"),
                "will_it_snow": hour.get("will_it_snow"),
                "chance_of_snow": hour.get("chance_of_snow"),
                "vis_km": hour.get("vis_km"),
                "vis_miles": hour.get("vis_miles"),
                "gust_mph": hour.get("gust_mph"),
                "gust_kph": hour.get("gust_kph"),
                "uv": hour.get("uv")
            }
            hours_data.append(hour_data)

    df = pd.DataFrame(hours_data)
    return df

def get_city_forecast(df_city_info, step_callback=None): # Renamed df to df_city_info for clarity
    if df_city_info.empty:
        return None

    # Get lat/lon from the provided df_city_info (which should be from get_data_incremental or similar)
    lat = df_city_info.iloc[0]['lat']
    lon = df_city_info.iloc[0]['lon']

    url = f"{BASE_URL_FORECAST}?key={API_KEY}&q={lat},{lon}&days=3"

    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        weather_df = extract_hourly_forecast(weather_data)

        # --- IMPORTANT ADDITION ---
        # Extract location details from the forecast API response itself
        location_data = weather_data.get('location', {})
        location_lat = location_data.get('lat')
        location_lon = location_data.get('lon')
        city_name = location_data.get('name')
        country_name = location_data.get('country')
        region_name = location_data.get('region')

        # Add these details as new columns to the hourly forecast DataFrame
        # This makes them available for render_city_view
        weather_df['lat'] = location_lat
        weather_df['lon'] = location_lon
        weather_df['city'] = city_name
        weather_df['country'] = country_name
        weather_df['region'] = region_name
        # --- END IMPORTANT ADDITION ---

    except Exception as e:
        print(f"Error fetching city forecast data: {e}")
        return None

    if step_callback:
        step_callback(100)

    return weather_df # This DataFrame now includes 'lat', 'lon', 'city', 'country', 'region'

def get_data_incremental(df, step_callback=None):
    data = []
    total = len(df)

    for i, row in df.iterrows():
        lat = row['lat']
        lon = row['lon']
        url = f"{BASE_URL_CURRENT}?key={API_KEY}&q={lat},{lon}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                weather_data = response.json()
                processed = extract_row(weather_data)
                data.append(processed)
        except Exception as e:
            print(e)

        if step_callback:
            step_callback((i + 1) / total * 100)

    return pd.DataFrame(data)