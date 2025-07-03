## views/country_view.py
import plotly.express as px
from dash import dash_table, html, dcc
import pandas as pd

def render_continent_view(df: pd.DataFrame):
    if df is None or df.empty:
        return html.Div(
            "No weather data available. Select a continent and click 'Get Weather'.",
            style={"color": "red", 'background-color': 'rgba(255,255,255,0.7)', 'padding': '15px', 'border-radius': '8px'}
        )

    # Determine the selected continent (assuming all rows in df belong to the same continent)
    selected_continent = df['continent'].iloc[0].title() if 'continent' in df.columns and not df.empty else "Selected Continent"

    # --- Bar Chart: Average Temperature by Country in Continent ---
    # Group by country and calculate mean temperature
    avg_temp_by_country = df.groupby('country')['temp_c'].mean().reset_index()


    # --- Scatter Map for Cities in Continent ---
    fig_map = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        color="temp_c",
        hover_name="city",
        size="temp_c",
        projection="natural earth", # 'natural earth' is a good projection for continents
        title=f"Current City Temperatures in {selected_continent}",
        color_continuous_scale=px.colors.sequential.Plasma,
        height=600
    )
    fig_map.update_layout(
        geo=dict(
            showland = True,
            landcolor = "rgb(210, 210, 210)", # Consistent land color
            oceancolor="rgb(150, 190, 230)", # Consistent ocean color
            showocean=True,
            countrycolor = "rgb(100, 100, 100)", # Consistent country border color
            subunitcolor="rgb(180, 180, 180)", # Consistent subunit border color
            bgcolor='rgba(0,0,0,0)', # Transparent geo background
            fitbounds="locations", # <--- CRUCIAL: Auto-zoom to the data points (cities in the continent)
            resolution=50 # Add resolution for better map detail (110 for higher resolution)
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)', # Make Plotly paper background transparent
        plot_bgcolor='rgba(0,0,0,0)'  # Make Plotly plot background transparent
    )

    return html.Div([
        html.H4(f"Weather in {selected_continent}", className="mb-3 text-center", style={'color': '#444'}),
        dcc.Graph(figure=fig_map, className="mb-4"),
    ], style={'background-color': 'rgba(255,255,255,0.4)', 'border-radius': '8px', 'padding': '15px'})