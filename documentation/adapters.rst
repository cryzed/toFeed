Adapters
~~~~~~~~
Adapters are the heart of toFeed. They take care of retrieving, scraping and
generating the syndication feeds for sites you wish to subscribe to.

Adapters can be grouped together in modules. Such a module must contain a
``ROUTE`` top-level constant, which is used as the first part of the URL you
give your news aggregator to retrieve the content. The complete URL is built by
appending the ``ROUTE`` class variable of the specific adapter.

For example the built-in adapters include an adapter specific to parsing the
Twitter timeline widget data. In the ``twitter`` module the ``ROUTE`` equals
``twitter`` and the adapter's ``ROUTE`` class variable equals
``timelineWidget``. That means this adapter would be reachable at:
``twitter/timelineWidget``.

Notable also is that it's the primary adapter of this module, meaning instead of
having to write ``twitter/timelineWidget``, simply using ``twitter`` i.e. the
``ROUTE`` of the module itself is sufficient.

When opening a route you can pass in arguments and keyword arguments which the
adapters can use to implement certain functionality, for example limiting the
title length of feed items. This is simply done via GET parameters. A
``?key=value`` pair would be interpreted as a keyword argument. A key without a
value, i.e. ``?test& ...`` would be a simple positional argument. If an adapter
needs to accept such parameters you need to define them in the constructor.

It is good practice to accept ``**kwargs`` in your adapter's constructor and
forward them to the base adapter's constructor, this way certain functionality
that makes sense for every adapter can be implemented and utilized. Currently
this is limited to manually setting the cache timeout, e.g.
``twitter?cache_timeout=300``.


.. automodule:: tofeed.adapters
   :members:
