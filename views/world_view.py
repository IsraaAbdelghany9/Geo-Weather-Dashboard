# views/world_view.py

import plotly.express as px
from dash import dash_table, html, dcc
import pandas as pd

def render_world_view(df: pd.DataFrame):
    """
    Renders the world weather view with a scatter geo map and a data table.

    Args:
        df (pd.DataFrame): DataFrame containing the fetched weather data for cities worldwide.
                          Expected columns: 'lat', 'lon', 'city', 'country', 'temp_c', etc.
    """
    if df is None or df.empty:
        return html.Div(
            "No weather data available. Click 'Get Weather' to fetch data.",
            style={"color": "red", "textAlign": "center", "marginTop": "20px", 'background-color': 'rgba(255,255,255,0.7)'} # Added background to this message div
        )

    # --- Global Temperature Map (Scatter Geo) ---
    fig_map = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        color="temp_c",  # Color points by temperature in Celsius
        hover_name="city", # Show city name on hover
        size="temp_c",     # Size points by temperature (optional, adjust as desired)
        projection="orthographic", # Corrected for spherical view
        title="Current City Temperatures Worldwide",
        color_continuous_scale=px.colors.sequential.Plasma, # A vibrant color scale
        height=650
    )

    # --- Customize the Earth's appearance in the map ---
    fig_map.update_layout(
        geo=dict(
            showland=True,
            landcolor="rgb(210, 210, 210)", # Light grey for landmasses
            oceancolor="rgb(150, 190, 230)", # Medium blue for oceans
            showocean=True,
            lakecolor="rgb(180, 220, 250)",
            countrycolor="rgb(100, 100, 100)",
            subunitcolor="rgb(180, 180, 180)",
            bgcolor='rgba(0,0,0,0)',   # Crucial: makes the map background transparent
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)', # Makes the entire graph's paper background transparent
        plot_bgcolor='rgba(0,0,0,0)'  # Makes the plot's background transparent
    )

    return html.Div([ # THIS IS THE OUTER DIV FROM render_world_view
        html.H4("Global Weather Overview", className="mb-3 text-center", style={'color': '#444'}),
        dcc.Graph(figure=fig_map, className="mb-4"),
        html.H5("Raw Data Table", className="mb-2", style={'color': '#444'}),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": col, "id": col} for col in df.columns],
            style_table={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'auto', 'background-color': 'rgba(255,255,255,0.8)', 'border-radius': '5px'},
            style_cell={
                'minWidth': '100px', 'width': '150px', 'maxWidth': '250px',
                'whiteSpace': 'normal',
                'textAlign': 'left',
                'backgroundColor': 'rgba(255,255,255,0.7)', # Semi-transparent cells
                'border': '1px solid #ddd'
            },
            style_header={
                'backgroundColor': '#f2f2f2',
                'fontWeight': 'bold',
                'border': '1px solid #ccc'
            },
            page_size=10,
            fixed_rows={'headers': True}
        )
    ], style={'background-color': 'rgba(255,255,255,0)', 'border-radius': '8px', 'padding': '15px'}) # ADDED: Transparent background for this div