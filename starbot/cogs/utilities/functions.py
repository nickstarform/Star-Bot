"""Generalized Functions Hub."""

# internal modules
import datetime
from enum import Enum
import re
from typing import Optional

# external modules
from asyncpg import Record

# relative modules

# global attributes
__all__ = ('current_time',
           'ModAction',
           'extract_member_id',
           'extract_channel_id',
           'extract_role_id',
           'extract_guild_id',
           'extract_time',
           'extract_float',
           'clean_command',
           'parse',
           'chunks')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


# Basic functions

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def parse(record: Record) -> Optional[list]:
    """Parsing Record values.

    Parameters
    ----------
    record : Record
        The connection pool

    Returns
    ----------
    list
        Results from the record in list format
    """
    try:
        return list(record.items())
    except AttributeError:
        return None


def current_time(ordinal: bool=False):
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
    if ordinal:
        return time.toordinal()
    else:
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


def clean_command(argument: str):
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
    i = 1
    for x in argument:
        if x != ' ':
            i += 1
        else:
            break
    return argument[i:]

def is_id(argument: str):
    """Check if argument is #.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    status = True
    for x in argument:
        try:
            _ = int(x)
        except:
            status = False
            return False
    return True


def extract_member_id(argument: str):
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
    if argument.strip(' ') == '':
        return ''
    if not is_id(argument.replace('<', '').replace('>', '').replace('@', '')):
        return ''
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


def extract_channel_id(argument: str):
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
    if argument.strip(' ') == '':
        return
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


def extract_role_id(argument: str):
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
    if argument.strip(' ') == '':
        return
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


def extract_guild_id(argument: str):
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
    if argument.replace(' ', '') == '':
        return
    print(f'<{argument}>')
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


def extract_float(argument: str):
    """Extract float from string.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare float
    """
    ret = ''
    for char in argument:
        try:
            if char != '.':
                ret += str(int(char))
            else:
                ret += '.'
        except:
            return ret
    return ret


def extract_time(argument: str):
    """Try to autocheck for time.

    Checks in order, for these datastructures

    #y#mo#d#h#m#s (any combination in order thereof)
    #:#:# (h:m:s)
    #:# (m:s)
    # (defaults to seconds)

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    regex = r'([0-9]*y)?([0-9]*mo)?([0-9]*w)?([0-9]*d)?([0-9]*h)?([0-9]*m)?([0-9]*s)?'  # noqa
    reg_map = (
        1. * 60. * 60. * 24. * 365.25,  # 'y'
        1. * 60. * 60. * 24. * (365.25 / 12.),  # 'mo
        1. * 60. * 60. * 24. * 7.,  # 'w'
        1. * 60. * 60. * 24.,  # 'd'
        1. * 60. * 60.,  # 'h'
        1. * 60.,  # 'm'
        1.)  # 's'
    argument = argument.lower().replace(' ', '')
    if ':' in argument:
        # parse by :
        args = argument.split(':')
        if len(args) > 3:
            return False
        args = sum([float(a) * 60. ** i for i, a in enumerate(args[::-1])])
        return args
    else:
        args = 0
        matches = re.finditer(regex, argument, re.MULTILINE)
        match = matches.__next__()
        for groupNum in range(0, len(match.groups())):
            grp = match.group(groupNum + 1)
            if not isinstance(grp, type(None)):
                flt = extract_float(grp)
                args += float(flt) * reg_map[groupNum]
        return args

# end of code

# end of file
