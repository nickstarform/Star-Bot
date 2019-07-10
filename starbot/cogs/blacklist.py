"""."""

# internal modules

# external modules
from discord.ext import commands

# relative modules
from cogs.utilities import (Colours, permissions)
from cogs.utilities.functions import (current_time, extract_id, get_member, get_channel, flatten)
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.embed_dialog import respond
from cogs.utilities.embed_errors import internalerrorembed

# global attributes
__all__ = ('Blacklist',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(Blacklist(bot))
    print('Loaded Blacklisting')


class Blacklist(commands.Cog):
    """Administrative commands."""

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    """
    BLACKLIST
    """
    @commands.group(aliases=['blgu'], pass_context=True)
    @permissions.is_master()
    async def blacklistglobaluser(self, ctx):
        """Add or remove a user to blacklist global list.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            users = await self.bot.pg.get_all_blacklist_users_global()
            if isinstance(users, type(None)):
                users = []
            if len(users) > 0:
                title = 'Users in global blacklist'
                desc = '<@'
                desc += '>, <@'.join(map(str, users))
                desc += '>'
            else:
                desc = ''
                title = 'No users in global blacklist'
            embeds = generic_embed(
                title=title,
                desc=desc,
                fields=[],
                footer=current_time(),
                colours=Colours.COMMANDS
            )
            for embed in embeds:
                await ctx.send(embed=embed)

    @blacklistglobaluser.command(name='add', pass_context=True)
    async def _blgua(self, ctx: commands.Context, uids: str=None):
        """Add user to global blacklist.

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
            users = [extract_id(x, 'member') for x in msg.split(',')]
        else:
            users = [extract_id(msg, 'member')]
        users = [x for x in users if x != '']

        try:
            for user in users:
                success = await self.bot.pg.add_blacklist_user_global(user)
                if success:
                    added_users.append(user)
            if added_users:
                self.bot.blglobal += list(map(int, added_users))
                title = 'Users added into global blacklist'
                desc = '<@'
                desc += '>, <@'.join(map(str, added_users))
                desc += '>'
                embeds = generic_embed(
                    title=title,
                    desc=desc,
                    fields=[],
                    colours=Colours.COMMANDS,
                    footer=current_time()
                )
            else:
                self.bot.logger.info(f'Error adding users to global blacklist')
                embed = internalerrorembed(f'Error adding users to global blacklist')
                await respond(ctx, False)
                await ctx.send(embed=embed, delete_after=5)
                return
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding users to global blacklist {e}')
            embed = internalerrorembed(f'Error adding users to global blacklist {e}')
            await respond(ctx, False)
            await ctx.send(embed=embed, delete_after=5)

    @blacklistglobaluser.command(name='remove', aliases=['rem', 'del', 'rm'])
    async def _blgur(self, ctx: commands.Context, uids: str=None):
        """Removes a user from the blacklist.

        Parameters
        ----------
        uids: str
            List of id, comma separated

        Returns
        -------
        """
        removed_users = []
        user_notfound = []
        msg = uids.replace(' ', '')
        if ',' in msg:
            users = [extract_id(x, 'member') for x in msg.split(',')]
        else:
            users = [extract_id(msg, 'member')]
        print(users)

        try:
            for user in users:
                success = False
                try:
                    success = await self.bot.pg.rem_blacklist_user_global(user)
                    if success:
                        self.bot.blglobal.remove(int(user))
                        removed_users.append(user)
                    else:
                        user_notfound.append(user)
                except:
                    user_notfound.append(user)

            fields = []
            if removed_users:
                fields.append(['PASS', ', '.join([f'<@{x}>' for x in removed_users])])
            if user_notfound:
                fields.append(['FAIL', ', '.join([f'<@{x}>' for x in user_notfound])])
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
            await ctx.send(embed=embed, delete_after=5)
            await respond(ctx, False)

    @commands.group(aliases=['blgg'], pass_context=True)
    @permissions.is_master()
    async def blacklistglobalguild(self, ctx):
        """Add or remove a guild to blacklist global list.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            guilds = await self.bot.pg.get_all_blacklist_guild_global()
            if isinstance(guilds, type(None)):
                guilds = []
            if len(guilds) > 0:
                title = 'Guilds in global blacklist'
                desc = '<'
                desc += '>, <'.join(map(str, guilds))
                desc += '>'
            else:
                desc = ''
                title = 'No guilds in global blacklist'
            embeds = generic_embed(
                title=title,
                desc=desc,
                fields=[],
                footer=current_time(),
                colours=Colours.COMMANDS
            )
            for embed in embeds:
                await ctx.send(embed=embed)

    @blacklistglobalguild.command(name='add', pass_context=True)
    async def _blgga(self, ctx: commands.Context, *, gids: str=None):
        """Add guild to global blacklist.

        Give id or trigger inside of a guild.

        Parameters
        ----------
        uids: str
            List of id, comma separated

        Returns
        -------
        """
        added_guilds = []
        if gids is not None:
            msg = gids.replace(' ', '')
            if ',' in msg:
                guilds = [extract_id(x, 'guild') for x in msg.split(',')]
            else:
                guilds = [extract_id(msg, 'guild')]
            guilds = flatten(guilds)
        else:
            guilds = [ctx.guild.id]

        try:
            for guild in guilds:
                success = await self.bot.pg.add_blacklist_guild_global(guild)
                if success:
                    added_guilds.append(guild)
            if added_guilds:
                self.bot.blglobal += list(map(int, added_guilds))
                title = 'Guilds added into global blacklist'
                desc = '<'
                desc += '>, <'.join(map(str, added_guilds))
                desc += '>'
                embeds = generic_embed(
                    title=title,
                    desc=desc,
                    fields=[],
                    colours=Colours.COMMANDS,
                    footer=current_time()
                )
            else:
                self.bot.logger.info(f'Error adding guilds to global blacklist')
                embed = internalerrorembed(f'Error adding guilds to global blacklist')
                await ctx.send(embed=embed, delete_after=5)
                await respond(ctx, False)
                return
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding guilds to global blacklist {e}')
            embed = internalerrorembed(f'Error adding guilds to global blacklist {e}')
            await ctx.send(embed=embed, delete_after=5)
            await respond(ctx, False)

    @blacklistglobalguild.command(name='remove', aliases=['rem', 'del', 'rm'])
    async def _blggr(self, ctx: commands.Context, gids: str=None):
        """Removes a guild from the blacklist.

        Give id or trigger inside of a guild.

        Parameters
        ----------
        gids: str
            List of id, comma separated

        Returns
        -------
        """
        removed_guilds = []
        guild_notfound = []
        if gids is not None:
            msg = gids.replace(' ', '')
            if ',' in msg:
                guilds = [extract_id(x, 'guild') for x in msg.split(',')]
            else:
                guilds = [extract_id(msg, 'guild')]
            guilds = flatten(guilds)
        else:
            guilds = [ctx.guild.id]

        try:
            for guild in guilds:
                success = False
                try:
                    success = await self.bot.pg.rem_blacklist_guild_global(guild)
                    if success:
                        self.bot.blglobal.remove(int(guild))
                        removed_guilds.append(guild)
                    else:
                        guild_notfound.append(guild)
                except ValueError:
                    guild_notfound.append(guild)
            fields = []
            if removed_guilds:
                fields.append(['PASS.)', ', '.join([f'<@{x}>' for x in removed_guilds])])
            if guild_notfound:
                fields.append(['FAIL.)', ', '.join([f'<@{x}>' for x in guild_notfound])])
            title = 'Guilds blacklisting Removed'
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
            self.bot.logger.warning(f'Issue removing guilds from ' +
                                    f'global blacklist: {e}')
            embed = internalerrorembed(f'Issue removing guilds from ' +
                                                          f'global blacklist: {e}')
            await ctx.send(embed=embed, delete_after=5)
            await respond(ctx, False)

    @commands.group(aliases=['globalcommands', 'blgc'], pass_context=True)
    @permissions.is_master()
    async def blacklistglobalcmd(self, ctx):
        """Add or remove a command to blacklist global list.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            cmds = await self.bot.pg.get_all_disallowed_global()
            cmds = [x['disallowed_command'] for x in cmds]
            if isinstance(cmds, type(None)):
                cmds = []
            if len(cmds) > 0:
                title = 'Commands blacklisted globally'
                desc = ', '.join(cmds)
            else:
                desc = ''
                title = 'No commands in global blacklist'
            embeds = generic_embed(
                title=title,
                desc=desc,
                fields=[],
                footer=current_time(),
                colours=Colours.COMMANDS
            )
            for embed in embeds:
                await ctx.send(embed=embed)

    @blacklistglobalcmd.command(name='add', pass_context=True)
    async def _blgca(self, ctx: commands.Context, cmds: str=None):
        """Add command to global blacklist.

        Parameters
        ----------
        uids: str
            List of id, comma separated

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
                success = await self.bot.pg.add_disallowed_global(cmd)
                if success:
                    added_cmds.append(cmd)
            if added_cmds:
                title = 'Commands added into global blacklist'
                desc = ', '.join(added_cmds)
                embeds = generic_embed(
                    title=title,
                    desc=desc,
                    fields=[],
                    colours=Colours.COMMANDS,
                    footer=current_time()
                )
            else:
                self.bot.logger.info(f'Error adding Commands to global blacklist')
                embed = internalerrorembed(f'Error adding Commands to global blacklist')
                await ctx.send(embed=embed, delete_after=5)
                await respond(ctx, False)
                return
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding Commands to global blacklist {e}')
            embed = internalerrorembed(f'Error adding Commands to global blacklist {e}')
            await ctx.send(embed=embed, delete_after=5)
            await respond(ctx, False)

    @blacklistglobalcmd.command(name='remove', aliases=['rem', 'del', 'rm'])
    async def _blgcr(self, ctx: commands.Context, cmds: str=None):
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
                    success = await self.bot.pg.rem_disallowed_global(cmd)
                    if success:
                        removed_cmds.append(cmd)
                    else:
                        cmds_notfound.append(cmd)
                except ValueError:
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
                                    f'global blacklist: {e}')
            embed = internalerrorembed(f'Issue removing commands from ' +
                                                          f'global blacklist: {e}')
            await ctx.send(embed=embed)

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
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'blacklistuser', only_global=True):
            return
        if ctx.invoked_subcommand is None:
            users = await self.bot.pg.get_all_blacklist_users(ctx.guild.id)
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
                success = await self.bot.pg.add_blacklist_user(ctx.guild.id, user.id)
                self.bot.guild_settings[ctx.guild.id]['blacklist_users'].append(user.id)
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
        msg = uids
        if ',' in msg:
            users = [get_member(ctx, x) for x in msg.split(',')]
        else:
            users = [get_member(ctx, msg)]
        # print(users)
        try:
            for user in flatten(users):
                success = False
                # print('kjas:',user.id)
                try:
                    success = await self.bot.pg.rem_blacklist_user(ctx.guild.id, user.id)
                    if success:
                        self.bot.guild_settings[ctx.guild.id]['blacklist_users'].remove(user.id)
                        removed_users.append(user.mention)
                    else:
                        user_notfound.append(user.mention)
                except:
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
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'blacklistchannel', only_global=True):
            return
        if ctx.invoked_subcommand is None:
            channels = await self.bot.pg.get_all_blacklist_channels(ctx.guild.id)
            channels = [ctx.guild.get_channel(int(g)) for g in channels]
            if isinstance(channels, type(None)):
                channels = []
            else:
                channels = [str(x.id) for x in flatten(channels)]
            if len(channels) > 0:
                desc = '<#'
                desc += '>, <#'.join(map(str, channels))
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
                success = await self.bot.pg.add_blacklist_channel(ctx.guild.id, channel.id)
                if success:
                    self.bot.guild_settings[ctx.guild.id]['blacklist_channels'].append(channel.id)
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
                    success = await self.bot.pg.rem_blacklist_channel(ctx.guild.id, channel.id)
                    if success:
                        removed_channel.append(channel.mention)
                        self.bot.guild_settings[ctx.guild.id]['blacklist_channels'].remove(channel.id)
                    else:
                        channel_notfound.append(channel.mention)
                except ValueError:
                    channel_notfound.append(channel)
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
            await respond(ctx, False)

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
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'blacklistcmd', only_global=True):
            return
        if ctx.invoked_subcommand is None:
            cmds = await self.bot.pg.get_all_disallowed(ctx.guild.id)
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
                success = await self.bot.pg.add_disallowed(ctx.guild.id, cmd)
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
            await respond(ctx, False)

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
                # print(cmd)
                try:
                    success = await self.bot.pg.rem_disallowed(ctx.guild.id, cmd)
                    if success:
                        removed_cmds.append(cmd)
                    else:
                        cmds_notfound.append(cmd)
                except ValueError:
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
            await respond(ctx, False)

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
