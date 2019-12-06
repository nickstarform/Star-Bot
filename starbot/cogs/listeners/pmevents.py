"""."""

# internal modules

# external modules
import discord
from discord.ext import commands

# relative modules

# global attributes
__all__ = ('PrivateMessageEvents',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class PrivateMessageEvents(commands.Cog):
    """."""
    def __init__(self, bot):
        """."""
        self.bot = bot
        super().__init__()
        for func in [self.on_message]:
            bot.add_listener(func)

    async def on_message(self, message):
        if not isinstance(message.channel, discord.DMChannel):
            return
        # handle help calls
        # handle prefix calls
        # handle reports

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
