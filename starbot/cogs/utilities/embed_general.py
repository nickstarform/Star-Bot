"""General Embed Constructor Hub."""

# internal modules
import datetime

# external modules
import discord

# relative modules
from .colours import Colours
from .functions import current_time, chunks, time_conv
from config import Config

# global attributes
__all__ = ('generic_embed',
           'joinabletargetaddembed',
           'joinabletargetremoveembed',
           'joinabletargetforbiddenembed',
           'rolenotfoundembed',
           'roleduplicateembed',
           'rolenotremovedembed',
           'MAX_LEN')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

MAX_DESC_LEN = 2000
MAX_FIELD_LEN = 1000
MAX_LEN = 6000


def generic_embed(title: str, desc: str, fields: list,
                  footer: str=None, colours: Colours=Colours.COMMANDS, force_single: bool=False, **kwargs):
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
    if not footer:
        footer = current_time()
    if len(fields) > 0:
        ret = []
        for fi, f in enumerate(fields):
            f = list(map(str, f))
            if (f[1] == '[]') or (f[1] == ''):
                f[1] = 'NONE SET'
            if len(f[1]) > MAX_FIELD_LEN:
                n = []
                i = 1
                for x in chunks(f[1], MAX_FIELD_LEN - 1):
                    n.append([f[0] + f'({1})', x])
                    i += 1
                del fields[fi]
                fields += n
            ret.append(f)
        fields = ret
    print(title, desc, fields, footer)
    if (len(title) + len(desc)) > MAX_DESC_LEN:
        desc = desc[:MAX_DESC_LEN - len(title)]
    total_embeds = (sum([len(''.join(x)) for x in fields]) +
                    len(title) + len(footer) + len(desc)) // MAX_FIELD_LEN + 1
    print(total_embeds)
    print(sum([len(''.join(x)) for x in fields]) + len(title) + len(footer) + len(desc))
    url = kwargs['url'] if 'url' in kwargs.keys() else ''
    if total_embeds > 1:
        embeds = []
        tmpi = 0
        title += f' (PageX/{total_embeds})'
        for i in range(total_embeds):
            tmplen = 0
            ctitle = title.replace('X', str(i + 1))
            embed = discord.Embed(title=ctitle, type='rich',
                                  color=colours.value, desc='', url=url)
            if 'image' in kwargs.keys():
                if kwargs['image'] is not None and kwargs['image'].lower() != 'none':
                    embed.set_image(url=kwargs['image'])
            if 'thumbnail' in kwargs.keys():
                if kwargs['thumbnail'] is not None and kwargs['thumbnail'].lower() != 'none':
                    embed.set_thumbnail(url=kwargs['thumbnail'])
            if (i == 0) and (len(desc) > 0):
                embed.description = desc
            if len(footer) > 0:
                embed.set_footer(text=footer)
            if len(fields) > 0:
                tmplen += len(''.join(fields[tmpi]))
                print(tmplen + len(ctitle) + len(footer))
                while ((tmplen + len(ctitle) + len(footer)) < MAX_LEN) and\
                        (tmpi < (len(fields) - 1)):
                    tmplen += len(''.join(fields[tmpi]))
                    field = fields[tmpi]
                    embed.add_field(name=field[0],
                                    value=field[1])
                    tmpi += 1
            embeds.append(embed)
    else:
        embeds = []
        embed = discord.Embed(title=title, type='rich', desc='', color=colours.value, url = url)
        if 'image' in kwargs.keys():
            if (kwargs['image'] is not None) and kwargs['image'].lower() != 'none':
                embed.set_image(url=kwargs['image'])
        if 'thumbnail' in kwargs.keys():
            if kwargs['thumbnail'] is not None and kwargs['thumbnail'].lower() != 'none':
                embed.set_thumbnail(url=kwargs['thumbnail'])
        if len(desc) > 0:
            embed.description = desc
        if len(footer) > 0:
            embed.set_footer(text=footer)
        if len(fields) > 0:
            for field in fields:
                embed.add_field(name=field[0],
                                value=field[1])
        embeds.append(embed)
    for x in embeds:
        print(x.to_dict())
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

# end of code

# end of file
