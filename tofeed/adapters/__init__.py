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
        addition to its own route. If this is the case, implementing the
        :attr:`ROUTE` class variable is optional.

    :var str CACHE_TIMEOUT:
        The default time to cache the content returned by the adapter's
        implementation of :meth:`to_feed`.

    :Note: Parameters received by the constructor are strings and must be
        handled accordingly.

    :parameter str cache_timeout: The time to cache the content returned by the
        adapter's implementation of :meth:`to_feed`.
    """
    ROUTE = None
    PRIMARY = False
    CACHE_TIMEOUT = '120'

    def __init__(self, cache_timeout=CACHE_TIMEOUT):
        if self.ROUTE is None:
            raise NotImplementedError('The adapter must implement a "ROUTE" class variable')

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
    :rtype: bool
    :returns: ``True`` if ``object_`` inherits from :class:`Adapter`.
    """
    if not inspect.isclass(object_):
        return False

    base_classes = inspect.getmro(object_)

    # Ignore base adapter class
    if base_classes == (Adapter, object):
        return False

    return Adapter in base_classes


def _get_adapters():
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
                    raise RuntimeError('There can only be one primary adapter within a module ("%s", "%s")' % (primary_adapter.__name__, member_name))

                adapters[module.ROUTE] = adapter
                primary_adapter = adapter

                # If the adapter is the primary adapter a route is optional
                if not adapter.ROUTE:
                    continue

            adapters[module.ROUTE + '/' + adapter.ROUTE] = adapter
    return adapters
