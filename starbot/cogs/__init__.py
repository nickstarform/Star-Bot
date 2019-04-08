"""File handles general loading."""

# internal modules

# external modules

# relative modules
from . import utilities
from .fun import Fun
from .owner import Owner
from .general import General
from .moderation import Moderation
from .administration import Administration

# global attributes
__all__ = ('utilities',
           'Owner',
           'Fun',
           'General',
           'Moderation',
           'Administration')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

# end of code

# end of file
