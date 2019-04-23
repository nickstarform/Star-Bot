"""Generalized Functions Hub."""

# internal modules
import datetime
from enum import Enum
import re
from typing import Optional
from time import sleep
import math

# external modules
from asyncpg import Record
from discord.ext import commands
import discord

# relative modules

# global attributes
__all__ = ('current_time',
           'ModAction',
           'extract_id',
           'extract_time',
           'extract_float',
           'clean_command',
           'parse',
           'chunks',
           'bannedmember',
           'flatten',
           'get_role',
           'get_member',
           'get_channel',
           'lessen_list',
           'create_fake',
           'type_force',
           'Timer')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


# Basic functions

def type_force(val: str, dtype):
    if isinstance(val, dtype):
        return val
    else:
        if isinstance(dtype, list) or isinstance(dtype, tuple):
            val = val.strip('[').strip(']')
            val = val.split(',')
            if dtype == list:
                return val
            else:
                return tuple(val)
        elif isinstance(dtype, int):
            return int(val)
        elif isinstance(dtype, float):
            return float(val)
        elif isinstance(dtype, bool):
            if val.lower() == 'true':
                return True
            else:
                return False
        else:
            return val

def create_fake(target_id: str, dtype: str='member'):
    if dtype == 'member':
        return create_fake_user(target_id)


def create_fake_user(user_id: str):
    member = fake_object(int(user_id))
    member.name = 'GenericUser'
    member.discriminator = '0000'
    member.joined_at = datetime.datetime.utcnow()
    return member

class fake_object:

    def __init__(self, snowflake):
        self.id = int(snowflake)
        self.name = ''
        self.created_at = datetime.datetime.utcnow()

    def __repr__(self):
        return ''.format()

    def __eq__(self, other):
        return self.id == other.id

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


def flatten(ilist):
    ret = []
    for i in ilist:
        if not isinstance(i, type(None)):
            if i is not False and i != '':
                ret.append(i)
    return ret


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def parse(records):
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
        ret = []
        if isinstance(records, list):
            for record in records:
                ret.append([[key, val] for (key, val) in record.items()])
            return ret
        else:
            return [[key, val] for (key, val) in records.items()]
    except AttributeError:
        return []


def time_conv(dt: datetime):
    """
    Get Current time in botworld.

    Parameters
    ----------

    Returns
    -------
    str
        String format (Day Mon, DD YYYY HH:MM) of datetime in UTC
    """
    if isinstance(dt, datetime.timedelta):
        dt = dt.total_seconds()
        y = int(abs(dt) // int(60. * 60. * 24. * 365.25))
        r = int(abs(dt) % int(60. * 60. * 24. * 365.25))
        mo = int(r // int(60. * 60. * 24.* 30))
        r = int(r % int(60. * 60. * 24. * 30))
        d = int(r // int(60. * 60. * 24.))
        r = int(r % int(60. * 60. * 24.))
        h = int(r // int(60. * 60.))
        r = int(r % int(60. * 60.))
        m = int(r // int(60.))
        s = int(r % int(60.))
        strings = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
        ret = []
        for i, f in enumerate([y, mo, d, h, m, s]):
            if f != 0:
                ret.append(f'{f} {strings[i]}')
        if dt < 0:
            return ' '.join(ret) + ' ago'
        else:
            return ' '.join(ret)
    return dt.strftime('%A, %b %d %Y %H:%M')


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


def clean_str(argument: str, dtype: str='role'):
    argument = str(argument)
    general = argument.replace('<', '').replace('>', '')\
                      .replace('@', '')
    if dtype == 'role':
        return general.replace('&', '')
    if dtype == 'channel':
        return general.replace('#', '')
    else:
        return general.replace('#', '').replace('&', '')


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


def get_channel(ctx, argument: str):
    """Tries to return a channel object.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    discord.Channel
        channel object to return
    """
    cleaned = clean_str(argument).lower()
    try:
        ret = extract_id(argument, 'channel')
        if not ret:
            ret = discord.utils.find(lambda m: (m.id == ret) or
                (m.name.lower() == cleaned), ctx.guild.channels) # noqa
        else:
            return ctx.guild.get_channel(int(ret))
        if ret:
            return ret
    except:
        return False


def get_role(ctx, argument: str):
    """Tries to return a role object.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    discord.Role
        role object to return
    """
    cleaned = clean_str(argument, 'role').lower()
    try:
        ret = extract_id(argument, 'role')
        if not ret:
            ret = discord.utils.find(lambda m:
                (m.name.lower() == cleaned), ctx.guild.roles)
        else:
            return ctx.guild.get_role(int(ret))
        if ret:
            return ret
    except:
        return False


def get_member(ctx, argument: str):
    """Tries to return a member object.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    discord.Member
        member object to return
    """
    ret = extract_id(argument, 'member')
    t_st = clean_str(argument, 'member').lower()
    if not ret:
        ret = discord.utils.find(lambda m: (m.id == ret) or (m.name.lower() == t_st), ctx.guild.members)
    else:
        ret = ctx.guild.get_member(int(ret))
    if not ret:
        ret = ctx.guild.get_member_named(t_st)
    if ret:
        return ret
    else:
        return None

def extract_id(argument: str, dtype: str='member'):
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
    argument = clean_str(argument, dtype)
    if is_id(argument):
        return argument
    if dtype == 'member':
        regexes = (
            r'\<?\@?(\d{17,})\>?',  # '<@!?#17+>'
            r'\<?\@?(\d{1,})\>?',  # '<@!?#+>'
            r'?(\d{17,})',  # '!?#17+>'
            r'?(\d{1,})',  # '!?#+>'
        )
    elif dtype == 'role':
        regexes = (
            r'\<?\@?\&?(\d{17,})\>?',  # '<@!?#17+>'
            r'\<?\@?\&?(\d{1,})\>?',  # '<@!?#+>'
            r'?(\d{17,})',  # '!?#17+>'
            r'?(\d{1,})',  # '!?#+>'
        )
    elif dtype == 'channel':
        regexes = (
            r'\<?\#?(\d{17,})\>?',  # '<@!?#17+>'
            r'\<?\#?(\d{1,})\>?',  # '<@!?#+>'
            r'?(\d{17,})',  # '!?#17+>'
            r'?(\d{1,})',  # '!?#+>'
        )
    else:
        regexes = (
            r'?(\d{17,})',  # '!?#17+>'
            r'?(\d{1,})',  # '!?#+>'
        )
    i = 0
    member_id = ''
    while i < len(regexes):
        regex = regexes[i]
        try:
            match = re.finditer(regex, argument, re.MULTILINE)
        except:
            match = None
        i += 1
        if match is None:
            continue
        else:
            match = [x for x in match]
            if len(match) > 0:
                match = match[0]
                member_id = int(match[0], base=10)
                return str(member_id)
    return None

async def bannedmember(ctx, argument):
    ban_list = await ctx.guild.bans()
    member_id = extract_id(argument, 'member')
    if member_id is not None:
        entity = discord.utils.find(
            lambda u: str(u.user.id) == str(member_id), ban_list)
        return entity
    else:
        raise commands.BadArgument("Not a valid previously-banned member.")

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
    regex = r'(\d*y)?(\d*mo)?(\d*w)?(\d*d)?(\d*h)?(\d*m)?(\d*s)?'  # noqa
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

def lessen_list(ilist: list, amount: int):
    """Try to split list intelligently.

    This is a highly specific command, but it takes
    the input list, counts up the length of its 
    constituents, and tries to output a new
    list of the same elements but for a 
    length specified by amount.

    Example:
        ilist = [1,2,3,4,5], amount = 3
        yields [1,2,3]
        ilist = [1,24,3,4,5], amount = 3
        yields [1,24]
        ilist = [1,242,3,4,5], amount = 3
        yields [1]
    Parameters
    ----------
    ilist: list
        list to modify
    amount: int
        max length of sum of parts

    Returns
    ----------
    list
        shortened list
    """
    sum_c = 0
    sum_n = 0
    i = 0
    ret = []
    while i < (len(ilist) - 1):
        sum_c += len(str(ilist[i]))
        sum_n = len(str(ilist[i + 1]))
        ret.append(ilist[i])
        if (sum_c > amount) or (sum([sum_c, sum_n]) > amount):
            i = len(ilist)
        i += 1
    return ret

class Timer:
    """Context manager to measure how long the indented block takes to run."""

    def __init__(self):
        self.start: float = None
        self.end: float = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    async def __aenter__(self):
        return self.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.__exit__(exc_type, exc_val, exc_tb)

    def __str__(self):
        return f'{self.duration:.3f}ms'

    @property
    def duration(self):
        """Duration in ms."""
        return (self.end - self.start) * 1000

# end of code

# end of file
