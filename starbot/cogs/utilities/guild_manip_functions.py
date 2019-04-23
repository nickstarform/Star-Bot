"""Generalized Guild Manipulation Hub."""

# internal modules
import datetime
from enum import Enum
import re
from typing import Optional

# external modules
from discord.ext import commands
import discord

# relative modules

# global attributes
__all__ = ('createrole',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


# Basic functions

async def createrole(bot, ctx, create_role_name: str, role_copy_id: str=None, color: bool=False):
    """Create a role.

    Parameters
    ----------
    create_role_name: str
        Name of the new role to create
    role_copy_id: str
        id of the role to copy

    Returns
    -------
    """
    create_role_name = f'#{create_role_name.strip("#")}'
    try:
        if not isinstance(role_copy_id, type(None)):
            role = ctx.guild.get_role(int(role_copy_id))
        else:
            role = ctx.guild.default_role
        perms = role.permissions if role.permissions else None
        colour = discord.Colour(int(f'0x{create_role_name.strip("#")}', 16)) if color else discord.Colour.default()
        hoist = role.hoist if role.hoist else False
        men = role.mentionable if role.mentionable else False
        r = await ctx.guild.create_role(name=create_role_name, permissions=perms, colour=colour,
                                        hoist=hoist, mentionable=men)
    except Exception as e:
        bot.logger.warning(f'Error creating role: {e}')
        return [False, False]
    return [True, r]

# Edit message



# end of code

# end of file
