"""Generalized Functions Hub."""

# internal modules
import datetime
from enum import Enum
import re

# external modules

# relative modules

# global attributes
__all__ = ('current_time',
           'ModAction',
           'extract_member_id',
           'extract_channel_id',
           'extract_role_id',
           'extract_guild_id',)
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


def extract_member_id(argument):
    """Check if argument is # or <@#>.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    regexes = (
        r'\\?\<\@?([0-9]{17})\>',  # '<@!?#17+>'
        r'\\?\<\@?([0-9]+)\>',  # '<@!?#+>'
        r'?([0-9]{17})',  # '!?#17+>'
        r'?([0-9]+)',  # '!?#+>'
    )
    i = 0
    member_id = None
    while i < len(regexes):
        regex = regexes[i]
        match = re.findall(regex, argument)
        i += 1
        if (match is not None) and (len(match) > 0):
            member_id = int(match[0], base=10)
            return str(member_id).strip(' ')
    return str(member_id).strip(' ')


def extract_channel_id(argument):
    """Check if argument is # or <##>.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    regexes = (
        r'\\?\<\#?([0-9]{17})\>',  # '<@!?#17+>'
        r'\\?\<\#?([0-9]+)\>',  # '<@!?#+>'
        r'?([0-9]{17})',  # '!?#17+>'
        r'?([0-9]+)',  # '!?#+>'
    )
    i = 0
    channel_id = None
    while i < len(regexes):
        regex = regexes[i]
        match = re.findall(regex, argument)
        i += 1
        if (match is not None) and (len(match) > 0):
            channel_id = int(match[0], base=10)
            return str(channel_id).strip(' ')
    return str(channel_id).strip(' ')


def extract_role_id(argument):
    """Check if argument is # or <@&#>.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    regexes = (
        r'\\?\<\@\&?([0-9]{17})\>',  # '<@!?#17+>'
        r'\\?\<\@\&?([0-9]+)\>',  # '<@!?#+>'
        r'?([0-9]{17})',  # '!?#17+>'
        r'?([0-9]+)',  # '!?#+>'
    )
    i = 0
    role_id = None
    while i < len(regexes):
        regex = regexes[i]
        match = re.findall(regex, argument)
        i += 1
        if (match is not None) and (len(match) > 0):
            role_id = int(match[0], base=10)
            return str(role_id).strip(' ')
    return str(role_id).strip(' ')


def extract_guild_id(argument):
    """Check if argument is # or <@&#>.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    regexes = (
        r'?([0-9]{17})',  # '!?#17+>'
        r'?([0-9]+)',  # '!?#+>'
    )
    i = 0
    role_id = None
    while i < len(regexes):
        regex = regexes[i]
        match = re.findall(regex, argument)
        i += 1
        if (match is not None) and (len(match) > 0):
            role_id = int(match[0], base=10)
            return str(role_id).strip(' ')
    return str(role_id).strip(' ')


# end of code

# end of file
