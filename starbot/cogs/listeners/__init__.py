"""Main Listeners Hub."""

# internal modules

# external modules

# relative modules
from cogs.listeners.metaguildevents import MetaGuildEvents
from cogs.listeners.messageevents import MessageEvents
from cogs.listeners.userevents import UserEvents
from cogs.listeners.pmevents import PrivateMessageEvents
from cogs.listeners.reactevents import ReactEvents
from cogs.listeners.channelevents import ChannelEvents

# global attributes
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

_load = (MetaGuildEvents, MessageEvents, UserEvents,
         PrivateMessageEvents, ReactEvents, ChannelEvents)


def setup(bot):
    for mod in _load:
        bot.add_cog(mod(bot))
        print(f'Loaded {mod.__name__}')

# end of code

# end of file
