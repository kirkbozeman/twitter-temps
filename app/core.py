import os
import requests
import json
from collections import deque
from datetime import datetime
from shapely.geometry import box

import logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)-8s %(message)s")

TWITTER_TOKEN = os.getenv('TWITTER_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')
RUN_STARTTIME = datetime.now()


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

    logging.info(f"Weather API: {loc['name']}, {loc['region']}, {loc['country']}")

    return temp_f


def get_geo_stream(bearer_token, n):
    """
    Runs Twitter sample stream to grab geo data when available, also grabs weather data when geo data found
        Follows docs at: https://2.python-requests.org/en/master/user/advanced/#body-content-workflow
    """

    url = "https://api.twitter.com/2/tweets/sample/stream?tweet.fields=geo&expansions=geo.place_id&place.fields=full_name,geo"
    temps_deq = deque([], maxlen=n)

    output_root = f"/root/app/output/{RUN_STARTTIME.strftime('%m%d%Y_%H%M%S')}"
    os.makedirs(output_root)

    session = requests.Session()
    with session.get(url, headers={'Authorization': f'Bearer {bearer_token}'}, stream=True) as response:
        for line in response.iter_lines():
            if line:
                includes = json.loads(line).get('includes')
                if includes:
                    places = includes.get('places')
                    full_name = places[0]['full_name']
                    bbox = places[0]['geo']['bbox']

                    logging.info(f"Twitter API: {full_name}")

                    temp = bbox_to_temp(bbox, WEATHER_TOKEN)
                    temps_deq.append(temp)
                    rolling_avg = round(sum(temps_deq)/len(temps_deq), 2)

                    with open(f"{output_root}/temps.csv", 'a') as file:
                        file.write(f'"{full_name}",{temp}\n')

                    with open(f"{output_root}/rolling_avg.csv", 'a') as file:
                        file.write(f'"{full_name}",{rolling_avg}\n')


if __name__ == "__main__":

    try:
        get_geo_stream(TWITTER_TOKEN, 5)
    except Exception as e:
        logging.exception(e)
