"""General Embed Constructor Hub."""

# internal modules

# external modules
import discord
import asyncio
from discord.ext import commands

# relative modules
from cogs.utilities.functions import current_time
from cogs.utilities import Colours
from config.config import Config

# global attributes
__all__ = ('JoinableTargetAddEmbed',
           'JoinableTargetRemoveEmbed',
           'JoinableTargetForbiddenEmbed',
           'RoleNotFoundEmbed',
           'RoleDuplicateEmbed',
           'RoleNotRemovedEmbed',
           'BotInviteEmbed',
           'BotServerEmbed')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class JoinableTargetAddEmbed(discord.Embed):
    """Embed for Joinable Role added to user.

    Parameters
    ----------

    Returns
    -------
    """
    def __init__(self, user, role_name):
        ctitle = f'Joinable role added'
        cdesc = f'{user.mention} now in **{role_name}** role.'
        ccolour = Colours.CHANGE_U
        super().__init__(
            title=ctitle,
            description=cdesc,
            color=ccolour
        )
        self.set_footer(text=current_time())


class JoinableTargetRemoveEmbed(discord.Embed):
    """Embed for Joinable Role removed from user.

    Parameters
    ----------

    Returns
    -------
    """
    def __init__(self, user, role_name: str):
        ctitle = f'Joinable role removed'
        cdesc = f'{user.mention} left **{role_name}** role.'
        ccolour = Colours.CHANGE_U
        super().__init__(
            title=ctitle,
            description=cdesc,
            color=ccolour
        )
        self.set_footer(text=current_time())


class JoinableTargetForbiddenEmbed(discord.Embed):
    """Embed for Joinable Role unable to be applied to user.

    Parameters
    ----------

    Returns
    -------
    """
    def __init__(self, role_name: str):
        ctitle = f'Role Not Added'
        cdesc = f'**{role_name}** is not self-assignable'
        ccolour = Colours.ERROR
        super().__init__(
            title=ctitle,
            description=cdesc,
            color=ccolour
        )
        self.set_footer(text=current_time())


class RoleNotFoundEmbed(discord.Embed):
    """Embed for Generic Role doesn't exit.

    Parameters
    ----------

    Returns
    -------
    """
    def __init__(self, role_name: str):
        ctitle = f'Role not found'
        cdesc = f'Couldn\'t find role **{role_name}**'
        ccolour = Colours.ERROR
        super().__init__(
            title=ctitle,
            description=cdesc,
            color=ccolour
            )
        self.set_footer(text=current_time())


class RoleDuplicateEmbed(discord.Embed):
    """Embed for Generic Role already in.

    Parameters
    ----------

    Returns
    -------
    """
    def __init__(self, message_user, role_name):
        ctitle = 'Role Not Added'
        cdesc = f'{message_user.mention} already in **{role_name}** role'
        ccolour = Colours.WARNING
        super().__init__(
            title=ctitle,
            description=cdesc,
            color=ccolour
        )
        self.set_footer(text=current_time())


class RoleNotRemovedEmbed(discord.Embed):
    """Embed for Generic Role are not in which can't be removed.

    Parameters
    ----------

    Returns
    -------
    """
    def __init__(self, message_user, role_name):
        ctitle = 'Role Not Removed'
        cdesc = f'{message_user.mention}, you don\'t have the **{role_name}** role'
        ccolour = Colours.WARNING
        super().__init__(
            title=ctitle,
            description=cdesc,
            color=ccolour
        )
        self.set_footer(text=current_time())


class BotInviteEmbed(discord.Embed):
    """Bot invite link.

    Parameters
    ----------

    Returns
    -------
    """

    def __init__(self):
        ccolour = Colours.COMMANDS
        ctitle = f'Invite link'
        cdesc=f'[Click!]({Config.bot_key.value}) to invite ' +\
            f'<@{Config.bot_id.value}> to your server!'
        super().__init__(
            title=ctitle,
            description=cdesc,
            color=ccolour)
        self.set_footer(text=current_time())


class BotServerEmbed(discord.Embed):
    """Bot support server invite.

    Parameters
    ----------

    Returns
    -------
    """
    def __init__(self):
        ccolour = Colours.COMMANDS
        ctitle = f'Invite link'
        cdesc = f'[Click!]({Config.support_server.value}) to join the bot' +\
            f'<@{Config.bot_id.value}>\'s support server!'
        super().__init__(
            title=ctitle,
            description=cdesc,
            color=ccolour)
        self.set_footer(text=current_time())


# end of code

# end of file
