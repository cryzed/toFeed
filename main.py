import time

import flask
import werkzeug.contrib.cache

import toFeed.adapters


app = flask.Flask(__name__)
adapters = toFeed.adapters.get_adapters()
cache = werkzeug.contrib.cache.SimpleCache()
cached = {}


@app.route('/<path:path>')
def index(path):
    if not path in adapters:
        return 'No matching adapter found', 404

    args = []
    kwargs = {}
    for key, value in flask.request.args.items():
        if value:
            kwargs[key] = value
        else:
            args.append(key)

    instance = adapters[path](*args, **kwargs)
    if flask.request.full_path in cached:
        if time.time() - cached[flask.request.full_path] < instance.cache_timeout:
            return cache.get(flask.request.full_path)

    feed = instance.to_feed()
    cache.set(flask.request.full_path, feed)
    cached[flask.request.full_path] = time.time()
    return feed


def main():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    main()
