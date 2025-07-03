## views/progress_view.py
from dash import html, dcc
import dash_bootstrap_components as dbc

def render_progress_view(prefix = ''):
    return dbc.Col([
    dcc.Store(id=f"progress-store-{prefix}"),
    dcc.Interval(id=f"progress-interval-{prefix}", interval=500, n_intervals=0, disabled=True),
    html.Div(id=f"progress-wrapper-{prefix}", children=[
        dbc.Progress(
            id=f"progress-bar-{prefix}",
            striped=True,
            animated=True,
            value=0
        )
        ], style={"display": "none"}, className='my-3'),
    html.Div(id=f"weather-output-{prefix}", className="mt-4")
    ], width=12)