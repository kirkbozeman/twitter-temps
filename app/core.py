import os
import requests
import json
from collections import deque
from shapely.geometry import box


TWITTER_TOKEN = os.getenv('TWITTER_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')


def bbox_to_lat_lon(bbox):
    """
    Converts bbox to lat/lon
    """

    polygon = box(*bbox)
    return round(polygon.centroid.y, 4), round(polygon.centroid.x, 4)


def bbox_to_temp(bbox, token):
    """
    Uses bbox from Twitter place.fields to query weather at lat/lon location
    """

    y, x = bbox_to_lat_lon(bbox)
    url = f"http://api.weatherapi.com/v1/current.json?key={token}&q={y},{x}"

    session = requests.Session()
    response = session.get(url)
    weather = json.loads(response.content)

    loc = weather['location']
    temp_f = weather.get('current').get('temp_f')

    print(f"Weather API: {loc['name']}, {loc['region']}, {loc['country']}")

    return temp_f


def get_geo_stream(bearer_token, n):
    """
    Runs Twitter sample stream to grab geo data when available, also grabs weather data when geo data found
        Follows docs at: https://2.python-requests.org/en/master/user/advanced/#body-content-workflow
    """

    url = "https://api.twitter.com/2/tweets/sample/stream?tweet.fields=geo&expansions=geo.place_id&place.fields=full_name,geo"

    temps = deque([], maxlen=n)
    session = requests.Session()
    with session.get(url, headers={'Authorization': f'Bearer {bearer_token}'}, stream=True) as response:
        for line in response.iter_lines():
            if line:
                includes = json.loads(line).get('includes')
                if includes:
                    places = includes.get('places')
                    full_name = places[0]['full_name']
                    bbox = places[0]['geo']['bbox']

                    temp = bbox_to_temp(bbox, WEATHER_TOKEN)
                    temps.append(temp)
                    rolling_avg = round(sum(temps)/len(temps), 2)

                    print(f"Twitter API: {full_name}")
                    print(temp)
                    print(f"Avg of last {n} temps: {rolling_avg}")


if __name__ == "__main__":

    print('STARTING...')

    get_geo_stream(TWITTER_TOKEN, 5)