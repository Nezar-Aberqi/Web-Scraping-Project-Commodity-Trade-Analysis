import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from geotext import GeoText  
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk


nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

## scrape a website containing geopolitical events.
def extract_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paras = soup.find_all("p")
    snippets = []
    for para in paras:
        snippets.append(para.get_text())
    return snippets

## Once the text is scrapped, we actually want to detect the country name that is being subject of the news.
def extract_country_from_news(snippet):
    places = GeoText(snippet)
    countries = places.countries
    return countries if countries else None

## Then detect the year of the geopolitical event
def extract_year_from_news(snippet):
    years = re.findall(r'\b(20\d{2})\b',snippet)
    return years[0] if years else None

## We want to know if the event has impacted the exports or the imports ? 
def detect_trading_context(snippet):
    if "export" in snippet.lower():
        return "Export"
    elif "import" in snippet.lower():
        return "Import"
    else:
        return None 

## After, we want to analyse the sentiments of the snippet to know if the event has impacted the economic activity in a good/bad way !!
def infer_impact_of_event(snippet):
    sentiment = sia.polarity_scores(snippet)
    if sentiment['compound'] > 0:
        return "Increase"
    elif sentiment['compound'] < 0:
        return "Decrease" 
    else : 
        return "Neutral"

""" 
Now we are going to scrape the website that we find intersting in a way that it contains articles talking about the news of 
the major geopolitical events that happened in the period of 2012-2023 and give details about what impact did they make of the
trade of the critical commodities that are subject to our study and how did they impact the rate or amount  of those trades.
For that, after thorough research, we have found three websites that are interesting to scrape and get the news from.
""" 
## List of the website that  we are going to scrap
news_urls = ["https://www.api.org/news-policy-and-issues/blog/2022/05/13/analyzing-how-geopolitical-events-have-impacted-crude-oil-market",
        "https://www.atlanticcouncil.org/blogs/econographics/beyond-oil-natural-gas-and-wheat-the-commodity-shock-of-russia-ukraine-crisis/", 
         "https://www.markets.com/education-centre/commodities-prices/"]
def scrape_api_org() :
    url = "https://www.api.org/news-policy-and-issues/blog/2022/05/13/analyzing-how-geopolitical-events-have-impacted-crude-oil-market"
    snippets = extract_news(url)
    print(snippets)
    data = []
    for snippet in snippets:
        country = extract_country_from_news(snippet)
        print('country : ',country)
        year = extract_year_from_news(snippet)
        print('year : ', year)
        trade_context = detect_trading_context(snippet)
        print('trade_context : ', trade_context)
        impact = infer_impact_of_event(snippet)
        print('impact : ', impact)
        if country and year and trade_context :
            data.append({
                'year': year,
                'country_name': country,  
                'commodity_name': 'Oil', 
                'event_happened': snippet[:20], 
                'target_economic_domain': trade_context,  
                'impact_of_event_on_target_domain': impact  
            })

    return pd.DataFrame(data)
## Montrer la dataframe finale :
df = scrape_api_org()
print(df) 
