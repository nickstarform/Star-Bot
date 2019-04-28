"""."""

# internal modules

# external modules
import discord
from discord.ext import commands

# relative modules
from cogs.utilities import (Colours, permissions)
from cogs.utilities.functions import (current_time, parse, time_conv, get_channel, flatten)
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.message_general import generic_message
from cogs.utilities.embed_dialog import respond
from cogs.utilities.embed_errors import internalerrorembed

# global attributes
__all__ = ('Logger',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(Logger(bot))
    print('Loaded Logger')


class Logger(commands.Cog):
    """Logger commands."""

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    """
    WELCOME LOG
    """
    @commands.group(name='welcomechannel')
    @commands.guild_only()
    @permissions.is_admin()
    async def _welcomechannel(self, ctx):
        """Welcome channel general commands.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand:
            return
        try:
            channels = await self.bot.pg.get_all_welcome_channels(ctx.guild.id, self.bot.logger)
            channels = [f'<#{channel}>' for channel in channels]
            if len(channels) > 0:
                embeds = generic_embed(title='Welcome channels', desc=f', '.join(channels), fields=[], footer=current_time())
            else:
                embeds = generic_embed(title='Welcome channels', desc='No welcome channels set', fields=[], footer=current_time())
            for embed in embeds:
                try:
                    await ctx.send(embed=embed)
                except Exception as e:
                    await ctx.send(embed=internalerrorembed(f'Sending message welcome channels: {e}'), delete_after=15)
                    self.bot.logger.warning(f'Error Sending welcome channels: {e}')
                    await respond(ctx, False)
                    continue
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Error retrieving welcome channels: {e}'), delete_after=15)
            self.bot.logger.warning(f'Error retrieving welcome channels: {e}')
            await respond(ctx, False)
            return

    @_welcomechannel.command(name='remove', aliases=['rm', '-'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _wcdel(self, ctx, channels: str=None):
        """Welcome channel delete.

        Delete either the specified channel
        or default to current channel

        Parameters
        ----------
        channel: Optional[str]
            Optional parameter for the channel(s) to remove
            Comma separated if more than one

        Returns
        -------
        """
        todel = []
        if channels is None:
            todel.append(ctx.message.channel)
        else:
            for channel in channels.split(','):
                todel.append(get_channel(ctx, channel))
        todel = flatten(todel)
        try:
            for target in todel:
                success = await self.bot.pg.rem_welcome_channel(
                    ctx.guild.id,
                    target.id,
                    self.bot.logger)
                await generic_message(ctx, [ctx.channel], f'Welcome channel has been deleted {target.mention}.', delete=15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong removing welcome channels.')
            await ctx.send(embed=local_embed, delete_after=10)
            await respond(ctx, False)
            return
        pass

    @_welcomechannel.command(name='add', aliases=['a', '+'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _wcadd(self, ctx, channels: str=None):
        """Welcome channel add.

        Add either the specified channel
        or default to current channel

        Parameters
        ----------
        channel: Optional[str]
            Optional parameter for the channel to add
            Comma separated if more than one

        Returns
        -------
        """
        toadd = []
        if channels is None:
            toadd.append(ctx.message.channel)
        else:
            for channel in channels.split(','):
                toadd.append(get_channel(ctx, channel))
        toadd = flatten(toadd)
        try:
            for target in toadd:
                success = await self.bot.pg.add_welcome_channel(
                    ctx.guild.id,
                    target.id,
                    self.bot.logger)
                await generic_message(ctx, [ctx.channel], f'Welcome channel has been added {target.mention}.', delete=15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong adding welcome channels.')
            await ctx.send(embed=local_embed, delete_after=10)
            await respond(ctx, False)
            return

    """
    GENERAL LOGGING
    """
    @commands.group(name='logging', aliases=['genlog'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _genlog(self, ctx):
        """Logging channel general commands.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand:
            return
        try:
            channels = await self.bot.pg.get_all_logger_channels(ctx.guild.id, self.bot.logger)
            channels = [f'<#{channel}>' for channel in channels]
            if len(channels) > 0:
                embeds = generic_embed(title='General logging channels', desc=f', '.join(channels), fields=[], footer=current_time())
            else:
                embeds = generic_embed(title='General Logging channels', desc='No channels set', fields=[], footer=current_time())
            for embed in embeds:
                try:
                    await ctx.send(embed=embed)
                except Exception as e:
                    await ctx.send(embed=internalerrorembed(f'Sending message logging channels: {e}'), delete_after=15)
                    self.bot.logger.warning(f'Error Sending logging channels: {e}')
                    await respond(ctx, False)
                    continue
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Error retrieving logging channels: {e}'), delete_after=15)
            self.bot.logger.warning(f'Error retrieving logging channels: {e}')
            await respond(ctx, False)
            return

    @_genlog.command(name='remove', aliases=['rm', '-'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _genlogdel(self, ctx, channels: str=None):
        """Logging channel delete.

        Delete either the specified channel
        or default to current channel

        Parameters
        ----------
        channel: Optional[str]
            Optional parameter for the channel to remove

        Returns
        -------
        """
        todel = []
        if channels is None:
            todel.append(ctx.message.channel)
        else:
            for channel in channels.split(','):
                todel.append(get_channel(ctx, channel))
        todel = flatten(todel)
        try:
            for target in todel:
                success = await self.bot.pg.rem_logger_channel(
                    ctx.guild.id,
                    target.id,
                    self.bot.logger)
                await generic_message(ctx, [ctx.channel], f'Logging channel has been deleted {target.mention}.', delete=15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Logging went wrong removing logging channels.')
            await ctx.send(embed=local_embed, delete_after=10)
            await respond(ctx, False)
            return
        pass

    @_genlog.command(name='add', aliases=['a', '+'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _genlogadd(self, ctx, channel: str=None):
        """Logging channel add.

        Add either the specified channel
        or default to current channel

        Parameters
        ----------
        channel: Optional[str]
            Optional parameter for the channel to add

        Returns
        -------
        """
        toadd = []
        if channels is None:
            toadd.append(ctx.message.channel)
        else:
            for channel in channels.split(','):
                toadd.append(get_channel(ctx, channel))
        toadd = flatten(toadd)
        try:
            for target in toadd:
                success = await self.bot.pg.add_logger_channel(
                    ctx.guild.id,
                    target.id,
                    self.bot.logger)
                await generic_message(ctx, [ctx.channel], f'Logging channel has been added {target.mention}.', delete=15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong adding logging channels.')
            await ctx.send(embed=local_embed, delete_after=10)
            await respond(ctx, False)
            return

    """
    MODLOG
    """
    @commands.group(name='modlog', aliases=['modlogging'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _modlog(self, ctx):
        """Mod only logging channel general commands.

        This channel carries more info than standard logging:
        message edit, role changes, etc
        This is stored under modlog since the bot will notify
        of any changes it sees in any channel

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand:
            return
        try:
            channels = await self.bot.pg.get_all_modlogs(ctx.guild.id, self.bot.logger)
            channels = [f'<#{channel}>' for channel in channels]
            if len(channels) > 0:
                embeds = generic_embed(title='Moderation logging channels', desc=f', '.join(channels), fields=[], footer=current_time())
            else:
                embeds = generic_embed(title='Moderation Logging channels', desc='No channels set', fields=[], footer=current_time())
            for embed in embeds:
                try:
                    await ctx.send(embed=embed)
                except Exception as e:
                    await ctx.send(embed=internalerrorembed(f'Sending message Moderation channels: {e}'), delete_after=15)
                    self.bot.logger.warning(f'Error Sending Moderation channels: {e}')
                    await respond(ctx, False)
                    continue
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Error retrieving Moderation channels: {e}'), delete_after=15)
            self.bot.logger.warning(f'Error retrieving Moderation channels: {e}')
            await respond(ctx, False)
            return

    @_modlog.command(name='remove', aliases=['rm', '-'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _modlogdel(self, ctx, channels: str=None):
        """Logging channel delete.

        Delete either the specified channel
        or default to current channel

        Parameters
        ----------
        channel: Optional[str]
            Optional parameter for the channel to remove

        Returns
        -------
        """
        todel = []
        if channels is None:
            todel.append(ctx.message.channel)
        else:
            for channel in channels.split(','):
                todel.append(get_channel(ctx, channel))
        todel = flatten(todel)
        try:
            for target in todel:
                success = await self.bot.pg.rem_modlog(
                    ctx.guild.id,
                    target.id,
                    self.bot.logger)
                await generic_message(ctx, [ctx.channel], f'Moderation channel has been deleted {target.mention}.', delete=15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Logging went wrong removing Moderation channels.')
            await ctx.send(embed=local_embed, delete_after=10)
            await respond(ctx, False)
            return
        pass

    @_modlog.command(name='add', aliases=['a', '+'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _modlogadd(self, ctx, channel: str=None):
        """Logging channel add.

        Add either the specified channel
        or default to current channel

        Parameters
        ----------
        channel: Optional[str]
            Optional parameter for the channel to add

        Returns
        -------
        """
        toadd = []
        if channels is None:
            toadd.append(ctx.message.channel)
        else:
            for channel in channels.split(','):
                toadd.append(get_channel(ctx, channel))
        toadd = flatten(toadd)
        try:
            for target in toadd:
                success = await self.bot.pg.add_modlog(
                    ctx.guild.id,
                    target.id,
                    self.bot.logger)
                await generic_message(ctx, [ctx.channel], f'Moderation channel has been added {target.mention}.', delete=15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong adding Moderation channels.')
            await ctx.send(embed=local_embed, delete_after=10)
            await respond(ctx, False)
            return

    """
    VOICELOG
    """
    @commands.group(name='voicelogging', aliases=['vclogs', 'prescence_logging'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _vclog(self, ctx):
        """Voice Logging of voice state changes.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand:
            return
        try:
            channels = await self.bot.pg.get_all_voice_channels(ctx.guild.id, self.bot.logger)
            channels = [f'<#{channel}>' for channel in channels]
            if len(channels) > 0:
                embeds = generic_embed(title='Voice logging channels', desc=f', '.join(channels), fields=[], footer=current_time())
            else:
                embeds = generic_embed(title='Voice Logging channels', desc='No channels set', fields=[], footer=current_time())
            for embed in embeds:
                try:
                    await ctx.send(embed=embed)
                except Exception as e:
                    await ctx.send(embed=internalerrorembed(f'Sending message Voice channels: {e}'), delete_after=15)
                    self.bot.logger.warning(f'Error Sending Voice channels: {e}')
                    await respond(ctx, False)
                    continue
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Error retrieving Voice channels: {e}'), delete_after=15)
            self.bot.logger.warning(f'Error retrieving Voice channels: {e}')
            await respond(ctx, False)
            return

    @_vclog.command(name='remove', aliases=['rm', '-'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _vclogdel(self, ctx, channels: str=None):
        """Voice Logging channel delete.

        Delete either the specified channel
        or default to current channel

        Parameters
        ----------
        channel: Optional[str]
            Optional parameter for the channel to remove

        Returns
        -------
        """
        todel = []
        if channels is None:
            todel.append(ctx.message.channel)
        else:
            for channel in channels.split(','):
                todel.append(get_channel(ctx, channel))
        todel = flatten(todel)
        try:
            for target in todel:
                success = await self.bot.pg.rem_voice_channel(
                    ctx.guild.id,
                    target.id,
                    self.bot.logger)
                await generic_message(ctx, [ctx.channel], f'Voice Logging channel has been deleted {target.mention}.', delete=15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Logging went wrong removing Voice Logging channels.')
            await ctx.send(embed=local_embed, delete_after=10)
            await respond(ctx, False)
            return
        pass

    @_vclog.command(name='add', aliases=['a', '+'])
    @commands.guild_only()
    @permissions.is_admin()
    async def _vclogadd(self, ctx, channel: str=None):
        """Voice Logging channel add.

        Add either the specified channel
        or default to current channel

        Parameters
        ----------
        channel: Optional[str]
            Optional parameter for the channel to add

        Returns
        -------
        """
        toadd = []
        if channels is None:
            toadd.append(ctx.message.channel)
        else:
            for channel in channels.split(','):
                toadd.append(get_channel(ctx, channel))
        toadd = flatten(toadd)
        try:
            for target in toadd:
                success = await self.bot.pg.add_voice_channel(
                    ctx.guild.id,
                    target.id,
                    self.bot.logger)
                await generic_message(ctx, [ctx.channel], f'Voice Logging channel has been added {target.mention}.', delete=15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong adding Voice Logging channels.')
            await ctx.send(embed=local_embed, delete_after=10)
            await respond(ctx, False)
            return

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
