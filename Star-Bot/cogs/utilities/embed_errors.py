"""Embed Constructors for Errors Hub."""

# internal modules

# external modules
import discord

# relative modules
from cogs.utilities import Colours, current_time, generic_embed
from config import Config

# global attributes
__all__ = ('botpermissionerrorembed',
           'userpermissionerrorembed',
           'internalerrorembed',
           'panicerrorembed',
           'moderrorembed')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def botpermissionerrorembed(action: str, required_perm: str):
    """
    Handle Invalid Bot Permissions.

    Will use this embed for when the bot doesn't have
    the valid permissions for the thrown command.

    Parameters
    ----------
    action : string
        Command that was tried
    required_perm : str
        Permissions that are needed

    Returns
    -------
    """
    ccolour = Colours.ERROR
    ctitle = f'Insufficient Permissions'
    cdesc = f'The bot doesn\'t have the required ' +\
        f'permissions for the command **{action}** and ' +\
        f'needs perm **{required_perm}**'
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def userpermissionerrorembed(action: str, required_perm: str):
    """
    Handle Invalid User Permissions.

    Will use this embed for when the user doesn't have
    the valid permissions for the thrown command.

    Parameters
    ----------
    action : string
        Command that was tried
    required_perm : str
        Permissions that are needed

    Returns
    -------
    """
    ccolour = Colours.ERROR
    ctitle = f'Insufficient Permissions'
    cdesc = f'You don\'t have the required ' +\
        f'permissions for the command **{action}** and ' +\
        f'you need perm **{required_perm}**'
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def internalerrorembed(message: str):
    """
    Some random error occured.

    Parameters
    ----------
    message : str
        Message thrown with the command.

    Returns
    -------
    """
    ccolour = Colours.ERROR
    ctitle = f'Error with command!'
    cdesc = f'{message}'
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def panicerrorembed():
    """
    Something Failed Majorly

    Parameters
    ----------

    Returns
    -------
    """
    ccolour = Colours.CATASTROPHIC
    ctitle = f'INTERNAL ERROR!'
    cdesc = f'Contact the bot-owner <@{Config.owner_id.value}> ' +\
        f'or the bot-developer <@{Config.devel_id.value}>.\nYou ' +\
        f'can also join the bot support server ' +\
        f'[Click!]({Config.support_server.value}).'
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def moderrorembed():
    """
    General Moderation Error

    Parameters
    ----------

    Returns
    -------
    """
    ccolour = Colours.ERROR
    ctitle = f'Incorrect User!'
    cdesc = f'Unable to perform action on user. Most likely ' +\
        f'typed in the wrong id.'
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]

# end of code

# end of file
