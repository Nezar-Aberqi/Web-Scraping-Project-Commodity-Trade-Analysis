from database import get_db_data, get_commodity_code,filter_trade,filter_trade_world,get_news_data
import numpy as np 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

### we will define here helper functions that would help us with the plotting of the graphs
"""Function to plot the exports."""
def plot_exports(country,commodity):
    export_flows = filter_trade_world(country, commodity, 'Export')
    news  = get_news_data(country,commodity,'Export')
    
    figure = px.line(export_flows, x='Period', y='Trade Value (M $)', title=f'Evolution of {commodity} Imports from {country} over the recent period')
    
    figure = px.line(export_flows, x='Period', y='Trade Value (M $)',
                 title=f'Evolution of {commodity} Exports from the {country} over the recent periods',
                 line_shape='linear',
                 markers=True, 
                 color_discrete_sequence=['darkred']  
)   
    
    for i,row in news.iterrows() : 
        figure.add_annotation(
            x=row['year'], y=export_flows[export_flows['Period'] == row['year']]['Trade Value (M $)'].values[0],
            text="🛈", showarrow=True, arrowhead=2, ax=0, ay=-40,
            hovertext=row['event_happened'],  
            hoverlabel=dict(bgcolor="black", font_size=16, font_family="Rockwell")
        )
    figure.update_layout(
        title={'x': 0.5},  
        font_color='darkblue',  
        plot_bgcolor='white',  
        yaxis=dict(title="USD millions", tickformat=',', showgrid=True, gridcolor='rgba(173, 216, 230, 0.5)'),
        xaxis = dict(showgrid=False,dtick=1)
    )
    # i want the x ticks to contain all the years from 2012 to 2024
    figure.update_traces(marker=dict(size=10, color='darkred', symbol='circle')) 
    return figure


"""Function to plot the exports."""
def plot_imports(country,commodity):
    import_flows = filter_trade_world(country, commodity, 'Import')
    news  = get_news_data(country,commodity,'Import')
        
    figure = px.line(import_flows, x='Period', y='Trade Value (M $)',
                 title=f'Evolution of {commodity} Imports from the {country} over the recent periods',
                 line_shape='linear',
                 markers=True, 
                 color_discrete_sequence=['darkred']  
)   
    
    for i,row in news.iterrows() : 
        figure.add_annotation(
            x=row['year'], y=import_flows[import_flows['Period'] == row['year']]['Trade Value (M $)'].values[0],
            text="🛈", showarrow=True, arrowhead=2, ax=0, ay=-40,
            hovertext=row['event_happened'],  
            hoverlabel=dict(bgcolor="black", font_size=16, font_family="Rockwell")
        )
    figure.update_layout(
        title={'x': 0.5},  
        font_color='darkblue',  
        plot_bgcolor='white',  
        yaxis=dict(title="USD millions", tickformat=',', showgrid=True, gridcolor='rgba(173, 216, 230, 0.5)'),
        xaxis = dict(showgrid=False,dtick=1)
    )
    # i want the x ticks to contain all the years from 2012 to 2024
    figure.update_traces(marker=dict(size=10, color='darkred', symbol='circle')) 
    return figure



"""Function to plot the balance of the trades over the year"""
def commodity_balance(country,commodity) :
    exports = filter_trade_world(country,commodity,'Export') 
    imports = filter_trade_world(country,commodity,'Import')
    balance = exports[['Period','Trade Value (M $)']].set_index('Period')
    balance = balance.rename(columns={'Trade Value (M $)':'Exports Value (M $)'})
    balance = balance.join(imports[['Period','Trade Value (M $)']].set_index('Period'), how='outer')
    balance = balance.rename(columns={'Trade Value (M $)': 'Imports Value (M $)'})
    balance['Trade Balance (M $)'] = balance['Exports Value (M $)'] - balance['Imports Value (M $)'] 
    fig = go.Figure()
    fig.add_trace(go.Bar(x=balance.index,y=balance['Exports Value (M $)'],name=f'{commodity} Exports',
        marker_color='green',width=0.3))
    fig.add_trace(go.Bar(x=balance.index,y=-balance['Imports Value (M $)'], name=f'{commodity} Imports',
        marker_color='red',width=0.3))
    fig.add_trace(go.Scatter( x=balance.index,y=balance['Trade Balance (M $)'],mode='lines',name='Balance',
       line=dict(color='black', width=4)
    ))
    fig.update_layout(width=1000,height=600,title=f'{commodity} balance for {country} over the recent periods',title_x=0.5,yaxis_title='Million $', plot_bgcolor='white',
        xaxis=dict(title='Year', showgrid=False, dtick=1),
        yaxis=dict(gridcolor='rgba(173, 216, 230, 0.5)', showline=True,zeroline=True,zerolinecolor='black'),
        legend=dict(title="",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        barmode='overlay')
    return fig 


"""Function to plot the top countries that import the commodity from the selected country"""
def Countries_Share(country, commodity_code):
    flows = filter_trade(country, commodity_code, 'Export') 
    print(flows)
    total_export_trades =flows[flows['Partner'] == 'World'].set_index('Period')['Trade Value (M $)'].to_dict()
    flows['Share of Exports (%)'] = flows.apply(lambda row: (row['Trade Value (M $)'] / total_export_trades.get(row['Period'], 1)) * 100, axis=1)
    flows = flows[flows['Partner'] != 'World']
    fig = px.choropleth(
        flows,locations='Partner', locationmode='country names', color='Share of Exports (%)',hover_name='Partner',
        hover_data={'Share of Exports (%)': True,'Period':False},
        animation_frame='Period', color_continuous_scale=px.colors.sequential.Plasma,
        title=f'Partner Share of {commodity_code} Exports from {country} over the recent periods',
        labels={'Share of Exports (%)': 'Export Share (%)'}
    )
    fig.update_layout(
        width=1000, 
        height=800,
        geo=dict(showframe=False, showcoastlines=False, projection_type='natural earth'),
        coloraxis_colorbar=dict(
            title='Export Share (%)',
            ticks='outside',
            tickvals=[0, 25, 50, 75, 100],
        ),
        title_x=0.5
    )
    return fig

"""Function the define the data table of export growth to the target country""" 
def highest_growth_exporters(country,commodity) :
    imports = filter_trade(country, commodity, 'Import')
    imports = imports[(imports['Partner']!='World')&(imports['Period'].between(2018, 2023))]
    pivot =  imports.pivot_table(index='Partner', columns='Period', values='Trade Value (M $)').reset_index()
    years_period = pivot.columns.to_list()
    years_period.remove('Partner')
    pivot.dropna(thresh=len(list(pivot.columns))//2, inplace=True)
    pivot.dropna(subset=[pivot.columns[1]], inplace=True)
    pivot = pivot.apply(lambda row: row.fillna(method='ffill'), axis=1)
    for year in  years_period[1:]:
        pivot[f'Growth {year} (%)'] = (pivot[year] - pivot[year-1])/pivot[year-1]*100

    pivot = pivot.replace([np.inf,-np.inf],100)
    pivot['Growth Average (%)'] = pivot[[f'Growth {year} (%)' for year in years_period[1:]]].mean(axis=1)
    top10 = pivot.sort_values(by='Growth Average (%)', ascending=False).head(10)

    flags = {country : f'https://flagcdn.com/{country}.svg' for  country in top10['Partner'].values}
    top10['Flag'] = top10['Partner'].map(flags)

    top_exporters = top10[['Partner','Flag','Growth 2019 (%)','Growth 2020 (%)','Growth 2021 (%)','Growth 2022 (%)','Growth 2023 (%)']]
    top_exporters = top_exporters.reset_index(drop=True)
    header = list(top_exporters.columns)
    top_exporters['Flag'] = top_exporters['Flag'].apply(lambda url: f'<img src="{url}" style="height:30px;">')

    for col in header[2:]:  
      top_exporters[col] = top_exporters[col].apply(lambda x: f"{x:.2f}%")
    cell_values = [top_exporters[col].to_list() for col in list(top_exporters.columns)]
    fig = go.Figure(data=[go.Table(
        columnwidth=[80, 50, 80, 80, 80, 80, 80],  
    header=dict(
            values=header,  
            fill_color='rgba(255, 255, 255, 0)',  
            align='left',
            font=dict(color='black', size=14),
            line_color='white' 
        ),
        cells=dict(
            values=cell_values,
            align='left',
            font=dict(color='black', size=12),
            height=30,
            line_color='white', 
            format=[None]  
        )
    )])
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=400
    ) 
    return fig 
