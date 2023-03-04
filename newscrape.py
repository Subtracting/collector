from bs4 import BeautifulSoup
import requests


def get_news():

    res = requests.get('https://www.nu.nl/')
    soup = BeautifulSoup(res.text, 'html.parser')

    spans = soup.find_all('span', {'class': 'item-title__title'})
    spans_href = soup.find('href', {'class': 'item-title__title'})
    main_title = soup.find_all('h1', {'class': 'title fluid'})[0].get_text()

    titles = [span.get_text() for span in spans]
    unique = [main_title]
    count = 0

    for title in titles:
        if title not in unique:
            unique.append(title)
            count += 1
        if count == 10:
            break
    return unique


get_news()
