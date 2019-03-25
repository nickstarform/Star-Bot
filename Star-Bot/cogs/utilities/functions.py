"""Generalized Functions Hub."""

# internal modules
import datetime
from enum import Enum

# external modules

# relative modules

# global attributes
__all__ = ('current_time', 'ModAction')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


# Basic functions


def current_time():
    """
    Get Current time in botworld.

    Parameters
    ----------

    Returns
    -------
    str
        String format (Day Mon, DD YYYY HH:MM) of datetime in UTC
    """
    time = datetime.datetime.utcnow()
    return time.strftime('%A, %b %d %Y %H:%M')


class ModAction(Enum):
    """Moderation Types.

    Parameters
    ----------

    Returns
    ----------
    """

    MISC = 0
    KICK = 1
    BAN = 2
    UNBAN = 3

# end of code

# end of file
