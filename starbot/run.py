"""Actually runs the code."""

# import internal modules
import sys

# import external modules
import traceback
import discord
from discord.ext import commands
from asyncio import get_event_loop

# import relative modules
from config import Config
from bot import Starbot
from cogs import (utilities, )
from cogs.utilities import permissions
from cogs.utilities.embed_dialog import respond



initial_extensions = ['cogs.fun',
                      'cogs.owner',]

def run():
    """Load cogs and build bot.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object

    Returns
    -------
    """
    loop = get_event_loop()
    bot = loop.run_until_complete(Starbot.get_instance())
    for cog in initial_extensions:
        bot.load_extension(f'{cog}')
    bot.add_cog(Loader(bot))
    bot.run(Config['token'].value)

    @bot.event
    async def on_message(self, ctx):
        if not await permissions.is_blacklisted(self, ctx):
            return
        await bot.process_commands(ctx)

class Loader(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    """
    CODE CONFIGURATION
    """
    @commands.command(name='listcogs', hidden=True)
    @permissions.is_master()
    async def _list(self, ctx):
        """List.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

        Returns
        -------
        """
        await ctx.send(f'```py\n{initial_extensions}\n```')
        pass

    @commands.command(name='load', hidden=True)
    @permissions.is_master()
    async def _load(self, ctx, *, module):
        """Loads a module.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

        Returns
        -------
        """
        index = initial_extensions.index(module)
        if not isinstance(index, int):
            return
        try:
            self.bot.load_extension(f'{initial_extensions[index]}')
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await respond(ctx, True)

    @commands.command(name='unload', hidden=True)
    @permissions.is_master()
    async def _unload(self, ctx, *, module):
        """Unload a module.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

        Returns
        -------
        """
        index = initial_extensions.index(module)
        if not isinstance(index, int):
            return
        try:
            self.bot.unload_extension(f'{initial_extensions[index]}')
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await respond(ctx, True)

    @commands.command(name='reload', hidden=True)
    @permissions.is_master()
    async def _reload(self, ctx, *, module):
        """Reloads a module.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

        Returns
        -------
        """
        index = initial_extensions.index(module)
        if not isinstance(index, int):
            return
        try:
            self.bot.reload_extension(f'{initial_extensions[index]}')
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await respond(ctx, True)

if __name__ == '__main__':
    run()

# end of code

# end of file
