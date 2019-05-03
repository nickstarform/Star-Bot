"""."""

# internal modules

# external modules
from discord.ext import commands

# relative modules
from cogs.utilities.embed_errors import internalerrorembed
from cogs.utilities.functions import flatten

# global attributes
__all__ = ('MemberDbBotEvents',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class MemberDbBotEvents(commands.Cog):
    """."""
    def __init__(self, bot):
        """."""
        self.bot = bot
        super().__init__()
        for func in [self.on_member_join, self.on_member_remove]:
            bot.add_listener(func)

    async def on_member_join(self, member):
        """New User Joins.

        Parameters
        ----------
        before
            Member prior to change
        after
            Member after to change

        Returns
        -------
        discord.Embed
            embedded object to send message
        """
        try:
            roles = await self.bot.pg.get_all_autoroles(member.guild.id)
            roles = flatten([member.guild.get_role(int(role)) for role in roles])
            await member.edit(roles=roles)
        except Exception as e:
            print(f'Exception join {e}')
            return

    async def on_member_remove(self, member):
        """User leaves.

        Parameters
        ----------
        before
            Member prior to change
        after
            Member after to change

        Returns
        -------
        discord.Embed
            embedded object to send message
        """
        pass

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
