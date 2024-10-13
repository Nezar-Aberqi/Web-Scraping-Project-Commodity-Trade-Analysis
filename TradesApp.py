import dash
from dash import Dash,html
from  dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from database import get_db_data, get_commodity_code,filter_trade,filter_trade_world,get_news_data
from plotting_functions import plot_exports,plot_imports,Countries_Share,commodity_balance,Countries_Share,highest_growth_exporters
import numpy as np 
import pandas as pd



app = dash.Dash()

app.layout = html.Div([
    html.H1("Commodity Trade Analysis", style={'textAlign': 'center', 'font-family': 'Arial', 'color': '#333333'}),
    
    html.Div([
        html.Label("Select Country", style={'font-size': '18px', 'font-family': 'Arial', 'color': '#4A4A4A'}),
        dcc.Dropdown(
            id='country_choice',
            options=[{'label': country, 'value': country} for country in get_db_data("SELECT DISTINCT country_name FROM countries")['country_name']],
            value='USA',  # Default value
            style={'width': '60%', 'margin': 'auto', 'font-size': '14px', 'padding': '5px'}
        )
    ],style={'padding': '20px', 'textAlign': 'center'}),
    
    html.Div([
        html.Label("Select Commodity", style={'font-size': '18px', 'font-family': 'Arial', 'color': '#4A4A4A'}),
        dcc.Dropdown(
            id='commodity_choice',
            options=[{'label': row['commodity_name'], 'value': row['commodity_code']} for i, row in get_db_data("SELECT DISTINCT commodity_name, commodity_code FROM hs_commodities").iterrows()],
            value=2709,  
            style={'width': '60%', 'margin': 'auto', 'font-size': '14px', 'padding': '5px'}
        )
    ], style={'padding': '20px', 'textAlign': 'center'}),
    
    html.Div([
        html.Button('Submit', id='submit', n_clicks=0, 
                    style={
                        'background-color': '#008CBA', 
                        'color': 'white', 
                        'font-size': '16px', 
                        'font-family': 'Arial',
                        'padding': '10px 20px',
                        'border': 'none',
                        'cursor': 'pointer',
                        'textAlign': 'center',
                        'border-radius': '5px'
                    })
    ], style={'textAlign': 'center', 'padding': '20px'}),

    html.Div(id='graphs-container')

])

## callback to display the report based on the user input.
@app.callback(
    Output('graphs-container', 'children'),  
    Input('submit', 'n_clicks'),
    State('country_choice', 'value'),  
    State('commodity_choice', 'value')  
)
def generate_report(n_clicks, country, commodity):
    print('country selected : ',country)
    print('commodity selected : ',commodity)
    if n_clicks > 0:
     
        exports = dcc.Graph(figure=plot_exports(country, commodity))
        imports = dcc.Graph(figure=plot_imports(country, commodity))
   
        return dbc.Container([
            dbc.Row([
                dbc.Col(exports, width=6),  
                dbc.Col(imports, width=4)   
            ])  ,
            dbc.Row([
             dbc.Col(dcc.Graph(figure=commodity_balance(country,commodity)), width=5),
             dbc.Col(dcc.Graph(figure=Countries_Share(country,commodity)), width=5)
           ]) ,
            dbc.Row([
             dbc.Col(dcc.Graph(figure=highest_growth_exporters(country,commodity)), width=5),
           ])
        ])
    else:
        return html.Div()



if __name__ == '__main__':
    app.run_server(debug=True)  
   

