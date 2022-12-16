from gettext import find
from http import client
from pymongo import MongoClient
from gnews import GNews
from geopy.geocoders import Nominatim
import spacy
from newspaper import Article
from newspaper import Config


# method to find city coordinates
def find_coordinates(city):
    location = geolocator.geocode(city)
    if location.latitude and location.longitude:
        return [location.latitude, location.longitude]
    else:
        return ['', '']


# config for newspaper3k
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'

config = Config()
config.browser_user_agent = user_agent


geolocator = Nominatim(user_agent="CrimeMapper")
nlp = spacy.load('en_core_web_lg')  # loading a spacy package

# setting the parameters for scrapper
google_news = GNews()
google_news.country = 'United States'
google_news.language = 'english'

# defining constants
TODAY_DATE = '14 Nov 2022'  # set this as yesterday's date to get news
KEYWORDS = ['elder abuse', 'child abuse', 'patient abuse',
            'break-ins', 'shooting', 'murder', 'kidnapping']

# connection to db
client = MongoClient(
    '******************************************')
if client:
    print("Connected to Database...")
    database = client['news']
    col = database['news_articles']
    for keyword in KEYWORDS:
        all_news = google_news.get_news(keyword)
        if len(all_news):
            for news in all_news:
                if TODAY_DATE in news['published date']:
                    temp = news
                    article_url = temp['url']
                    # string_encode = article_url.encode("ascii", "ignore")
                    # string_decode = string_encode.decode()
                    print(article_url)
                    # getting city name from article
                    if article_url:
                        try:
                            article = Article(url="%s" %
                                              (article_url), language='en')
                            article.download()
                            article.parse()
                            title = article.title
                            text = article.text
                            if title != '':
                                doc = nlp(title)
                                for ent in doc.ents:
                                    if ent.label_ == 'GPE':
                                        temp['city'] = ent.text.lower()
                                        temp['keyword'] = keyword
                                        coordinates = find_coordinates(
                                            ent.text)
                                        temp['lat'] = coordinates[0]
                                        temp['long'] = coordinates[1]
                                        rec = col.insert_one(
                                            temp)
                                        if rec:
                                            print("Saved to db\t|\t",
                                                  title)
                                            print('\n')
                                        break
                            if text != '' and ('city' not in temp.keys()):
                                doc = nlp(text)
                                for ent in doc.ents:
                                    if ent.label_ == 'GPE':
                                        temp['city'] = ent.text.lower()
                                        temp['keyword'] = keyword
                                        coordinates = find_coordinates(
                                            ent.text)
                                        temp['lat'] = coordinates[0]
                                        temp['long'] = coordinates[1]
                                        rec = col.insert_one(
                                            temp)
                                        if rec:
                                            print("Saved to db\t|\t",
                                                  title)
                                            print('\n')
                                        break
                        except:
                            print('Unable to fetch article')

                    else:
                        print('Unable to fetch article content.')

        else:
            print('No results found for', keyword)
else:
    print("Unable to connect to mongodb.")
