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

async def createrole(bot, ctx, create_role_name: str, role_copy_id: str=None):
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
    try:
        if not isinstance(role_copy_id, type(None)):
            role = role_copy_id
        else:
            role = ctx.guild.default_role     
        perms = role.permissions if role.permissions else None
        colour = role.colour if role.permissions else discord.Colour.default()
        hoist = role.hoist if role.hoist else False
        pos = role.position if role.position else 0
        men = role.mentionable if role.mentionable else False
        r = await ctx.guild.create_role(name=create_role_name, )
    except Exception as e:
        bot.logger(f'Error creating role: {e}')
        return [False, False]
    return [True, r]




# end of code

# end of file
