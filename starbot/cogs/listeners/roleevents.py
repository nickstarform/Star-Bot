"""."""

# internal modules

# external modules
from discord.ext import commands

# relative modules
from cogs.utilities.embed_errors import internalerrorembed
from cogs.utilities.functions import flatten

# global attributes
__all__ = ('RoleEvents',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class RoleEvents(commands.Cog):
    """."""
    def __init__(self, bot):
        """."""
        self.bot = bot
        super().__init__()
        for func in [self.on_voice_state_update, self.on_voice_state_update]:
            bot.add_listener(func)

    # handle if user join role, then check if in joinable_role db

    # handle role remove
    # handle role add


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
