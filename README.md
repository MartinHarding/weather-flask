# Weather Flask

A simple weather site example with Flask. This is a purely-for-fun experiment.

When a user visits the root path, Weather Flask attempts to resolve the client's IP address to a location and redirect the user to the appropriate path (e.g. `/10036`). If it can't determine a location, it will redirect to `New York, NY`.

If something goes horribly wrong, the index template just neglects to show weather info until a location is entered.

Clone, install, and run dev server:
```shell
git clone https://github.com/martinharding/weather-flask
cd weather-flask
python3 -m venv env && source env/bin/activate
pip install -r requirements.txt
FLASK_APP=app.py FLASK_DEBUG=1 python3 -m flask run
```

## Insights

To reduce the number of requests to the external APIs, it was imperative that I cache the geolocation lookup and weather results. I wrote a super-quick-and dirty file-based caching class to faciliate this, which simply stores the text response of the request to the API.

Flask-Caching and/or correctly setting up your API Gateway / web server (Apache/NGINX) to support appropriate caching is absolutely the correct way to do this. I repeat *do not do it (in production) the way I did it here.* Sometimes it's just fun to reinvent the wheel.

If I was doing this for a practical purpose, I'd probably use Memcached or Redis for external API caching along with (for example) AWS API Gateway response caching. I would also consider proxying the external weather and geolocation APIs through some standalone self-hosted services capable of drawing the data from multiple sources, transparently caching it, and normalizing it into a convenient format. This would allow automatic fail over to different sources if one isn't available (or they changed their API) and simplify the weather app logic so it becomes more of an ignorant display layer.
