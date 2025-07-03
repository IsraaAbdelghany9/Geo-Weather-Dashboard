import plotly.express as px
from dash import dash_table, html, dcc
import pandas as pd # Import pandas

def render_world_view(df: pd.DataFrame): # Add type hint for clarity
    if df is None or df.empty:
        return html.Div("No weather data available. Click 'Get Weather' to fetch data.", style={"color": "red"})

    # --- Global Temperature Map (Scatter Geo) ---
    # Assuming 'lat', 'lon', 'city', 'country', 'temp_c' columns exist in your DataFrame
    # If your `cities_df` (used in app.py to get the initial list of cities) contains 'continent',
    # you might want to join it with your fetched weather data (df) to show continent on hover or filter.
    # For a simple start, we'll just use the fetched weather data directly.

    fig_map = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        color="temp_c",  # Color points by temperature in Celsius
        hover_name="city", # Show city name on hover
        size="temp_c",     # Size points by temperature (optional, can remove if not desired)
        projection="natural earth", # Or "equirectangular", "mercator"
        title="Current City Temperatures Worldwide",
        color_continuous_scale=px.colors.sequential.Plasma, # Choose a color scale
        height=650
    )
    # Update map layout for better visibility
    fig_map.update_layout(
        geo=dict(
            showland = True,
            landcolor = "rgb(243, 243, 243)",
            countrycolor = "rgb(204, 204, 204)",
        ),
        margin={"r":0,"t":50,"l":0,"b":0} # Adjust margins
    )

    return html.Div([
        html.H4("Global Weather Overview", className="mb-3 text-center"),
        dcc.Graph(figure=fig_map, className="mb-4"),
        html.H5("Raw Data Table", className="mb-2"),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": col, "id": col} for col in df.columns],
            style_table={'overflowX': 'auto', 'maxHeight': '400px', 'overflowY': 'auto'},
            style_cell={
                'minWidth': '100px', 'width': '150px', 'maxWidth': '250px',
                'whiteSpace': 'normal',
                'textAlign': 'left',
            },
            style_header={
                'backgroundColor': '#f2f2f2',
                'fontWeight': 'bold'
            },
            page_size=10, # Reduced page size for better fit
            fixed_rows={'headers': True}
        )
    ])