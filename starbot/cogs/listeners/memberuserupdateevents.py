"""."""

# internal modules

# external modules
from discord.ext import commands

# relative modules
from cogs.utilities.embed_errors import internalerrorembed
from cogs.utilities import embed_log as lembed
from cogs.utilities.functions import flatten

# global attributes
__all__ = ('MemberUserUpdateEvents',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class MemberUserUpdateEvents(commands.Cog):
    """."""
    def __init__(self, bot):
        """."""
        self.bot = bot
        super().__init__()
        for func in [self.on_member_update, self.on_user_update,
                     self.on_member_join, self.on_member_remove]:
            bot.add_listener(func)

    async def on_member_update(self, before, after):
        """When member gets updated.

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
        if isinstance(before.guild, type(None)):
            return
        if not self.bot.guild_settings[before.guild.id]['modlog_enabled']:
            return
        channels = await self.bot.pg.get_all_modlogs(before.guild.id)
        if before.roles != after.roles:
            roles_added = list(set(after.roles) - set(before.roles))
            roles_removed = list(set(before.roles) - set(after.roles))

            for channel in channels:
                try:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed=lembed.roleeditembed(before, roles_added, roles_removed))
                except:
                    continue
        if before.display_name != after.display_name:
            for channel in extended_channels:
                try:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed=lembed.nicknameupdateembed(after, before.display_name, after.display_name))
                except:
                    continue

    async def on_user_update(self, before, after):
        """When member gets updated.

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

        if isinstance(before.guild, type(None)):
            return
        user_mutuals = []
        for guild in self.bot.guilds:
            if not self.bot.guild_settings[guild.id]['modlog_enabled']:
                continue
            if before in guild.members:
                user_mutuals.append(guild.id)
        extended_channels = []
        for guild_id in user_mutuals:
            extended_channels.extend(
                await self.bot.pg.get_all_modlogs(guild_id))
        if before.username != after.username:
            for channel in extended_channels:
                try:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed=lembed.usernameupdateembed(after, before.username, after.username))
                except:
                    continue

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
        if not self.bot.guild_settings[member.guild.id]['logging_enabled']:
            return
        channels = await self.bot.pg.get_all_logger_channels(
            member.guild.id)
        print(channels)
        for channel in channels:
            try:
                ch = self.bot.get_channel(int(channel))
                print(ch)
                await ch.send(embed=lembed.joinembed(member))
            except:
                print('eception join1')
                continue

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
        if not self.bot.guild_settings[member.guild.id]['logging_enabled']:
            return
        channels = await self.bot.pg.get_all_logger_channels(
            member.guild.id)
        for channel in channels:
            try:
                ch = self.bot.get_channel(int(channel))
                await ch.send(embed=lembed.leaveembed(member))
            except:
                continue

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
