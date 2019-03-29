"""General Embed Constructor Hub."""

# internal modules

# external modules
import discord

# relative modules
from .colours import Colours
from .functions import current_time
from config import Config

# global attributes
__all__ = ('generic_embed',
           'joinabletargetaddembed',
           'joinabletargetremoveembed',
           'joinabletargetforbiddenembed',
           'rolenotfoundembed',
           'roleduplicateembed',
           'rolenotremovedembed',
           'botinviteembed',
           'botserverembed')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def generic_embed(title: str, desc: str, fields: list,
                  footer: str, colours: Colours=Colours.COMMANDS):
    """Generic embed builder.

    The main constraint is len title + desc < 500. Use the generic
    message sender if this isn't the case. Otherwise this tries to
    split up fields intelligently.

    Parameters
    ----------
    title: str
        title of the embed
    desc: str
        the desc to display
    fields: list
        a 2d list of field populators [[field_name, field_value, inline],[]]
    footer: str
        footer to add
    colours: :func: Colours
        Enum object of colours

    Returns
    -------
    :func: discord.Embed
        The discord embed object
    """
    if (len(title) + len(desc)) > 500:
        desc = desc[:500-len(title)]
    total_embeds = (sum([len(''.join(x)) for x in fields]) +
                    len(title) + len(footer) + len(desc)) // 500 + 1
    if len(total_embeds) > 1:
        embeds = [discord.Embed(title=title + f'(Page{x+1}/{total_embeds})',
                                type='rich',
                                color=colours.value)
                  for x in range(total_embeds)]
        tmplen = 0
        tmpi = 0
        for i in range(total_embeds):
            ctitle = title.replace('X', i + 1)
            embed = discord.Embed(title=ctitle, type='rich',
                                  color=colours.value)
            if (i == 0) and (len(message) > 0):
                embed.description = message
            if len(footer) > 0:
                embed.set_footer(text=footer)
            if len(fields) > 0:
                tmplen += len(''.join(fields[tmpi]))
                while ((tmplen + len(ctitle) + len(footer)) < 500) and\
                        (tmpi < (len(fields) - 1)):
                    tmplen += len(''.join(fields[tmpi]))
                    field = fields[tmpi]
                    embed.add_field(name=field[0],
                                    value=field[1])
                    tmpi += 1
            embeds.append(embed)
    else:
        embeds = []
        embed = discord.Embed(title=title, type='rich', color=colours.value)
        if len(message) > 0:
            embed.description = message
        if len(footer) > 0:
            embed.set_footer(text=footer)
        if len(fields) > 0:
            for field in fields:
                embed.add_field(name=field[0],
                                value=field[1])
        embeds.append(embed)
    return embeds


def joinabletargetaddembed(user: discord.User, role_name: str):
    """Embed for Joinable Role added to user.

    Parameters
    ----------
    user: discord.User
        user that applied the role
    role_name: str
        name of the role applied

    Returns
    -------
    discord.Embed
        embedded object to send message
    """
    ctitle = f'Joinable role added'
    cdesc = f'{user.mention} now in **{role_name}** role.'
    ccolour = Colours.CHANGE_U
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]



def joinabletargetremoveembed(user: discord.User, role_name: str):
    """Embed for Joinable Role removed from user.

    Parameters
    ----------
    user: discord.User
        user that applied the role
    role_name: str
        name of the role applied

    Returns
    -------
    discord.Embed
        embedded object to send message
    """
    ctitle = f'Joinable role removed'
    cdesc = f'{user.mention} left **{role_name}** role.'
    ccolour = Colours.CHANGE_U
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def joinabletargetforbiddenembed(role_name: str):
    """Embed for Joinable Role unable to be applied to user.

    Parameters
    ----------
    role_name: str
        name of the role applied

    Returns
    -------
    discord.Embed
        embedded object to send message
    """
    ctitle = f'Role Not Added'
    cdesc = f'**{role_name}** is not self-assignable'
    ccolour = Colours.ERROR
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def rolenotfoundembed(role_name: str):
    """Embed for Generic Role doesn't exit.

    Parameters
    ----------
    role_name: str
        name of the role applied

    Returns
    -------
    """
    ctitle = f'Role not found'
    cdesc = f'Couldn\'t find role **{role_name}**'
    ccolour = Colours.ERROR
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def roleduplicateembed(user: discord.User, role_name: str):
    """Embed for Generic Role already in.

    Parameters
    ----------
    user: discord.User
        user that applied the command
    role_name: str
        name of the role attempted

    Returns
    -------
    discord.Embed
        embedded object to send message
    """
    ctitle = 'Role Not Added'
    cdesc = f'{user.mention} already in **{role_name}** role'
    ccolour = Colours.WARNING
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def rolenotremovedembed(user: discord.User, role_name: str):
    """Embed for Generic Role are not in which can't be removed.

    Parameters
    ----------
    user: discord.User
        user that applied the command
    role_name: str
        name of the role attempted

    Returns
    -------
    discord.Embed
        embedded object to send message
    """
    ctitle = 'Role Not Removed'
    cdesc = f'{user.mention}, you don\'t have the **{role_name}** role'
    ccolour = Colours.WARNING
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def botinviteembed():
    """Bot invite link.

    Parameters
    ----------

    Returns
    -------
    discord.Embed
        embedded object to send message
    """

    ccolour = Colours.COMMANDS
    ctitle = f'Invite link'
    cdesc = f'[Click!]({Config.bot_key.value}) to invite ' +\
        f'<@{Config.bot_id.value}> to your server!'
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]


def botserverembed():
    """Bot support server invite.

    Parameters
    ----------

    Returns
    -------
    discord.Embed
        embedded object to send message
    """
    ccolour = Colours.COMMANDS
    ctitle = f'Invite link'
    cdesc = f'[Click!]({Config.support_server.value}) to join the bot' +\
        f'<@{Config.bot_id.value}>\'s support server!'
    return generic_embed(ctitle, cdesc, [], current_time(), ccolour)[0]

# end of code

# end of file
