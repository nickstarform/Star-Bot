"""Embed Constructors for Errors Hub."""

# internal modules

# external modules
import discord
import datetime

# relative modules
from cogs.utilities.functions import current_time
from cogs.utilities import Colours
from config.config import Config

# global attributes
__all__ = ('BotPermissionErrorEmbed',
           'UserPermissionErrorEmbed',
           'InternalErrorEmbed',
           'PanicErrorEmbed',
           'ModErrorEmbed')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class BotPermissionErrorEmbed(discord.Embed):
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

    def __init__(self, action, required_perm=None):
        ccolour = Colours.ERROR.value
        ctitle = f'Insufficient Permissions'
        cdesc = f'The bot doesn\'t have the required ' +\
            f'permissions for the command **{action}** and ' +\
            f'needs perm **{required_perm}**'
        super().__init__(
            color=ccolour,
            title=ctitle,
            description=cdesc)
        self.set_footer(text=current_time())


class UserPermissionErrorEmbed(discord.Embed):
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

    def __init__(self, action, required_perm=None):
        ccolour = Colours.ERROR.value
        ctitle = f'Insufficient Permissions'
        cdesc = f'You don\'t have the required ' +\
            f'permissions for the command **{action}** and ' +\
            f'you need perm **{required_perm}**'
        super().__init__(
            color=ccolour,
            title=ctitle,
            description=cdesc)
        self.set_footer(text=current_time())


class InternalErrorEmbed(discord.Embed):
    """
    Some random error occured.

    Parameters
    ----------
    message : str
        Message thrown with the command.

    Returns
    -------
    """

    def __init__(self, message):
        ccolour = Colours.ERROR.value
        ctitle = f'Error with command!'
        cdesc = f'{message}'
        super().__init__(
            color=ccolour,
            title=ctitle,
            description=cdesc)
        self.set_footer(text=current_time())


class PanicErrorEmbed(discord.Embed):
    """
    Something Failed Majorly

    Parameters
    ----------

    Returns
    -------
    """

    def __init__(self):
        ccolour = Colours.CATASTROPHIC.value
        ctitle = f'INTERNAL ERROR!'
        cdesc = f'Contact the bot-owner <@{Config.owner_id.value}> ' +\
            f'or the bot-developer <@{Config.devel_id.value}>.\nYou ' +\
            f'can also join the bot support server ' +\
            f'[Click!]({Config.support_server.value}).'
        super().__init__(
            color=ccolour,
            title=ctitle,
            description=cdesc)
        self.set_footer(text=current_time())


class ModErrorEmbed(discord.Embed):
    """
    General Moderation Error

    Parameters
    ----------

    Returns
    -------
    """

    def __init__(self):
        ccolour = Colours.ERROR.value
        ctitle = f'Incorrect User!'
        cdesc = f'Unable to perform action on user. Most likely ' +\
            f'typed in the wrong id.'
        super().__init__(
            color=ccolour,
            title=ctitle,
            description=cdesc)
        self.set_footer(text=current_time())

# end of code

# end of file
