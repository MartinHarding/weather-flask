import json
import os
import requests
import urllib.parse

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory

from file_cache import FileCache


app = Flask(__name__, static_url_path='')

# TODO: Store global variables in app.config
CACHE_TIMEOUT = 3600 # Cache weather results for 1 hour
CACHE_DIR = './cache'
ASSETS_DIR = './public'

app.file_cache = FileCache(cache_dir=CACHE_DIR, timeout=CACHE_TIMEOUT)


@app.route('/', methods=['GET'])
@app.route('/<location>', methods=['GET'])
def index(location=None):
    """Display a page showing the next 24 hours of weather"""

    # If location code param is set, redirect to that location code page
    if request.args.get('location'):
            return redirect('/'+request.args.get('location'))

    kwargs = {}

    # Look up IP address location if location parameter isn't set
    if not location:
        # TODO: handle x-forwarded-for header (e.g. API Gateway, Load Balancers)
        #: Pass IP as a query parameter to simulate geolocation
        remote_ip = request.args.get('ip') if request.args.get(
            'ip') else request.remote_addr
        # Get geolocation info for the remote (client) IP address
        ip_info = geolocate(remote_ip)
        location = ip_info.get('postal', False) if ip_info else 'New York, NY'

    cache_key = 'w_{}.html'.format(location) if location else 'index.html'
    iscached = app.file_cache.check(cache_key)

    if iscached and not request.args.get('nocache'):
        return send_from_directory(CACHE_DIR, cache_key)

    elif location:
        if os.path.exists('{}/{}'.format(ASSETS_DIR, location)):
            return send_from_directory(ASSETS_DIR, location)
        kwargs['location'] = location
        weather = yahoo_weather(location)
        if weather:
            kwargs['weather'] = weather
            kwargs['weather_json'] = json.dumps(weather, indent=4)

    rendered = render_template('index.html', **kwargs)

    app.file_cache.save(cache_key, rendered)
    return rendered

def yahoo_weather(location: str) -> dict:
    """Get weather for a given location code

    Args:
        location (str): location code to look up

    Returns:
        dict: weather forecast for the location code
    """
    cache_key = 'w_{}.json'.format(location)
    cached = app.file_cache.load(cache_key)
    if cached and not request.args.get('nocache'):
        return json.loads(cached)
    else:
        yql = """select * from weather.forecast where woeid in (select woeid from
                geo.places(1) where text="{}")""".format(location)
        url = 'https://query.yahooapis.com/v1/public/yql?{}'.format(
            urllib.parse.urlencode({'q': yql.strip(), 'format': 'json'}))
        try:
            # TODO: Add some handling for locations without weather data
            resp = requests.get(url)
            if resp.ok:
                weather = resp.json()['query']['results']['channel']
                app.file_cache.save(cache_key, json.dumps(weather, indent=4))
                return weather
            else:
                app.logger.warn(resp.text)
        except Exception as error:
            app.logger.error(error)

def geolocate(ip: str) -> dict:
    """Look up information about a given IP address

    Returns:
        dict: geolocation information for the IP
    """
    cache_key = 'i_{}.json'.format(ip)
    # Geolocation changes infrequently, so cache timeout is set to 90 days
    cached = app.file_cache.load(cache_key, timeout=7776000)
    if cached and not request.args.get('nocache'):
        return json.loads(cached)
    else:
        try:
            resp = requests.get('https://api.ipdata.co/{}'.format(ip))
            if resp.ok:
                ip_info = resp.json()
                app.file_cache.save(cache_key, json.dumps(ip_info, indent=4))
                return ip_info
            else:
                app.logger.warn(resp.text)
        except Exception as error:
            app.logger.error(error)

