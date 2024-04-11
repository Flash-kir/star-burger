import requests
from geopy import distance
from django.conf import settings
from foodcartapp.models import Address


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.API_YANDEX_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None, None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return (lat, lon)


def check_address(addr):
    addresses = Address.objects.filter(address=addr)
    if addresses:
        address = addresses.first()
        lat = address.lat
        lon = address.lon
    else:
        (lat, lon) = fetch_coordinates(addr)
        address, create = Address.objects.get_or_create(lat=lat, lon=lon, address=addr)
    return (lat, lon)


def calculate_distance(address1, address2):
    (lat1, lon1) = check_address(address1)
    (lat2, lon2) = check_address(address2)

    if lat1 and lat2 and lon1 and lon2:
        dist = distance.distance((lat1, lon1), (lat2, lon2)).km
    else:
        dist = None
    return dist


def distance_text(distance):
    distance_text = ''
    if distance:
        distance_text = f' - {round(distance, 3)} км.'
    else:
        distance_text = ' (не удалось вычислить расстояние)'
    return distance_text
