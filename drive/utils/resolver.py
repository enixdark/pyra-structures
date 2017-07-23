import inspect
from pyramid.decorator import reify
import sys

def caller_module(depth=1):
    frm = inspect.stack()[depth + 1]
    caller = inspect.getmodule(frm[0])
    return caller

def caller_package(depth=1):
    module = caller_module(depth + 1)
    f = getattr(module, '__file__', '')
    if '__init__.py' in f:
        # module is a package
        return module

    # go up one level to get the package
    package_name = module.__name__.rsplit('.', 1)[0]
    return sys.modules[package_name]

class lazy_callable(object):
    def __init__(self, path):
        self.package = caller_package()
        self.path = path

    @reify
    def callable(self):
        return maybe_resolve(self.path, package=self.package)

    def __call__(self, *args, **kwargs):
        return self.callable(*args, **kwargs)

# borrowed from pyramid.path.DottedNameResolver
def maybe_resolve(value, package=None):
    if not isinstance(value, str):
        return value

    if package is None and value.startswith('.'):
        package = caller_package()

    module = getattr(package, '__name__', None)  # package may be None
    if not module:
        module = None
    if value == '.':
        if module is None:
            raise ValueError(
                'relative name %r irresolveable without package' % (value,)
            )
        name = module.split('.')
    else:
        name = value.split('.')
        if not name[0]:
            if module is None:
                raise ValueError(
                    'relative name %r irresolveable without '
                    'package' % (value,))
            module = module.split('.')
            name.pop(0)
            while not name[0]:
                module.pop()
                name.pop(0)
            name = module + name

    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used += '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)  # pragma: no cover

    return found
