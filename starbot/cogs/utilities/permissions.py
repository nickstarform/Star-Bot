"""General Permissions Handler."""

# internal modules

# external modules
from discord.ext import commands

# relative modules
from config import Config

# global attributes
__all__ = ('has_permissions',
           'has_guild_permissions',
           'is_manager',
           'is_admin',
           'is_master',
           'manager_or_permissions',
           'admin_or_permissions',
           'is_in_guilds',
           'is_blacklisted',
           'is_cmd_blacklisted')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


async def check_permissions(ctx, perms, *, check=all):
    """Generic perm checker.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    perms: dict
        permissionsof user to check against
    check:
        is the check type

    Returns
    -------
    bool
        if has perms true false
    """
    if ctx.guild is None:
        return False

    is_owner = await ctx.bot.is_owner(ctx.author)
    if (str(Config.owner_id.value) == str(ctx.author.id)) or\
       (str(Config.devel_id.value) == str(ctx.author.id)) or is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) ==
                 value for name, value in perms.items())


def has_permissions(*, check=all, **perms):
    """Decorator for generic check perms.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    perms: dict
        permissionsof user to check against
    check:
        is the check type

    Returns
    -------
    bool
        if has perms true false
    """
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)


async def check_guild_permissions(ctx, perms, *, check=all):
    """Generic check guild perms.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    perms: dict
        permissionsof user to check against
    check:
        is the check type

    Returns
    -------
    bool
        if has perms true false
    """
    if ctx.guild is None:
        return False

    is_owner = await ctx.bot.is_owner(ctx.author)
    if (str(Config.owner_id.value) == str(ctx.author.id)) or\
       (str(Config.devel_id.value) == str(ctx.author.id)) or is_owner:
        return True

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) ==
                 value for name, value in perms.items())


def has_guild_permissions(*, check=all, **perms):
    """Decorator for generic guild check perms.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    perms: dict
        permissionsof user to check against
    check:
        is the check type

    Returns
    -------
    bool
        if has perms true false
    """
    async def pred(ctx):
        return await check_guild_permissions(ctx, perms, check=check)
    return commands.check(pred)

# These do not take channel overrides into account


def is_manager():
    """Check if user is manager.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object

    Returns
    -------
    bool
        if has perms true false
    """
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'manage_guild': True})
    return commands.check(pred)


def is_admin():
    """Check if user is admin..

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object

    Returns
    -------
    bool
        if has perms true false
    """
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'administrator': True})
    return commands.check(pred)


def is_master():
    """Check if user is admin..

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object

    Returns
    -------
    bool
        if has perms true false
    """
    async def pred(ctx):
        return True if str(ctx.author.id) == str(Config.owner_id.value) or\
            str(ctx.author.id) == str(Config.devel_id.value) else False
    return commands.check(pred)


def manager_or_permissions(**perms):
    """Check if user is manager/has perms.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    perms: dict
        permissionsof user to check against

    Returns
    -------
    bool
        if has perms true false
    """
    perms['manage_guild'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)


def admin_or_permissions(**perms):
    """Check if user is admin/has perms.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object
    perms: dict
        permissionsof user to check against

    Returns
    -------
    bool
        if has perms true false
    """
    perms['administrator'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)

"""
GUILD CHECK
"""


def is_in_guilds(*guild_ids):
    """Check if in guilds.

    Parameters
    ----------

    Returns
    -------
    bool
        if in true false
    """
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids
    return commands.check(predicate)

"""
BLACKLIST
"""


async def is_cmd_blacklisted(bot, guild_id: str, cmd: str):
    """Check if in guilds.

    Parameters
    ----------

    Returns
    -------
    bool
        if in true false
    """
    if await bot.pg.is_disallowed_global(cmd):
        return True
    elif await bot.pg.is_disallowed(guild_id, cmd):
        return True
    else:
        return False


async def is_blacklisted(bot, message):
    """Check if in guilds.

    Parameters
    ----------
    self: botinstance
        Description of arg1
    message:
        The discord message object

    Returns
    -------
    bool
        if in true false
    """
    if await bot.pg.is_blacklist_guild_global(message.guild.id):
        return True
    if await bot.pg.is_blacklist_user_global(message.author.id):
        return True
    if await bot.pg.is_blacklist_channel(message.guild.id, message.channel.id):
        return True
    if await bot.pg.is_blacklist_user(message.guild.id, message.author.id):
        return True
    return False

if __name__ == "__main__":
    """Directly Called."""
    print('Testing module')
    print('Test Passed')

# end of code

# end of file
