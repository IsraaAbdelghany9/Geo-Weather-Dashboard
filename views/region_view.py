# views/region_view.py
import plotly.express as px
from dash import html, dcc # Removed dash_table as it's no longer used
import pandas as pd

def render_region_view(df: pd.DataFrame):
    if df is None or df.empty:
        return html.Div(
            "No weather data available. Select a region and click 'Get Weather'.",
            style={"color": "red", 'background-color': 'rgba(255,255,255,0.7)', 'padding': '15px', 'border-radius': '8px'}
        )

    selected_country = df['country'].iloc[0].title() if 'country' in df.columns and not df.empty else "Selected Country"
    selected_region = df['region'].iloc[0].title() if 'region' in df.columns and not df.empty else "Selected Region"

    # --- Scatter Map for Cities in Region ---
    fig_map = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        color="temp_c",
        hover_name="city",
        size="temp_c",
        # Removed scope="world" as fitbounds="locations" handles the zoom
        title=f"Current City Temperatures in {selected_region}, {selected_country}",
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
            subunitcolor="rgb(180, 180, 180)", # Consistent subunit border color (for sub-regions/states)
            bgcolor='rgba(0,0,0,0)', # Transparent geo background
            fitbounds="locations", # <--- CRUCIAL: Auto-zoom to the data points (cities in the region)
            resolution=50 # Add resolution for better map detail
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)', # Make Plotly paper background transparent
        plot_bgcolor='rgba(0,0,0,0)'  # Make Plotly plot background transparent
    )

    return html.Div([
        html.H4(f"Weather in {selected_region}, {selected_country}", className="mb-3 text-center", style={'color': '#444'}),
        dcc.Graph(figure=fig_map, className="mb-4"), # Only the map remains
    ], style={'background-color': 'rgba(255,255,255,0.4)', 'border-radius': '8px', 'padding': '15px'})