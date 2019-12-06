"""."""

# internal modules

# external modules
from discord.ext import commands

# relative modules
from cogs.utilities.embed_errors import internalerrorembed
from cogs.utilities.functions import flatten

# global attributes
__all__ = ('UserEvents',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class UserEvents(commands.Cog):
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
        # roles
        try:
            roles = await self.bot.pg.get_all_autoroles(member.guild.id)
            if not isinstance(roles, type(None)):
                roles = flatten([member.guild.get_role(int(role)) for role in roles])
                await member.edit(roles=roles)
        except Exception as e:
            print(f'Exception join {e}')

        if not self.bot.guild_settings[member.guild.id]['logging_enabled']:
            return
        channels = await self.bot.pg.get_all_logger_channels(
            member.guild.id)
        for channel in channels:
            try:
                ch = self.bot.get_channel(int(channel))
                print(ch)
                await ch.send(embed=lembed.joinembed(member))
            except:
                print('exception join1')
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
        pass

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
        channels = None
        if before.roles != after.roles:
            channels = await self.bot.pg.get_all_modlogs(before.guild.id)
            if isinstance(channels, type(None)):
                return
            roles_added = list(set(after.roles) - set(before.roles))
            roles_removed = list(set(before.roles) - set(after.roles))
            for channel in channels:
                try:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed=lembed.roleeditembed(before, roles_added, roles_removed))
                except:
                    continue
        if before.display_name != after.display_name:
            if isinstance(channels, type(None)):
                channels = await self.bot.pg.get_all_modlogs(before.guild.id)
                if isinstance(channels, type(None)):
                    return
            for channel in channels:
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

        if not self.bot.guild_settings[guild.id]['modlog_enabled']:
            return
        if before.username != after.username:
            channels = await self.bot.pg.get_all_modlogs(guild_id)
            if isinstance(channels, type(None)):
                return
            for channel in channels:
                try:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed=lembed.usernameupdateembed(after, before.username, after.username))
                except:
                    continue

    async def on_member_ban(self, guild, user):
        if not self.bot.guild_settings[guild.id]['modlog_enabled']:
            return
        channels = await self.bot.pg.get_all_modlogs(guild.id)
        for channel in channels:
            try:
                ch = self.bot.get_channel(channel)
                await ch.send(embed=lembed.banembed(user, self.bot.user, reason))
            except:
                continue

    async def on_member_unban(self, guild, user):
        if not self.bot.guild_settings[guild.id]['modlog_enabled']:
            return
        channels = await self.bot.pg.get_all_modlogs(guild.id)
        for channel in channels:
            try:
                ch = self.bot.get_channel(channel)
                await ch.send(embed=lembed.unbanembed(user, self.bot.user, reason))
            except:
                continue
if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
