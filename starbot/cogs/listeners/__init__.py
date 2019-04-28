"""Main Listeners Hub."""

# internal modules

# external modules

# relative modules
from cogs.listeners.events import Events

# global attributes
__all__ = ('Events',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(Events(bot))
    print('Loaded General Events')

# end of code

# end of file
