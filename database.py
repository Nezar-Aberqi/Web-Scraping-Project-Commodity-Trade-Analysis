import sqlite3
import pandas as pd


def create_database():
    ### Creating the database, creating the tables and populating them with the main targeted countries and also commodities
    conn = sqlite3.connect('Commodities_analyses.db')
    cursor = conn.cursor()
    trades = pd.read_csv('trading_data.csv')
    # rename commodity code column to delete the space and also the tradee flow column of the trade table.
    trades.rename(columns={'Commodity Code': 'Commodity_Code', 'Trade Flow': 'Trade_Flow'}, inplace=True)
    news = pd.read_csv('geopolitical.csv')
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS hs_commodities(
    commodity_code INTEGER PRIMARY KEY,
    commodity_name TEXT NOT NULL,
    unit TEXT,
    category TEXT );""",

        """ CREATE TABLE IF NOT EXISTS countries (
    country_code INTEGER PRIMARY KEY,
    country_name TEXT NOT NULL,
    region TEXT NOT NULL
    );""",

        """ INSERT INTO hs_commodities(commodity_code, commodity_name, unit, category)
        VALUES 
        (2709, 'Crude Petroleum Oil', 'Barrels', 'Energy'),
        (2711, 'Natural Gas', 'Cubic Meters', 'Energy'),
        (7108, 'Gold', 'Kilograms', 'Precious Metals'),
        (1001, 'Wheat', 'Tons', 'Agriculture'); """,

        """ INSERT INTO countries(country_code, country_name, region)
        VALUES
        (1, 'USA', 'North America'),
        (44, 'United Kingdom', 'Europe'),
        (33, 'France', 'Europe'),
        (86, 'China', 'East Asia'),
        (7, 'Russia', 'North Asia'),
        (380, 'Ukraine', 'Europe'),
        (966, 'Saudi Arabia', 'Middle East'),
        (974, 'Qatar', 'Middle East'),
        (91, 'India', 'South Asia'); """
    ]

    for statement in sql_statements:
        cursor.execute(statement)
        print('Table created successfully')
    ## on cree la premiere table de faits
    trades.to_sql('trades', conn, if_exists='replace', index=False)
    ## on cree la deuxieme table de faits 
    news.to_sql('news', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print(f"Tables are created  successfully, database is now up and running...")
    return None 

def get_db_data(query, query_params=()):
    try:
        conn = sqlite3.connect('Commodities_analyses.db')
        df = pd.read_sql_query(query, conn, params=query_params)
        conn.close()
        return df
    except Exception as e:
        print(str(e))
        return None


def get_commodity_code(commodity_name):
    query = """ 
    SELECT commodity_code FROM hs_commodities WHERE commodity_name = ?
    """
    result = get_db_data(query,commodity_name)
    return result


def filter_trade_world(country,commodity_code,trade_flow): 
    query = """ 
      SELECT * FROM trades Where Reporter = ? AND Commodity_Code = ? AND Trade_Flow = ? AND Partner = 'World'
      """
    result = get_db_data(query, (country,commodity_code,trade_flow))
    return result


def filter_trade(country,commodity_code,trade_flow): 
    query = """ 
      Select * from trades Where Reporter = ? and 'Commodity_Code' = ? and 'Trade_Flow' = ? 
      """
    result = get_db_data(query, (country,commodity_code,trade_flow))
    return result   

def get_commodity_name(commodity_code):
    query = """ 
    SELECT commodity_name FROM hs_commodities WHERE commodity_code = ?
    """
    result = get_db_data(query,(commodity_code,))

    return result

def get_news_data(country,commodity_code,tradeFlow='Export') : 
    name_query = """SELECT commodity_name FROM hs_commodities WHERE commodity_code = ?"""
    commodity_name = get_db_data(name_query,(commodity_code,))
    commodity_name = commodity_name['commodity_name'].values[0]
    query = """SELECT year, event_happened  FROM news WHERE country_name = ? AND commodity_name = ?  AND target_economic_domain = ? """
    result = get_db_data(query, (country,commodity_name,tradeFlow))

    return result

