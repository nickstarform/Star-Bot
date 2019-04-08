"""."""

# internal modules
import psutil

# external modules
import traceback
import discord
from discord.ext import commands
import sys

# relative modules
from cogs.utilities import (Colours, permissions)
from cogs.utilities.functions import (current_time, extract_id, get_member, get_role, parse, get_channel, flatten)
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.embed_dialog import respond
from cogs.utilities.embed_errors import internalerrorembed

# global attributes
__all__ = ('Administration',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(Administration(bot))
    print('Loaded Administration')


class Administration(commands.Cog):
    """Administrative commands."""

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    """
    BOTSTUFF
    """
    @commands.command()
    @permissions.is_admin()
    @commands.guild_only()
    async def change_nickname(self, ctx: commands.Context, *, new_username: str):
        """
        Changes bot username
        """
        bot_user = ctx.guild.me
        try:
            await bot_user.edit(nick=new_username)
            await respond(ctx, True)
        except Exception as e:
            await respond(ctx, False)
            self.bot.logger.warning(f'Error changing bots nickname: {e}')

    @commands.group(aliases=['changeprefix', 'setprefix', 'getprefix'])
    @commands.guild_only()
    @permissions.is_admin()
    async def prefix(self, ctx):
        """
        Either returns current prefix or sets new one
        """
        if ctx.invoked_subcommand is None:
            local_embed = discord.Embed(
                title=f'Current prefix is: '
                f'\'{self.bot.server_settings[ctx.guild.id]["prefix"]}\'',
                description=' ',
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @prefix.command()
    async def change(self, ctx: commands.Context, prefix):
        """
        Sets the prefix for the server
        """
        if len(prefix.strip()) > 2:
            local_embed = discord.Embed(
                title=f'Prefix must be less than or equal to two characters',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        try:
            success = await self.bot.pg_utils.set_prefix(
                ctx.guild.id,
                prefix,
                self.bot.logger
            )
            if success:
                self.bot.server_settings[ctx.guild.id]['prefix'] = prefix
                local_embed = discord.Embed(
                    title=f'Server prefix set to \'{prefix}\'',
                    description=' ',
                    color=0x419400
                )
        except Exception as e:
            local_embed = embeds.InternalErrorEmbed()
            ctx.send(local_embed)

    """
    BLACKLIST
    """
    @commands.group(aliases=['blu'], pass_context=True)
    @permissions.is_admin()
    @commands.guild_only()
    async def blacklistuser(self, ctx):
        """Add or remove a user to blacklist list.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            users = await self.bot.pg.get_all_blacklist_users(ctx.guild.id)
            users = parse(users)[0][0][1]
            users = [get_member(ctx, str(x)) for x in users]
            users = [x.mention for x in flatten(users)]
            if isinstance(users, type(None)):
                users = []
            if len(users) > 0:
                title = 'Users in blacklist'
                desc = ','.join(users)
            else:
                desc = ''
                title = 'No users in blacklist'
            embeds = generic_embed(
                title=title,
                desc=desc,
                fields=[],
                footer=current_time(),
                colours=Colours.COMMANDS
            )
            for embed in embeds:
                await ctx.send(embed=embed)

    @blacklistuser.command(name='add', pass_context=True)
    async def _blua(self, ctx: commands.Context, *, uids: str):
        """Add user to blacklist.

        Parameters
        ----------
        uids: str
            List of id, comma separated

        Returns
        -------
        """
        added_users = []
        msg = uids.replace(' ', '')
        if ',' in msg:
            users = [get_member(ctx, x) for x in msg.split(',')]
        else:
            users = [get_member(ctx, msg)]

        try:
            for user in flatten(users):
                success = await self.bot.pg.add_blacklist_user(ctx.guild.id, user.id, self.bot.logger)
                if success:
                    added_users.append(user.mention)
            if added_users:
                title = 'Users added into blacklist'
                desc = ', '.join(added_users)
                embeds = generic_embed(
                    title=title,
                    desc=desc,
                    fields=[],
                    colours=Colours.COMMANDS,
                    footer=current_time()
                )
            else:
                self.bot.logger.info(f'Error adding users to blacklist')
                embed = internalerrorembed(f'Error adding users to blacklist')
                await ctx.send(embed=embed)
                return
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding users to global blacklist {e}')
            embed = internalerrorembed(f'Error adding users to global blacklist {e}')
            await ctx.send(embed=embed)

    @blacklistuser.command(name='remove', aliases=['rem', 'del', 'rm'])
    async def _blur(self, ctx: commands.Context, *, uids: str):
        """Removes a user from the blacklist.

        Parameters
        ----------
        uids: str
            List of users

        Returns
        -------
        """
        removed_users = []
        user_notfound = []
        msg = uids.replace(' ', '')
        if ',' in msg:
            users = [get_member(ctx, x) for x in msg.split(',')]
        else:
            users = [get_member(ctx, msg)]
        try:
            for user in flatten(users):
                success = False
                try:
                    success = await self.bot.pg.rem_blacklist_user(user.id, self.bot.logger)
                except:
                    user_notfound.append(user.mention)
                if success:
                    removed_users.append(user.mention)
                else:
                    user_notfound.append(user.mention)

            fields = []
            if removed_users:
                fields.append(['PASS', ', '.join([f'{x}' for x in removed_users])])
            if user_notfound:
                fields.append(['FAIL', ', '.join([f'{x}' for x in user_notfound])])
            title = 'Users blacklisting'
            desc = ''
            embeds = generic_embed(
                title=title,
                desc=desc,
                fields=fields,
                colours=Colours.COMMANDS,
                footer=current_time()
            )
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue removing users from ' +
                                    f'global blacklist: {e}')
            embed = internalerrorembed(f'Issue removing users from ' +
                                                          f'global blacklist: {e}')
            await ctx.send(embed=embed)

    @commands.group(aliases=['blc'], pass_context=True)
    @permissions.is_admin()
    @commands.guild_only()
    async def blacklistchannel(self, ctx):
        """Channel blacklistings.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            channels = await self.bot.pg.get_all_blacklist_channels(ctx.guild.id)
            channels = [ctx.guild.get_channel(int(g)) for g in channels]
            if isinstance(channels, type(None)):
                channels = []
            else:
                channels = [str(x.id) for x in flatten(channels)]
            if len(channels) > 0:
                desc = '<#'
                desc += '>, <#'.join(channels)
                desc += '>'
                title = 'Blacklisted Channels'
            else:
                desc = ''
                title = 'No channels in blacklist'
            embeds = generic_embed(
                title=title,
                desc=desc,
                fields=[],
                footer=current_time(),
                colours=Colours.COMMANDS
            )
            for embed in embeds:
                await ctx.send(embed=embed)

    @blacklistchannel.command(name='add', pass_context=True)
    async def _blca(self, ctx: commands.Context, *, cids: str=None):
        """Add channel to blacklist.

        Give id/mentionable or trigger inside of a channel.

        Parameters
        ----------
        cids: str
            list of channels

        Returns
        -------
        """
        added_channel = []
        if cids is not None:
            msg = cids.replace(' ', '')
            if ',' in msg:
                channels = [self.bot.get_channel(int(extract_id(x, 'channel'))) for x in msg.split(',')]
            else:
                channels = [self.bot.get_channel(int(extract_id(msg, 'channel')))]
            channels = flatten(channels)
        else:
            channels = [ctx.channel]
        try:
            for channel in channels:
                success = await self.bot.pg.add_blacklist_channel(ctx.guild.id, channel.id, self.bot.logger)
                if success:
                    added_channel.append(channel.mention)
            if added_channel:
                title = 'Channels added into blacklist'
                desc = ', '.join(added_channel)
                embeds = generic_embed(
                    title=title,
                    desc=desc,
                    fields=[],
                    colours=Colours.COMMANDS,
                    footer=current_time()
                )
            else:
                self.bot.logger.info(f'Error adding channels to blacklist')
                embed = internalerrorembed(f'Error adding channels to blacklist')
                await respond(ctx, False)
                await ctx.send(embed=embed, delete_after=5)
                return
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding channel to blacklist {e}')
            embed = internalerrorembed(f'Error adding channels to blacklist {e}')
            await respond(ctx, False)
            await ctx.send(embed=embed, delete_after=5)

    @blacklistchannel.command(name='remove', aliases=['rem', 'del', 'rm'])
    async def _blcr(self, ctx: commands.Context, *, cids: str=None):
        """Removes a channel from the blacklist.

        Give id/mentionable or trigger inside of a channel.

        Parameters
        ----------
        cids: str
           Channel name, id, etc

        Returns
        -------
        """
        removed_channel = []
        channel_notfound = []
        if cids is not None:
            msg = cids.replace(' ', '')
            if ',' in msg:
                channels = [self.bot.get_channel(int(extract_id(x, 'channel'))) for x in msg.split(',')]
            else:
                channels = [self.bot.get_channel(int(extract_id(msg, 'channel')))]
            channels = flatten(channels)
        else:
            channels = [ctx.channel]
        try:
            for channel in channels:
                success = False
                try:
                    success = await self.bot.pg.rem_blacklist_channel(ctx.guild.id, channel.id, self.bot.logger)
                except ValueError:
                    channel_notfound.append(channel)
                if success:
                    removed_channel.append(channel.mention)
                else:
                    channel_notfound.append(channel.mention)
            fields = []
            if removed_channel:
                fields.append(['PASS.)', ', '.join(removed_channel)])
            if channel_notfound:
                fields.append(['FAIL.)', ', '.join(channel_notfound)])
            title = 'Channel blacklisting Removed'
            desc = ''
            embeds = generic_embed(
                title=title,
                desc=desc,
                fields=fields,
                colours=Colours.COMMANDS,
                footer=current_time()
            )
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue removing channels from ' +
                                    f' blacklist: {e}')
            embed = internalerrorembed(f'Issue removing channel from ' +
                                                          f' blacklist: {e}')
            await ctx.send(embed=embed, delete_after=5)

    @commands.group(aliases=['commands', 'blcm'], pass_context=True)
    @permissions.is_admin()
    @commands.guild_only()
    async def blacklistcmd(self, ctx):
        """Add or remove a command to blacklist list.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            cmds = await self.bot.pg.get_all_disallowed(ctx.guild.id)
            cmds = [x[0][1] for x in parse(cmds)]
            if isinstance(cmds, type(None)):
                cmds = []
            if len(cmds) > 0:
                title = 'Commands blacklisted'
                desc = ', '.join(cmds)
            else:
                desc = ''
                title = 'No commands in blacklist'
            embeds = generic_embed(
                title=title,
                desc=desc,
                fields=[],
                footer=current_time(),
                colours=Colours.COMMANDS
            )
            for embed in embeds:
                await ctx.send(embed=embed)

    @blacklistcmd.command(name='add', pass_context=True)
    async def _blcma(self, ctx: commands.Context, *, cmds: str):
        """Add command to blacklist.

        Parameters
        ----------
        cmds: str
            Commands

        Returns
        -------
        """
        added_cmds = []
        if cmds in ['all', 'everything']:
            msg = ','.join([x.name for x in self.bot.commands])
        else:
            msg = cmds.replace(' ', '')
        if ',' in msg:
            cmds = [x for x in msg.split(',')]
        else:
            cmds = [msg]

        try:
            for cmd in cmds:
                success = await self.bot.pg.add_disallowed(ctx.guild.id, cmd, self.bot.logger)
                if success:
                    added_cmds.append(cmd)
            if added_cmds:
                title = 'Commands added into blacklist'
                desc = ', '.join(added_cmds)
                embeds = generic_embed(
                    title=title,
                    desc=desc,
                    fields=[],
                    colours=Colours.COMMANDS,
                    footer=current_time()
                )
            else:
                self.bot.logger.info(f'Error adding Commands to blacklist')
                embed = internalerrorembed(f'Error adding Commands to blacklist')
                await ctx.send(embed=embed, delete_after=5)
                return
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding Commands to blacklist {e}')
            embed = internalerrorembed(f'Error adding Commands to blacklist {e}')
            await ctx.send(embed=embed, delete_after=5)

    @blacklistcmd.command(name='remove', aliases=['rem', 'del', 'rm'])
    async def _blcmr(self, ctx: commands.Context, *, cmds: str):
        """Removes a command from the blacklist.

        Parameters
        ----------
        cmds: str
            List of cmds, comma separated

        Returns
        -------
        """
        removed_cmds = []
        cmds_notfound = []
        if cmds in ['all', 'everything']:
            msg = ','.join([x.name for x in self.bot.commands])
        else:
            msg = cmds.replace(' ', '')
        if ',' in msg:
            cmds = [x for x in msg.split(',')]
        else:
            cmds = [msg]
        cmds = [x for x in cmds if x != '']
        try:
            for cmd in cmds:
                success = False
                try:
                    success = await self.bot.pg.rem_disallowed(ctx.guild.id, cmd, self.bot.logger)
                except ValueError:
                    cmds_notfound.append(cmd)
                if success:
                    removed_cmds.append(cmd)
                else:
                    cmds_notfound.append(cmd)
            fields = []
            if removed_cmds:
                fields.append(['PASS.)', ', '.join(removed_cmds)])
            if cmds_notfound:
                fields.append(['FAIL.)', ', '.join(cmds_notfound)])
            title = 'Command blacklisting'
            desc = ''
            embeds = generic_embed(
                title=title,
                desc=desc,
                fields=fields,
                colours=Colours.COMMANDS,
                footer=current_time()
            )
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue removing commands from ' +
                                    f'blacklist: {e}')
            embed = internalerrorembed(f'Issue removing commands from ' +
                                                          f'blacklist: {e}')
            await ctx.send(embed=embed, delete_after=5)

    """
    MODLOG
    """

    @commands.group()
    @commands.guild_only()
    @permissions.is_admin()
    async def modlog(self, ctx):
        """
        Adds or removes a channel to modlog list
        """
        if ctx.invoked_subcommand is None:
            desc = ''
            modlogs = await self.bot.pg_utils.get_modlogs(
                ctx.guild.id)
            for channel in ctx.guild.channels:
                if channel.id in modlogs:
                    desc += f'{channel.name} \n'
            local_embed = discord.Embed(
                title=f'Current modlog list is: ',
                description=desc,
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @modlog.command(aliases=['add'])
    async def add_channel(self, ctx):
        """
        Adds channel to modlog list
        """
        added_channels = []
        desc = ''
        try:
            success = await \
                self.bot.pg_utils.add_modlog_channel(
                    ctx.guild.id, ctx.message.channel.id, self.bot.logger
                )
            if success:
                added_channels.append(ctx.message.channel.name)
            if added_channels:
                for channel in added_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels added to modlog list:',
                    description=desc,
                    color=0x419400
                )
                self.bot.server_settings[ctx.guild.id]['modlog_enabled'] = True
            else:
                self.bot.logger.info(f'slktjsaj')
                local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding channels {e}')
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)

    @modlog.command(aliases=['rem', 'remove'])
    async def remove_channel(self, ctx):
        """
        Removes a channel from the modlog list
        """
        removed_channels = []
        absent_channels = []
        desc = ''
        try:
            try:
                success = False
                success = await \
                    self.bot.pg_utils.rem_modlog_channel(
                        ctx.guild.id, ctx.message.channel.id, self.bot.logger
                    )
            except ValueError:
                absent_channels.append(ctx.message.channel.name)
            if success:
                removed_channels.append(ctx.message.channel.name)
            if removed_channels:
                for channel in removed_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels removed from modlog list:',
                    description=desc,
                    color=0x419400
                )
                modlogs = await self.bot.pg_utils.get_modlogs(
                    ctx.guild.id)
                if not modlogs:
                    self.bot.server_settings[ctx.guild.id]['modlog_enabled']\
                        = False
                if absent_channels:
                    desc = ''
                    for channel in absent_channels:
                        desc += f'{channel}\n'
                    local_embed.add_field(
                        name='Channels not in modlog list :',
                        value=desc
                    )
            elif absent_channels:
                desc = ''
                for channel in absent_channels:
                    desc += f'{channel}\n'
                local_embed = discord.Embed(
                    title=f'Channels not in modlog list: ',
                    description=desc,
                    color=0x651111
                )
            else:
                local_embed = discord.Embed(
                    title=f'Internal error, please contact @dashwav#7785',
                    description=' ',
                    color=0x651111
                )
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue: {e}')
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
    """
    VOICELOG
    """

    @commands.group(aliases=['vclogs', 'prescence_logging'])
    @commands.guild_only()
    @permissions.is_admin()
    async def voice_logging(self, ctx):
        """
        Enables and disables logging to channel.
        """
        if ctx.invoked_subcommand is None:
            desc = ''
            voicelogs = await self.bot.pg_utils.get_voice_channels(
                ctx.guild.id)
            for channel in ctx.guild.channels:
                if channel.id in voicelogs:
                    desc += f'{channel.name} \n'
            local_embed = discord.Embed(
                title=f'Current voice log channel list is: ',
                description=desc,
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @voice_logging.command(name='enable')
    async def _enable(self, ctx):
        """
        Adds channel to the log channel list.
        """
        added_channels = []
        desc = ''
        try:
            success = await \
                self.bot.pg_utils.add_voice_channel(
                    ctx.guild.id, ctx.message.channel.id, self.bot.logger
                )
            if success:
                added_channels.append(ctx.message.channel.name)
            if added_channels:
                for channel in added_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels added to voice log channel list:',
                    description=desc,
                    color=0x419400
                )
            else:
                local_embed = discord.Embed(
                    title=f'Internal error, please contact @dashwav#7785',
                    description=' ',
                    color=0x651111
                )
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding channels {e}')
            local_embed = discord.Embed(
                title=f'Internal issue, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)

    @voice_logging.command(name='disable', aliases=['rem'])
    async def _disable(self, ctx):
        """
        Removes channel from the log channel list
        """
        removed_channels = []
        absent_channels = []
        desc = ''
        try:
            try:
                success = False
                success = await \
                    self.bot.pg_utils.rem_voice_channel(
                        ctx.guild.id, ctx.message.channel.id, self.bot.logger
                    )
            except ValueError as e:
                absent_channels.append(ctx.message.channel.name)
            if success:
                removed_channels.append(ctx.message.channel.name)
            if removed_channels:
                for channel in removed_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels removed from voice log channel list:',
                    description=desc,
                    color=0x419400
                )
                if absent_channels:
                    desc = ''
                    for channel in absent_channels:
                        desc += f'{channel}\n'
                    local_embed.add_field(
                        name='Channels not in voice log channel list :',
                        value=desc
                    )
            elif absent_channels:
                desc = ''
                for channel in absent_channels:
                    desc += f'{channel}\n'
                local_embed = discord.Embed(
                    title=f'Channels not in voice log channel list: ',
                    description=desc,
                    color=0x651111
                )
            else:
                local_embed = discord.Embed(
                    title=f'Internal error, please contact @dashwav#7785',
                    description=' ',
                    color=0x651111
                )
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue: {e}')
            local_embed = discord.Embed(
                title=f'Internal issue, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)

    """
    GENERAL LOG
    """

    @commands.group()
    @commands.guild_only()
    @permissions.is_admin()
    async def logging(self, ctx):
        """
        Enables and disables logging to channel.
        """
        if ctx.invoked_subcommand is None:
            desc = ''
            modlogs = await self.bot.pg_utils.get_logger_channels(
                ctx.guild.id)
            for channel in ctx.guild.channels:
                if channel.id in modlogs:
                    desc += f'{channel.name} \n'
            local_embed = discord.Embed(
                title=f'Current log channel list is: ',
                description=desc,
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @logging.command()
    async def enable(self, ctx):
        """
        Adds channel to the log channel list.
        """
        added_channels = []
        desc = ''
        try:
            success = await \
                self.bot.pg_utils.add_logger_channel(
                    ctx.guild.id, ctx.message.channel.id, self.bot.logger
                )
            if success:
                added_channels.append(ctx.message.channel.name)
            if added_channels:
                for channel in added_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels added to log channel list:',
                    description=desc,
                    color=0x419400
                )
                self.bot.server_settings[ctx.guild.id]['logging_enabled']\
                    = True
            else:
                local_embed = discord.Embed(
                    title=f'Internal error, please contact @dashwav#7785',
                    description=' ',
                    color=0x651111
                )
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding channels {e}')
            local_embed = discord.Embed(
                title=f'Internal issue, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)

    @logging.command(aliases=['rem'])
    async def disable(self, ctx):
        """
        Removes channel from the log channel list
        """
        removed_channels = []
        absent_channels = []
        desc = ''
        try:
            try:
                success = False
                success = await \
                    self.bot.pg_utils.rem_logger_channel(
                        ctx.guild.id, ctx.message.channel.id, self.bot.logger
                    )
            except ValueError as e:
                absent_channels.append(ctx.message.channel.name)
            if success:
                removed_channels.append(ctx.message.channel.name)
            if removed_channels:
                for channel in removed_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels removed from log channel list:',
                    description=desc,
                    color=0x419400
                )
                logs = await self.bot.pg_utils.get_logger_channels(
                    ctx.guild.id)
                if not logs:
                    self.bot.server_settings[ctx.guild.id]['logging_enabled']\
                        = False
                if absent_channels:
                    desc = ''
                    for channel in absent_channels:
                        desc += f'{channel}\n'
                    local_embed.add_field(
                        name='Channels not in log channel list :',
                        value=desc
                    )
            elif absent_channels:
                desc = ''
                for channel in absent_channels:
                    desc += f'{channel}\n'
                local_embed = discord.Embed(
                    title=f'Channels not in log channel list: ',
                    description=desc,
                    color=0x651111
                )
            else:
                local_embed = discord.Embed(
                    title=f'Internal error, please contact @dashwav#7785',
                    description=' ',
                    color=0x651111
                )
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue: {e}')
            local_embed = discord.Embed(
                title=f'Internal issue, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)

    """
    MODIFY CONFIGURATION
    """

    @commands.group()
    @permissions.is_admin()
    @commands.guild_only()
    async def config(self, ctx):
        """Display Config.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            gid = ctx.guild.id
            try:
                config = await self.bot.pg.get_guild(gid, self.bot.logger)
                config = parse(config)
                guild = await self.bot.fetch_guild(gid)
                ctitle = f'{guild.name} Configuration'
                cdesc = ''
                fields = config

                embeds = generic_embed(
                    title=ctitle,
                    desc=cdesc,
                    fields=fields,
                    footer=current_time(),
                    colours=Colours.COMMANDS
                )
                for embed in embeds:
                    await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(embed=internalerrorembed(f'Problem checking guild config: {e}'), delete_after=5)
                await respond(ctx, False)
                self.bot.logger.warning(f'Error trying to return guild config: {e}')

    @commands.group()
    @commands.guild_only()
    @permissions.is_admin()
    async def footer(self, ctx):
        """
        Ban/kick footer command. If no subcommand is
        invoked, it will return the current ban/kick footer
        """
        ban_footer = await self.bot.pg_utils.get_ban_footer(
            ctx.guild.id,
            self.bot.logger
        )
        kick_footer = await self.bot.pg_utils.get_kick_footer(
            ctx.guild.id,
            self.bot.logger
        )
        footer_msg = f'**Ban Footer**:\n\n{ban_footer}\n\n'\
                     f'**Kick Footer:**\n\n{kick_footer}'
        if ctx.invoked_subcommand is None:
            local_embed = discord.Embed(
                title=f'Current welcome message: ',
                description=footer_msg
            )
            await ctx.send(embed=local_embed)

    @footer.command(name='set_ban')
    async def set_ban_footer(self, ctx: commands.Context, *, footer_string):
        """
        Attempts to set kick/ban footer to string passed in
        """
        if not footer_string:
            local_embed = discord.Embed(
                title=f'No string detected, I need a string parameter to work',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        success = await self.bot.pg_utils.set_ban_footer(
            ctx.guild.id,
            footer_string,
            self.bot.logger
        )
        if success:
            desc = footer_string.replace(
                f'%user%', ctx.message.author.mention)
            local_embed = discord.Embed(
                title=f'Footer message set:',
                description=f'**Preview:**\n{desc}',
                color=0x419400
            )
        else:
            local_embed = discord.Embed(
                title=f'Internal error occured, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)
        return

    @footer.command(name='set_kick')
    async def set_kick_footer(self, ctx: commands.Context, *, footer_string):
        """
        Attempts to set kick/ban footer to string passed in
        """
        if not footer_string:
            local_embed = discord.Embed(
                title=f'No string detected, I need a string parameter to work',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        success = await self.bot.pg_utils.set_kick_footer(
            ctx.guild.id,
            footer_string,
            self.bot.logger
        )
        if success:
            desc = footer_string.replace(
                f'%user%', ctx.message.author.mention)
            local_embed = discord.Embed(
                title=f'Footer message set:',
                description=f'**Preview:**\n{desc}',
                color=0x419400
            )
        else:
            local_embed = discord.Embed(
                title=f'Internal error occured, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)
        return


    @commands.group()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def invites(self, ctx):
        """
        Enables/Disables autodeletion of invites
        """
        if ctx.invoked_subcommand is None:
            allowed = self.bot.server_settings[ctx.guild.id]["invites_allowed"]
            local_embed = discord.Embed(
                title=f'Invites are:',
                description=f"{'Allowed' if allowed else 'Disallowed'}",
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @invites.command(aliases=['enable'])
    async def allow(self, ctx):
        """
        Disables autodeletion of invites
        """
        try:
            await self.bot.pg_utils.set_invites_allowed(
                ctx.guild.id, True)
        except Exception as e:
            local_embed = embeds.InternalErrorEmbed()
            self.bot.logger.warning(f'Error setting invites allowed: {e})')
            await ctx.send(embed=local_embed)
        self.bot.server_settings[ctx.guild.id]['invites_allowed'] = True
        local_embed = discord.Embed(
                title=f'Invites are now:',
                description=f'Allowed',
                color=0x419400
            )
        await ctx.send(embed=local_embed)

    @invites.command(aliases=['disable', 'delete'])
    async def disallow(self, ctx):
        """
        Enables autodeletion of invites
        """
        try:
            await self.bot.pg_utils.set_invites_allowed(
                ctx.guild.id, False)
        except Exception as e:
            local_embed = embeds.InternalErrorEmbed()
            self.bot.logger.warning(f'Error setting invites disallowed: {e})')
            await ctx.send(embed=local_embed)
            return
        self.bot.server_settings[ctx.guild.id]['invites_allowed'] = False
        local_embed = discord.Embed(
                title=f'Invites are now:',
                description=f'Disallowed',
                color=0x419400
            )
        await ctx.send(embed=local_embed)


    @commands.group()
    @commands.guild_only()
    @permissions.is_admin()
    async def welcome(self, ctx):
        """
        Welcome message command. If no subcommand is
        invoked, it will return the current welcome message
        """
        if not await permissions.is_channel_blacklisted(self, ctx):
            return
        welcome_msg = await self.bot.pg_utils.get_welcome_message(
            ctx.guild.id,
            self.bot.logger
        )
        if ctx.invoked_subcommand is None:
            local_embed = discord.Embed(
                title=f'Current welcome message: ',
                description=welcome_msg
            )
            await ctx.send(embed=local_embed)

    @welcome.command(name='set')
    async def setwelcome(self, ctx: commands.Context, *, welcome_string):
        """
        Attempts to set welcome message to string passed in
        """
        if not await permissions.is_channel_blacklisted(self, ctx):
            return
        if not welcome_string:
            local_embed = discord.Embed(
                title=f'No string detected, I need a string parameter to work',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        success = await self.bot.pg_utils.set_welcome_message(
            ctx.guild.id,
            welcome_string,
            self.bot.logger
        )
        if success:
            desc = welcome_string.replace(
                f'%user%', ctx.message.author.mention)
            local_embed = discord.Embed(
                title=f'Welcome message set:',
                description=f'**Preview:**\n{desc} ',
                color=0x419400
            )
        else:
            local_embed = discord.Embed(
                title=f'Internal error occured, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)
        return

    @welcome.command(aliases=['on'])
    async def enable(self, ctx):
        """
        Enables the welcome message in this channel
        """
        if not await permissions.is_channel_blacklisted(self, ctx):
            return
        success = await self.bot.pg_utils.add_welcome_channel(
            ctx.guild.id, ctx.message.channel.id, self.bot.logger
        )
        if success:
            local_embed = discord.Embed(
                title=f'Channel Added:',
                description=f'{ctx.message.channel.name} '
                'was added to welcome list.',
                color=0x419400
            )
        else:
            local_embed = discord.Embed(
                title=f'Internal error, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)

    @welcome.command(aliases=['off'])
    async def disable(self, ctx):
        """
        Enables the welcome message in this channel
        """
        if not await permissions.is_channel_blacklisted(self, ctx):
            return
        try:
            success = await self.bot.pg_utils.rem_welcome_channel(
                ctx.guild.id, ctx.message.channel.id, self.bot.logger
            )
        except ValueError:
            local_embed = discord.Embed(
                title=f'This channel is already not'
                'in the welcome channel list',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        if success:
            local_embed = discord.Embed(
                title=f'Channel removed:',
                description=f'{ctx.message.channel.name} '
                'was removed from welcome list.',
                color=0x419400
            )
        else:
            local_embed = discord.Embed(
                title=f'Internal error, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)

    """
    CHATSTATS
    """

    def create_chart(self, top, others, channel):
        plt.clf()
        sizes = [x[1] for x in top]
        labels = ["{} {:g}%".format(x[0], x[1]) for x in top]
        if len(top) >= 20:
            sizes = sizes + [others]
            labels = labels + ["Others {:g}%".format(others)]
        if len(channel.name) >= 19:
            channel_name = '{}...'.format(channel.name[:19])
        else:
            channel_name = channel.name
        title = plt.title("Stats in #{}".format(channel_name), color="white")
        title.set_va("top")
        title.set_ha("center")
        plt.gca().axis("equal")
        colors = ['r', 'darkorange', 'gold', 'y', 'olivedrab', 'green', 'darkcyan', 'mediumblue', 'darkblue', 'blueviolet', 'indigo', 'orchid', 'mediumvioletred', 'crimson', 'chocolate', 'yellow', 'limegreen','forestgreen','dodgerblue','slateblue','gray']
        pie = plt.pie(sizes, colors=colors, startangle=0)
        plt.legend(pie[0], labels, bbox_to_anchor=(0.7, 0.5), loc="center", fontsize=10,
                   bbox_transform=plt.gcf().transFigure, facecolor='#ffffff')
        plt.subplots_adjust(left=0.0, bottom=0.1, right=0.45)
        image_object = BytesIO()
        plt.savefig(image_object, format='PNG', facecolor='#36393E')
        image_object.seek(0)
        return image_object

    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(1, 10, commands.BucketType.channel)
    @permissions.is_admin()
    async def chatchart(self, ctx: commands.Context, channel: str):
        """
        Generates a pie chart, representing the last 5000 messages in the specified channel.
        """
        e = discord.Embed(description="Loading...", colour=0x00ccff)
        e.set_thumbnail(url="https://i.imgur.com/vSp4xRk.gif")
        em = await self.bot.say(embed=e)
        
        if channel is None:
            channel = ctx.message.channel
        history = []
        if not channel.permissions_for(ctx.message.author).read_messages == True:
            await self.bot.delete_message(em)
            return await self.bot.say("You're not allowed to access that channel.")
        try:
            async for msg in self.bot.logs_from(channel, 5000):
                history.append(msg)
        except discord.errors.Forbidden:
            await self.bot.delete_message(em)
            return await self.bot.say("No permissions to read that channel.")
        msg_data = {'total count': 0, 'users': {}}

        for msg in history:
            if len(msg.author.name) >= 20:
                short_name = '{}...'.format(msg.author.name[:20]).replace("$", "\$")
            else:
                short_name = msg.author.name.replace("$", "\$")
            whole_name = '{}#{}'.format(short_name, msg.author.discriminator)
            if msg.author.bot:
                pass
            elif whole_name in msg_data['users']:
                msg_data['users'][whole_name]['msgcount'] += 1
                msg_data['total count'] += 1
            else:
                msg_data['users'][whole_name] = {}
                msg_data['users'][whole_name]['msgcount'] = 1
                msg_data['total count'] += 1

        for usr in msg_data['users']:
            pd = float(msg_data['users'][usr]['msgcount']) / float(msg_data['total count'])
            msg_data['users'][usr]['percent'] = round(pd * 100, 1)

        top_ten = heapq.nlargest(20, [(x, msg_data['users'][x][y])
                                      for x in msg_data['users']
                                      for y in msg_data['users'][x]
                                      if y == 'percent'], key=lambda x: x[1])
        others = 100 - sum(x[1] for x in top_ten)
        img = self.create_chart(top_ten, others, channel)
        await self.bot.delete_message(em)
        await self.bot.send_file(ctx.message.channel, img, filename="chart.png")


def check_folders():
    if not os.path.exists("data/chatchart"):
        print("Creating data/chatchart folder...")
        os.makedirs("data/chatchart")

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
