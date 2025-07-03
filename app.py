# app.py

from threading import Thread
import dash
from dash import html, Input, Output, State, callback_context as ctx, callback
import dash_bootstrap_components as dbc
# Ensure all your custom modules are accessible in the Python path
from data import cities_df
from tabs.world_tab import world_layout
from tabs.continent_tab import continent_layout
from tabs.country_tab import country_layout
from tabs.region_tab import region_layout
from tabs.city_tab import city_layout
from utils import get_world_df, get_continent_df, get_country_df, get_region_df, get_city_row
from data_loader import get_data_incremental, get_countries_by_continent, get_regions_by_country, get_cities_by_region, get_city_forecast
from views.world_view import render_world_view
from views.continent_view import render_continent_view
from views.country_view import render_country_view
from views.region_view import render_region_view
from views.city_view import render_city_view
from dotenv import load_dotenv
import os

load_dotenv(".env")

progress = {"value": 0}
result_df = {
    "world": None,
    "continent": None,
    "country": None,
    "region": None,
    "city": None
}

def update_progress(p):
    global progress
    progress["value"] = p

def run_weather_fetch(df, fn, key):
    global result_df
    progress["value"] = 0
    result_df[key] = fn(df, step_callback=update_progress)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = dbc.Container([
    # This overlay div helps with readability on top of a busy background image
    html.Div(style={
        'position': 'absolute', # Positions relative to the parent container
        'top': 0, 'left': 0,
        'width': '100%', 'height': '100%',
        'background-color': 'rgba(255, 255, 255, 0.6)', # White overlay, 60% opaque
        'z-index': 0 # Rendered below other content
    }),
    dbc.Tabs([
        dbc.Tab(label="World", tab_id="world"),
        dbc.Tab(label="Continent", tab_id="continent"),
        dbc.Tab(label="Country", tab_id="country"),
        dbc.Tab(label="Region", tab_id="region"),
        dbc.Tab(label="City", tab_id="city"),
    ], id="tabs", active_tab="world", className="mt-4", style={'z-index': 1, 'position': 'relative'}), # Ensure tabs are above overlay
    html.Div(id="tab-content", className="p-4", style={'z-index': 1, 'position': 'relative'}) # Ensure content is above overlay
], fluid=True, style={
    'background-image': 'url("/assets/360_F_211524227_Ett8aboQvVnROAFtqu3S1pW99Y3Th9vm.jpg")', # Path to your image in the assets folder
    # Or use an online image URL like: 'url("https://images.unsplash.com/photo-1596706857999-edb201a073f1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w1MjcwNzV8MHwxfHNlYXJjaHwxNXx8Y2xvdWRzJTIwYmFja2dyb3VuZHxlbnwwfHx8fDE3MTk5MjczODl8MA&ixlib=rb-4.0.3&q=80&w=1080")',
    'background-size': 'cover',          # Image covers the entire container
    'background-repeat': 'no-repeat',    # Prevents image repetition
    'background-position': 'center center', # Centers the image
    'min-height': '100vh',               # Ensures background covers the full viewport height
    'background-attachment': 'fixed',    # Background scrolls with the content
    'position': 'relative',              # Needed for z-index of absolute children (the overlay)
    'padding-bottom': '50px'             # Add some padding at the bottom if content is long
})


@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab(tab):
    """Renders the content for the selected tab."""
    # This callback works by returning the layout defined in each tab's module.
    # Ensure these world_layout(), continent_layout(), etc., functions
    # are correctly defined and return valid Dash components.
    return {
        "world": world_layout(),
        "continent": continent_layout(),
        "country": country_layout(),
        "region": region_layout(),
        "city": city_layout()
    }.get(tab, html.Div("Tab not found."))

# Drop downs for country tab
@app.callback(
    Output("dropdown-country", "options"),
    Input("continent-dropdown-country", "value")
)
def update_country_options(selected_continent):
    return get_countries_by_continent(cities_df, selected_continent)

# Drop downs for region tab
@app.callback(
    Output("dropdown-region", "options"),
    Input("country-dropdown-region", "value")
)
def update_region_options(selected_country):
    return get_regions_by_country(cities_df, selected_country)

#Drop downs for city tab
@app.callback(
    Output("region-dropdown-city", "options"),
    Input("country-dropdown-city", "value")
)
def update_region_options_city_tab(selected_country):
    return get_regions_by_country(cities_df, selected_country)

@app.callback(
    Output("dropdown-city", "options"),
    Input("country-dropdown-city", "value"),
    Input("region-dropdown-city", "value"),
)
def update_city_options(selected_country, selected_region):
    return get_cities_by_region(cities_df, selected_country, selected_region)


# --------------MAIN CALLBACKS-----------------

#world tab callback
@app.callback(
    Output("progress-bar-world", "value"),
    Output("weather-output-world", "children"),
    Output("progress-wrapper-world", "style"),
    Output("progress-interval-world", "disabled"),
    Input("submit-world", "n_clicks"),
    Input("progress-interval-world", "n_intervals"),
    State("cap-size-world", "value"),
    prevent_initial_call=True,
)
def handle_world_tab(n_clicks, n_intervals, cap_size):
    global progress, result_df

    triggered = ctx.triggered_id

    if triggered == "submit-world":
        df = get_world_df(cities_df, cap_size)
        Thread(target=run_weather_fetch, args=(df,get_data_incremental,'world'), daemon=True).start()
        return 0, dash.no_update, {"display": "block"}, False

    value = int(progress["value"])
    if value >= 100 and result_df['world'] is not None:
        return 0, render_world_view(result_df['world']), {"display": "none"}, True

    if value > 0:
        return value, dash.no_update, {"display": "block"}, False

    return 0, dash.no_update, {"display": "none"}, False

#continent tab callback
@app.callback(
    Output("progress-bar-continent", "value"),
    Output("weather-output-continent", "children"),
    Output("progress-wrapper-continent", "style"),
    Output("progress-interval-continent", "disabled"),
    Input("submit-continent", "n_clicks"),
    Input("progress-interval-continent", "n_intervals"),
    State("dropdown-continent", "value"),
    State("cap-size-continent", "value"),
    prevent_initial_call=True,
)
def handle_continent_tab(n_clicks, n_intervals, continent, cap_size):
    global progress, result_df

    triggered = ctx.triggered_id

    if triggered == "submit-continent":
        df = get_continent_df(cities_df, continent, cap_size)
        Thread(target=run_weather_fetch, args=(df,get_data_incremental,'continent'), daemon=True).start()
        return 0, dash.no_update, {"display": "block"}, False

    value = int(progress["value"])
    if value >= 100 and result_df['continent'] is not None:
        return 0, render_continent_view(result_df['continent']), {"display": "none"}, True

    if value > 0:
        return value, dash.no_update, {"display": "block"}, False

    return 0, dash.no_update, {"display": "none"}, False

#country tab callback
@app.callback(
    Output("progress-bar-country", "value"),
    Output("weather-output-country", "children"),
    Output("progress-wrapper-country", "style"),
    Output("progress-interval-country", "disabled"),
    Input("submit-country", "n_clicks"),
    Input("progress-interval-country", "n_intervals"),
    State("dropdown-country", "value"),
    State("cap-size-country", "value"),
    prevent_initial_call=True,
)
def handle_country_tab(n_clicks, n_intervals, country, cap_size):
    global progress, result_df

    triggered = ctx.triggered_id

    if triggered == "submit-country":
        df = get_country_df(cities_df, country, cap_size)
        Thread(target=run_weather_fetch, args=(df,get_data_incremental,'country'), daemon=True).start()
        return 0, dash.no_update, {"display": "block"}, False

    value = int(progress["value"])
    if value >= 100 and result_df['country'] is not None:
        return 0, render_country_view(result_df['country']), {"display": "none"}, True

    if value > 0:
        return value, dash.no_update, {"display": "block"}, False

    return 0, dash.no_update, {"display": "none"}, False

#region tab callback
@app.callback(
    Output("progress-bar-region", "value"),
    Output("weather-output-region", "children"),
    Output("progress-wrapper-region", "style"),
    Output("progress-interval-region", "disabled"),
    Input("submit-region", "n_clicks"),
    Input("progress-interval-region", "n_intervals"),
    State("country-dropdown-region", "value"),
    State("dropdown-region", "value"),
    State("cap-size-region", "value"),
    prevent_initial_call=True,
)
def handle_region_tab(n_clicks, n_intervals, country, region, cap_size):
    global progress, result_df

    triggered = ctx.triggered_id

    if triggered == "submit-region":
        df = get_region_df(cities_df, country, region, cap_size)
        Thread(target=run_weather_fetch, args=(df,get_data_incremental,'region'), daemon=True).start()
        return 0, dash.no_update, {"display": "block"}, False

    value = int(progress["value"])
    if value >= 100 and result_df['region'] is not None:
        return 0, render_region_view(result_df['region']), {"display": "none"}, True

    if value > 0:
        return value, dash.no_update, {"display": "block"}, False

    return 0, dash.no_update, {"display": "none"}, False

#city tab callback
@app.callback(
    Output("progress-bar-city", "value"),
    Output("weather-output-city", "children"),
    Output("progress-wrapper-city", "style"),
    Output("progress-interval-city", "disabled"),
    Input("submit-city", "n_clicks"),
    Input("progress-interval-city", "n_intervals"),
    State("country-dropdown-city", "value"),
    State("region-dropdown-city", "value"),
    State("dropdown-city", "value"),
    prevent_initial_call=True,
)
def handle_city_tab(n_clicks, n_intervals, country, region, city):
    global progress, result_df

    triggered = ctx.triggered_id

    if triggered == "submit-city":
        df = get_city_row(cities_df, country, region, city)
        Thread(target=run_weather_fetch, args=(df,get_city_forecast,'city'), daemon=True).start()
        return 10, dash.no_update, {"display": "block"}, False

    value = int(progress["value"])
    if value >= 100 and result_df['city'] is not None:
        return 10, render_city_view(result_df['city']), {"display": "none"}, True

    if value > 0:
        return 10, dash.no_update, {"display": "block"}, False

    return 0, dash.no_update, {"display": "none"}, False


if __name__ == "__main__":
    app.run(debug=True)