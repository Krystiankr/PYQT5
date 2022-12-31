import requests
from bs4 import BeautifulSoup


def get_request(init_word: str):
    url = f"https://dictionary.cambridge.org/pl/dictionary/english/{init_word}"

    payload = {}
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'Cookie': 'XSRF-TOKEN=2b6ef741-4111-4923-ad06-7bd65f3901e1; loginPopup=1'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_translation_from(init_word: str) -> tuple:
    soup = get_request(init_word)
    head_word = soup.select_one('.dhw').text
    translation = soup.select_one('.def').text
    examples = [element.text for element in soup.find_all(
        class_='examp dexamp')]
    return {'head_word': head_word, 'translation': translation, 'examples': examples}
