import requests
from environs import Env
from geopy import distance

env = Env()
env.read_env()


def fetch_coordinates(address):
    API_YANDEX_KEY = env('API_YANDEX_KEY')

    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": API_YANDEX_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def calculate_distance(address1, address2):
    coord1 = fetch_coordinates(address1)
    coord2 = fetch_coordinates(address2)
    if coord1 and coord2:
        return distance.distance(coord1, coord2).km
    return None


def distance_text(distance):
    distance_text = ''
    if distance:
        distance_text = f' - {distance} км.'
    else:
        distance_text = ' (не удалось вычислить расстояние)'
    return distance_text
