"""Streams Twitter sample data w/ Twitter v2 API, calc rolling avg temps of tweets with an embedded location.
"""

from collections import deque
from datetime import datetime
import os
import json
import requests
from requests.exceptions import ConnectionError
from shapely.geometry import box

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s"
    )

TWITTER_TOKEN = os.getenv('TWITTER_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
RUN_STARTTIME = datetime.now()


def bbox_to_lat_lon(bbox):
    """Converts bbox to lat/lon.

    :param bbox: a bbox (list) returned from Twitter API

    :return centroid of bbox
    """

    polygon = box(*bbox)
    return round(polygon.centroid.y, 4), round(polygon.centroid.x, 4)


def bbox_to_temp(bbox, token):
    """Uses bbox from Twitter place.fields to query weather at lat/lon.

    :param bbox: a bbox (list) returned from Twitter API
    :param token: Weather API token

    :return temp at location (bbox centroid)
    """

    y, x = bbox_to_lat_lon(bbox)
    url = f"http://api.weatherapi.com/v1/current.json?key={token}&q={y},{x}"

    session = requests.Session()
    response = session.get(url)
    weather = json.loads(response.content)

    loc = weather['location']
    logging.info(f"Weather API: {loc['name']}, {loc['region']}, {loc['country']}")

    return weather.get('current').get('temp_f')


def get_twitter_geo_stream(bearer_token, n):
    """
    Runs Twitter sample stream (v2 API) to grab geo data when available (tweet ignored if not available),
        also grabs weather data when geo data found.

    :param bearer_token: Twitter bearer token
    :param n: n number of temps to keep rolling avg on
    """

    url = "https://api.twitter.com/2/tweets/sample/stream?tweet.fields=geo&expansions=geo.place_id&place.fields=full_name,geo"
    temps_deq = deque([], maxlen=n)

    session = requests.Session()
    with session.get(url, headers={'Authorization': f'Bearer {bearer_token}'}, stream=True) as response:
        for line in response.iter_lines():
            if line:
                includes = json.loads(line).get('includes')
                if includes:
                    places = includes.get('places')
                    if places:
                        full_name = places[0]['full_name']
                        logging.info(f"Twitter API: {full_name}")

                        bbox = places[0]['geo']['bbox']
                        temp = bbox_to_temp(bbox, WEATHER_TOKEN)
                        temps_deq.append(temp)
                        rolling_avg = round(sum(temps_deq)/len(temps_deq), 2)

                        with open(f"{output_root}/temps.csv", 'a') as file1, \
                                open(f"{output_root}/rolling_avg.csv", 'a') as file2:
                            file1.write(f'"{full_name}",{temp}\n')
                            file2.write(f'"{full_name}",{rolling_avg}\n')

    return


if __name__ == "__main__":

    try:
        output_root = f"/root/app/output/{RUN_STARTTIME.strftime('%m%d%Y_%H%M%S')}"
        if not os.path.exists(output_root):
            os.makedirs(output_root)

        roll_val = int(os.getenv('ROLL_VAL'))
        get_twitter_geo_stream(TWITTER_TOKEN, roll_val)

    except ValueError as e:
        logging.exception("Is your ROLL_VAL an int?")

    except ConnectionError as e:
        logging.exception("Failed to connect! Are you on wifi?")
