"""Main Utility Hub."""
# flake8: noqa

# internal modules

# external modules

# relative modules
from .colours import Colours
from .database_query import Controller
from .database_create import make_tables
from . import embed_dialog
from . import embed_errors
from . import embed_general
from . import embed_log
from . import embed_mod
from . import functions
#from . import help_format
from . import message_general
from . import permissions


# global attributes
__all__ = ('Colours',
           'Controller',
           'make_tables',
           'embed_dialog', 
           'embed_errors', 
           'embed_general', 
           'embed_log', 
           'embed_mod', 
           'functions', 
           #'help_format', 
           'message_general', 
           'permissions', )
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

# end of code

# end of file
