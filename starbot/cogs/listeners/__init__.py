"""Main Listeners Hub."""

# internal modules

# external modules

# relative modules
from cogs.listeners.metaguildevents import MetaGuildEvents
from cogs.listeners.messageevents import MessageEvents
from cogs.listeners.guildchanges import GuildChanges

# global attributes
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(MetaGuildEvents(bot))
    print('Loaded MetaGuild Events')
    bot.add_cog(MessageEvents(bot))
    print('Loaded Message Events')
    bot.add_cog(GuildChanges(bot))
    print('Loaded GuildChanges Events')
    """
    bot.add_cog(PM(bot))
    print('Loaded PM Events')
    bot.add_cog(PM(bot))
    print('Loaded PM Events')
    """

# end of code

# end of file
