"""Main Hub of Colours."""

# internal modules
from enum import Enum

# external modules

# relative modules

# global attributes
__all__ = ('Colours',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class Colours(Enum):
    """Generalized, Uniform Colour class."""

    CATASTROPHIC = 0xFD0000  # BRIGHT-RED, MAJOR ERRORS
    ERROR = 0xD01F00  # RED, ERRORS
    WARNING = 0xD07300  # ORANGE, WARNINGS BUT CONTINUE
    SUCCESS = 0x0CB806  # GREEN, SUCCESS
    CHANGE_U = 0x00F4E2  # LIGHT-BLUE, USER CHANGES
    CHANGE_M = 0x00D08C  # GREENISH-BLUE, MESSAGE CHANGES
    CHANGE_S = 0x0021c7  # DARK-BLUE, STATE CHANGES (VOICE)
    CHANGE_G = 0x007CC7  # DARKER-BLUE, GUILD CHANGES
    DIALOG_T = 0x9ED031  # YELLOW, TEMPORARY FOR DIALOGS
    COMMANDS = 0xAC91F5  # PURPLE, OUTPUT OF ONE-WAY COMMANDS

# end of code

# end of file
