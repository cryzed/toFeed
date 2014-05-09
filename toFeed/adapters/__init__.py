import pkgutil
import inspect
import importlib

ADAPTERS_PACKAGE_PATH = 'toFeed.adapters'


# All adapters need to inherit this base class.
class Adapter(object):
    ROUTE = ''
    CACHE_TIMEOUT = '120'

    def __init__(self, cache_timeout=CACHE_TIMEOUT):
        self.cache_timeout = int(cache_timeout)

    def to_feed(self):
        return ''


# Returns true if object is a class which inherits from the adapter base class
def _is_adapter(object_):
    if not inspect.isclass(object_):
        return False

    base_classes = inspect.getmro(object_)

    # Ignore base adapter class
    if base_classes == (Adapter, object):
        return False

    return Adapter in base_classes


def get_adapters():
    adapters = {}

    for _, name, _ in pkgutil.iter_modules(__path__):
        module = importlib.import_module('.' + name, ADAPTERS_PACKAGE_PATH)
        for _, adapter in inspect.getmembers(module, _is_adapter):
            adapters[module.ROUTE + '/' + adapter.ROUTE] = adapter

    return adapters
