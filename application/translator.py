from application.globals import YANDEX_TOKEN, YANDEX_HOST
import requests


def get_languages():
    url = f"{YANDEX_HOST}/getLangs&key={YANDEX_TOKEN}&ui=en"
    r = requests.get(url=url)
    if r.status_code == 200:
        data = r.json()
        return data
    return None


def detect_language(text, hint="en,uz"):
    url = f"{YANDEX_HOST}/detect?key={YANDEX_TOKEN}&text={text}&hint={hint}"
    r = requests.get(url=url)
    if r.status_code == 200:
        data = r.json()
        return data['lang']
    return None


def translate(text, lang_, lang__):
    url = f"{YANDEX_HOST}/translate?key={YANDEX_TOKEN}&lang={lang_}-{lang__}&text={text}"
    r = requests.get(url=url)
    if r.status_code == 200:
        data = r.json()
        return data['text'][0]
    return None