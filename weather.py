from bs4 import BeautifulSoup
import requests
from dash.dependencies import Output, Input


def get_weather(city):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    city = city.replace(" ", "+")
    res = requests.get(
        f'https://www.google.com/search?q={city}&oq={city}&aqs=chrome.0.35i39l2j0l4j46j69i60.6128j1j7&sourceid=chrome&ie=UTF-8', headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    weather = soup.select('#wob_tm')[0].getText().strip()
    humidity = soup.select('#wob_hm')[0].getText().strip()
    wind = soup.select('#wob_ws')[0].getText().strip()
    return weather, humidity, wind


def weather_callback(app):
    @ app.callback(
        [Output('weather', 'children'),
         Output('humidity', 'children'),
         Output('wind', 'children')],
        Input('interval-weather', 'n_intervals'))
    def update_weather(n):
        weather, humidity, wind = get_weather("Bergen op Zoom weather")
        return f"temperature: {weather} C°", f"humidity: {humidity}", f"wind: {wind}"
