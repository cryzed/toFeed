import time

import flask
import werkzeug.contrib.cache

import tofeed.adapters


app = flask.Flask(__name__)
adapters = tofeed.adapters._get_adapters()
cache = werkzeug.contrib.cache.SimpleCache()
cached_at = {}


def _split_request_args(request_arguments):
    """
    Splits the request arguments into a list of arguments and keyword arguments.
    """
    arguments = []
    keyword_arguments = {}
    for key, value in request_arguments.items():
        if value:
            keyword_arguments[key] = value
        else:
            arguments.append(key)
    return arguments, keyword_arguments


@app.route('/<path:path>')
def index(path):
    if not path in adapters:
        return 'No matching adapter found', 404

    arguments, keyword_arguments = _split_request_args(flask.request.args)
    instance = adapters[path](*arguments, **keyword_arguments)

    # Using a cache key consisting of the class object and the request arguments
    # allows caching of different routes leading to the same adapter, for
    # example the primary adapter.
    cache_key = (adapters[path], flask.request.args)
    if cache_key in cached_at:
        if time.time() - cached_at[cache_key] < instance.cache_timeout:
            return cache.get(cache_key)

    feed = instance.to_feed()
    cache.set(cache_key, feed)
    cached_at[cache_key] = time.time()
    return feed


def main():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    main()
