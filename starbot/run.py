"""Actually runs the code."""

# import internal modules
import sys
import os

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
                      'cogs.owner',
                      'cogs.general',
                      'cogs.moderation',
                      'cogs.administration',
                      'cogs.blacklist',
                      'cogs.logging',
                      'cogs.info',
                      'cogs.listeners']

def run():
    """Load cogs and build self.bot.

    Parameters
    ----------
    ctx: :func: commands.Context
        the context command object

    Returns
    -------
    """
    loop = get_event_loop()
    try:
        bot = loop.run_until_complete(Starbot.get_instance())
    except Exception as e:
        print('Error on startup:', str(e))
        return loop.run_until_complete(shutdown(bot, reason=e))
    # bot.add_cog(Extension(bot))
    for cog in initial_extensions:
        bot.load_extension(cog)
        bot._loaded_extensions.append(cog)

    try:
        loop.run_until_complete(bot.run(Config['token'].value, reconnect=True))
    except KeyboardInterrupt as e:
        return loop.run_until_complete(shutdown(bot, reason=e))

async def shutdown(bot, *, reason=None):
    """Somewhat clean shutdown with basic debug info."""
    await bot.logout()

    print(f'\n\nShutting down due to {type(reason).__name__}...\n{"="*30}\n')
    print(f'{datetime.datetime.utcnow()} || UTC\n\nPython: {sys.version}\nPlatform: {sys.platform}/{os.name}\n'
          f'Discord: {discord.__version__}\n\n{"="*30}\n')

    await asyncio.sleep(1)

    if isinstance(reason, KeyboardInterrupt):
        sys.exit(1)  # Systemd will think it failed and restart our service cleanly.
    sys.exit(0)

if __name__ == '__main__':
    run()

# end of code

# end of file
