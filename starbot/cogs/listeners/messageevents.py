"""."""

# internal modules

# external modules
from discord.ext import commands

# relative modules
from cogs.utilities import embed_log as lembed
from cogs.utilities.functions import flatten

# global attributes
__all__ = ('MessageEvents',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class MessageEvents(commands.Cog):
    """."""
    def __init__(self, bot):
        """."""
        self.bot = bot
        super().__init__()
        for func in [self.on_message_edit, self.on_message_delete]:
            bot.add_listener(func)

    async def on_message_edit(self, before, after):
        """If message is edited.

        Parameters
        ----------
        args:
            The exact parameters in keys

        Returns
        -------
        """
        if isinstance(before.guild, type(None)):
            return
        if not self.bot.guild_settings[before.guild.id]['modlog_enabled']:
            return
        try:
            if not before.content.strip() != after.content.strip():
                return
            channels = await self.bot.pg.get_all_modlogs(
                before.guild.id)
            try:
                embeds = lembed.messageeditembed(
                    before.author,
                    before.content,
                    after.content,
                    before.channel.name)
                for channel in channels:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed=embeds)
            except Exception as e:
                self.bot.logger.warning(f'Issue logging message edit: {e}')
                return
        except Exception as e:
            self.bot.logger.warning(f'Issue logging message edit: {e}')
            return

    async def on_message_delete(self, message):
        """If message is dvoice_loggingeleted.

        Parameters
        ----------
        args:
            The exact parameters in keys

        Returns
        -------
        """
        if isinstance(message.guild, type(None)):
            return
        if not self.bot.guild_settings[message.guild.id]['modlog_enabled']:
            return
        if message.author.bot:
            return
        try:
            channels = await self.bot.pg.get_all_modlogs(
            message.guild.id)
            embeds = lembed.messagedeleteembed(
                message.author,
                message.content,
                message.channel.name,
            )
            for channel in channels:
                ch = self.bot.get_channel(channel)
                await ch.send(embed=embeds)
        except Exception as e:
            self.bot.logger.warning(f'Issue logging message edit: {e}')

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
