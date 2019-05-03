"""."""

# internal modules

# external modules
from discord.ext import commands

# relative modules
from cogs.utilities.embed_errors import internalerrorembed
from cogs.utilities.functions import flatten

# global attributes
__all__ = ('MetaGuildEvents',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

class MetaGuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        for func in [self.on_guild_join, self.on_guild_remove]:
            bot.add_listener(func)

    async def on_guild_join(self, guild):
        """Auto add guild to db.

        Parameters
        ----------

        Returns
        -------
        """
        if isinstance(guild, type(None)):
            return
        if guild.id in self.blacklist:
            await guild.leave()
            return
        try:
            try:
                config = await self.bot.pg.get_single_guild_settings(guild.id)
            except:
                config = False
            if isinstance(config, bool):
                await self.bot.pg.add_guild(guild.id)
                config = await self.bot.pg.get_single_guild_settings(guild.id)
            self.bot.guild_settings[guild.id] = config
            user = await self.bot.fetch_user(int(self.bot.config.owner_id.value))
            if isinstance(user.dm_channel, type(None)):
                await user.create_dm()
            await user.send(f'Guild {guild.id} has joined: <@{guild.owner.id}> ')
            self.bot.logger.warning(f'Guild joined: {guild.id}')
            return
        except Exception as e:
            user = await self.bot.fetch_user(int(self.bot.config.owner_id.value))
            if isinstance(user.dm_channel, type(None)):
                await user.create_dm()
            await user.send(embed=internalerrorembed(f'Error adding guild to db: {e}'))
            self.bot.logger.warning(f'Error adding guild to db: {e}')
            return

    async def on_guild_remove(self, guild):
        """Auto add guild to db.

        Parameters
        ----------

        Returns
        -------
        """
        if isinstance(guild, type(None)):
            return
        # clear out any giveaways in guild
        giveaways = await self.bot.pg.get_all_giveaways_guild(guild.id, True, self.bot.logger)
        for give in giveaways:
            status = await self.bot.pg.update_giveaway(give, ['status'], [True], self.bot.logger)
            del self.bot.current_giveaways[give]
        del self.bot.guild_settings[guild.id]
        user = await self.bot.fetch_user(int(self.bot.config.owner_id.value))
        if isinstance(user.dm_channel, type(None)):
            await user.create_dm()
        await user.send(f'Guild {guild.id} has removed the bot: <@{guild.owner.id}>')
        self.bot.logger.warning(f'Guild left: {guild.id}')
        return

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
