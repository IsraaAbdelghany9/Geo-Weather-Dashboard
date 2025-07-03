import plotly.express as px
from dash import dash_table, html, dcc
import pandas as pd

def render_region_view(df: pd.DataFrame):
    if df is None or df.empty:
        return html.Div("No weather data available. Select a region and click 'Get Weather'.", style={"color": "red"})

    selected_country = df['country'].iloc[0].title() if 'country' in df.columns and not df.empty else "Selected Country"
    selected_region = df['region'].iloc[0].title() if 'region' in df.columns and not df.empty else "Selected Region"

    # --- Bar Chart: Average Temperature by City in Region ---
    avg_temp_by_city = df.groupby('city')['temp_c'].mean().reset_index()

    fig_bar = px.bar(
        avg_temp_by_city,
        x="city",
        y="temp_c",
        title=f"Average Temperature (°C) by City in {selected_region}, {selected_country}",
        labels={"temp_c": "Average Temperature (°C)", "city": "City"},
        color="temp_c",
        color_continuous_scale=px.colors.sequential.Viridis,
        height=400
    )
    fig_bar.update_layout(margin={"r":0,"t":50,"l":0,"b":0})

    # --- Scatter Map for Cities in Region ---
    fig_map = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        color="temp_c",
        hover_name="city",
        size="temp_c",
        scope="world",
        title=f"Current City Temperatures in {selected_region}",
        color_continuous_scale=px.colors.sequential.Plasma,
        height=600
    )
    fig_map.update_layout(
        geo=dict(
            showland = True,
            landcolor = "rgb(243, 243, 243)",
            countrycolor = "rgb(204, 204, 204)",
        ),
        margin={"r":0,"t":50,"l":0,"b":0}
    )

    return html.Div([
        html.H4(f"Weather in {selected_region}, {selected_country}", className="mb-3 text-center"),
        dcc.Graph(figure=fig_bar, className="mb-4"),
        dcc.Graph(figure=fig_map, className="mb-4"),
        html.H5("Raw Data Table", className="mb-2"),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": col, "id": col} for col in df.columns],
            style_table={'overflowX': 'auto', 'maxHeight': '300px', 'overflowY': 'auto'},
            style_cell={
                'minWidth': '100px', 'width': '150px', 'maxWidth': '250px',
                'whiteSpace': 'normal',
                'textAlign': 'left',
            },
            style_header={
                'backgroundColor': '#f2f2f2',
                'fontWeight': 'bold'
            },
            page_size=8,
            fixed_rows={'headers': True}
        )
    ])