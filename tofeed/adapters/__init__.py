"""
Adapters
~~~~~~~~

.. TODO: Still needs to rewritten and converted to reST.

.. code-block:: none

    Parameters are passed via GET parameters and used to instantiate the "Adapter"
    class instance. Parameters without a value are interpreted as positional
    arguments, and parameters with a value as a keyword argument.

    To write your own adapter you need to create a new module in "toFeed.packages"
    which has a top-level "ROUTE" attribute. This attribute is the first part of
    the route to your actual adapter class. All classes which inherit from the base
    adapter class in this module are automatically recognized. Your class needs to
    provide a static "ROUTE" attribute as well, which is the second part of the
    route to your adapter: for example "twitter/timeline". If the static "PRIMARY"
    attribute in your adapter class is set to true, it will also be accessible
    simply via the module "ROUTE" attribute, i.e. only "twitter".

    You need to add "\*\*kwargs" to the argument list and call this in your
    constructor:

        Adapter.__init__(self, **kwargs)

    All positional and keyword arguments you define before "\*\*kwargs" in your
    constructor can be passed via the GET parameters. The "to_feed"-method needs to
    be overriden and return a valid feed syndication format with your content. The
    included Python packages in "toFeed.formats" can be used to do that.

    To get a better idea, simply take a look at the already existing adapters.
"""

import pkgutil
import inspect
import importlib


class Adapter(object):
    """
    The base adapter class. Each adapter needs to inherit from this class.

    :var str ROUTE:
        The route leading to the adapter; must be set by the inheriting adapter.

    :var bool PRIMARY:
        If set to ``True``, the adapter will be recognized as the module's
        primary adapter and be directly accessible via the module's route in
        addition to its own route. In this case implementing the :attr:`ROUTE`
        class variable is optional.

    :var str CACHE_TIMEOUT:
        The default time to cache the content returned by the adapter's
        implementation of :meth:`to_feed`.

    :Note: Parameters received by the constructor will always be strings and
        must be handled accordingly. This is because the adapter objects are
        instantiated with parameters received by the GET HTTP request handled
        by the main module providing the webservice.

    :param str cache_timeout: The time to cache the content returned by the
        adapter's implementation of :meth:`to_feed`.
    """
    ROUTE = None
    PRIMARY = False
    CACHE_TIMEOUT = '120'

    def __init__(self, cache_timeout=CACHE_TIMEOUT):
        self.cache_timeout = int(cache_timeout)

    def to_feed(self):
        """
        Must be implemented by the inheriting adapter.

        :rtype: str
        :returns: The generated feed content.
        """
        raise NotImplementedError('The adapter must implement the "to_feed" method')


def _is_adapter(object_):
    """
    Returns True if object_ inherits from Adapter. Used with inspect.getmembers
    to filter the adapter classes from the adapter modules.
    """
    if not inspect.isclass(object_):
        return False

    base_classes = inspect.getmro(object_)

    # Ignore base adapter class
    if base_classes == (Adapter, object):
        return False

    return Adapter in base_classes


def get_adapters():
    """
    :rtype: dict
    :returns: Mapping of the adapter classes to their routes.
    """
    adapters = {}
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        module = importlib.import_module('.' + module_name, __name__)
        primary_adapter = None
        for member_name, adapter in inspect.getmembers(module, _is_adapter):

            # If the adapter is the primary adapter of the module, make it
            # directly accessible via the module route as well.
            if adapter.PRIMARY:
                if not primary_adapter is None:
                    raise RuntimeError('There can not be more than one primary adapter within the same module ("%s", "%s")' % (primary_adapter.__name__, member_name))

                adapters[module.ROUTE] = adapter
                primary_adapter = adapter

                # If the adapter is the primary adapter a route is optional
                if not adapter.ROUTE:
                    continue

            if adapter.ROUTE is None:
                raise NotImplementedError('The adapter class "%s" must implement a valid "ROUTE" class variable' % member_name)

            adapters[module.ROUTE + '/' + adapter.ROUTE] = adapter
    return adapters
