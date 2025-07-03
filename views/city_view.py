import plotly.graph_objects as go # For gauge chart
import plotly.express as px
from dash import dash_table, html, dcc
import pandas as pd

def render_city_view(df: pd.DataFrame):
    if df is None or df.empty:
        return html.Div("No weather data available. Select a city and click 'Get Weather'.", style={"color": "red"})

    # The 'df' passed to render_city_view is the hourly forecast DataFrame
    # from extract_hourly_forecast.
    # The current weather data might be the first row of this DataFrame, or you'd need
    # to fetch it separately in data_loader if you want a true "current" snapshot
    # that is separate from the first forecast hour.
    # For now, let's assume the first row represents the most current available data.

    city_name = df['city'].iloc[0].title() if 'city' in df.columns and not df.empty else "Selected City"
    country_name = df['country'].iloc[0].title() if 'country' in df.columns and not df.empty else ""
    region_name = df['region'].iloc[0].title() if 'region' in df.columns and not df.empty else ""


    # --- Current Temperature Gauge (using first forecast hour for current) ---
    current_temp = df['temp_c'].iloc[0] if not df.empty else None
    current_condition_text = df['condition_text'].iloc[0] if not df.empty else "N/A"
    current_humidity = df['humidity'].iloc[0] if not df.empty else None
    current_wind_kph = df['wind_kph'].iloc[0] if not df.empty else None

    if current_temp is not None:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta", # Add delta if you have previous temp
            value = current_temp,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Current Temp (°C)", 'font': {'size': 18}},
            gauge = {
                'axis': {'range': [-10, 40], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-10, 0], 'color': "lightblue"},
                    {'range': [0, 15], 'color': "lightgreen"},
                    {'range': [15, 25], 'color': "yellow"},
                    {'range': [25, 40], 'color': "red"}],
                'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': current_temp}
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=40, b=10))
    else:
        fig_gauge = {} # Empty figure if no data


    # --- Hourly Forecast Plot ---
    # Ensure 'time' column is suitable for plotting (datetime object or string)
    df['time'] = pd.to_datetime(df['time']) # Convert to datetime if not already

    fig_forecast = px.line(
        df,
        x="time",
        y=["temp_c", "feelslike_c", "humidity", "wind_kph", "cloud"],
        title=f"3-Day Hourly Forecast for {city_name}, {country_name}",
        labels={
            "temp_c": "Temperature (°C)",
            "feelslike_c": "Feels Like (°C)",
            "humidity": "Humidity (%)",
            "wind_kph": "Wind Speed (kph)",
            "cloud": "Cloud Cover (%)",
            "time": "Time"
        },
        height=500
    )
    fig_forecast.update_xaxes(tickformat="%m/%d %H:%M") # Format x-axis for date and time
    fig_forecast.update_layout(hovermode="x unified", margin={"r":0,"t":50,"l":0,"b":0})


    return html.Div([
        html.H4(f"Detailed Weather for {city_name}, {country_name}", className="mb-3 text-center"),
        html.Div([
            html.P(f"Condition: {current_condition_text}", style={'fontSize': '1.1em', 'fontWeight': 'bold'}),
            html.P(f"Humidity: {current_humidity}%", style={'fontSize': '1.1em'}),
            html.P(f"Wind Speed: {current_wind_kph} kph", style={'fontSize': '1.1em'}),
        ], className="text-center mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_gauge), width=4), # Current temp gauge
            dbc.Col(dcc.Graph(figure=fig_forecast), width=8) # Hourly forecast
        ], className="mb-4"),
        html.H5("Raw Forecast Data Table", className="mb-2"),
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
            page_size=8,
            fixed_rows={'headers': True}
        )
    ])