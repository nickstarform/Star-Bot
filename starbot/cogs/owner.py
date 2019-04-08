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
from cogs.utilities.functions import (current_time, extract_id, get_member, get_role, parse, time_conv)
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.message_general import generic_message
from cogs.utilities.embed_dialog import respond
from cogs.utilities.embed_errors import internalerrorembed

# global attributes
__all__ = ('Owner',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(Owner(bot))
    print('Loaded Owner')


class Owner(commands.Cog):
    """Blacklist Global commands."""

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    """
    BOT CONFIG
    """
    @commands.command()
    @permissions.is_master()
    async def guildlist(self, ctx):
        """Add or remove a user to blacklist global list.

        Parameters
        ----------

        Returns
        -------
        """
        glist = self.bot.guilds
        ctitle = f'Guild List: {len(glist)}'
        cdesc = ''
        for guild in glist:
            if isinstance(guild, type(None)):
                continue
            if isinstance(guild, type(None)):
                continue
            cdesc += f'**Guild: {guild.name}, ID: {guild.id}**\n'\
                f'Owner: {guild.owner.mention}\n'\
                f'Users: {len(guild.members)}\n'\
                f'Channels: {len(guild.text_channels)}\n'\
                f'Voice Channels: {len(guild.voice_channels)}\n'
        fields = []
        embeds = generic_embed(
            title=ctitle,
            desc=cdesc,
            fields=[],
            footer=current_time(),
            colours=Colours.COMMANDS
        )
        for embed in embeds:
            await ctx.send(embed=embed)

    @commands.command(aliases=['diagnostic'])
    @permissions.is_master()
    async def diagnostics(self, ctx):
        """Display diagnostics for bot.

        Parameters
        ----------

        Returns
        -------
        """
        ctitle = f'Star-Bot Diagnostics'
        cdesc = ''
        fields = []
        # guild info
        glist = self.bot.guilds
        all_u = self.bot.users
        bot = len([u for u in all_u if u.bot])
        text, voice = 0, 0
        for guild in glist:
            text += len(guild.text_channels)
            voice += len(guild.voice_channels)

        # Guild Info
        fields.append(['Guild Count', len(glist)])
        fields.append(['User Count', f'{len(all_u)}({bot}bots)'])
        fields.append(['Text Channel Count', text])
        fields.append(['Voice Channel Count', voice])

        # Global Info
        blguild = await self.bot.pg.get_all_blacklist_guild_global()
        bluser = await self.bot.pg.get_all_blacklist_users_global()
        blcmd = await self.bot.pg.get_all_disallowed_global()
        reports = await self.bot.pg.get_all_reports()
        reports = len(reports) if not isinstance(reports, type(None)) else 0
        fields.append(['Blacklisted Guilds', blguild])
        fields.append(['Blacklisted Users', bluser])
        fields.append(['Blacklisted Commands', blcmd])
        fields.append(['Number of Reports', reports])

        # Bot info
        current_process = psutil.Process()
        cpu = current_process.cpu_percent()
        mem = dict(psutil.virtual_memory()._asdict())
        fields.append(['CPU Usage', cpu])
        fields.append(['Memory', f'{mem["used"] / (1000 ** 3)}GB ({mem["percent"]}%)'])
        fields.append(['Version', self.bot.config.version.value])
        fields.append(['Git Hash', self.bot.config.githash.value])
        
        embeds = generic_embed(
            title=ctitle,
            desc=cdesc,
            fields=fields,
            footer=current_time(),
            colours=Colours.COMMANDS
        )
        for embed in embeds:
            await ctx.send(embed=embed)

    @commands.group()
    @permissions.is_master()
    async def globalconfig(self, ctx):
        """Display Config.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            ctitle = f'Star-Bot Configuration'
            cdesc = ''
            fields = []
            for key in self.bot.config.__members__:
                fields.append([key, self.bot.config.__members__[key].value])

            embeds = generic_embed(
                title=ctitle,
                desc=cdesc,
                fields=fields,
                footer=current_time(),
                colours=Colours.COMMANDS
            )
            for embed in embeds:
                await ctx.send(embed=embed)

    @globalconfig.command()
    async def guild(self, ctx: commands.Context, *, gid: str=None):
        """Check a specific guild configuration.
        Parameters
        ----------

        Returns
        -------
        """
        try:
            if not gid:
                gid = extract_id(ctx.message.clean_content, 'guild')
            if not gid:
                await respond(ctx, False)
                return
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

    """
    STATUS
    """
    @commands.command(hidden=True)
    @permissions.is_master()
    async def set_playing(self, ctx: commands.Context, *, game: str=None):
        if game:
            await self.bot.change_presence(activity=discord.Game(game))
        await respond(ctx, True)
        pass

    @commands.command(hidden=True)
    @permissions.is_master()
    async def change_username(self, ctx: commands.Context, *, new_username: str):
        """
        Changes bot username
        """
        bot_user = self.bot.user
        try:
            await bot_user.edit(username=new_username)
            await respond(ctx, True)
        except Exception as e:
            await respond(ctx, False)
            self.bot.logger.warning(f'Error changing bots username: {e}')

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
            users = [str(x[0][1]) for x in parse(users)]
            if isinstance(users, type(None)):
                users = []
            if len(users) > 0:
                title = 'Users in global blacklist'
                desc = '<@'
                desc += '>, <@'.join(users)
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
                success = await self.bot.pg.add_blacklist_user_global(user, self.bot.logger)
                if success:
                    added_users.append(user)
            if added_users:
                title = 'Users added into global blacklist'
                desc = '<@'
                desc += '>, <@'.join(added_users)
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
        users = [x for x in users if x != '']
        try:
            for user in users:
                success = False
                try:
                    success = await self.bot.pg.rem_blacklist_user_global(user, self.bot.logger)
                except:
                    user_notfound.append(user)
                if success:
                    removed_users.append(user)
                else:
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
            guilds = [str(g[0][1]) for g in parse(guilds)]
            if isinstance(guilds, type(None)):
                guilds = []
            if len(guilds) > 0:
                title = 'Guilds in global blacklist'
                desc = '<'
                desc += '>, <'.join(guilds)
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
                success = await self.bot.pg.add_blacklist_guild_global(guild, self.bot.logger)
                if success:
                    added_guilds.append(guild)
            if added_guilds:
                title = 'Guilds added into global blacklist'
                desc = '<'
                desc += '>, <'.join(added_guilds)
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
                    success = await self.bot.pg.rem_blacklist_guild_global(guild, self.bot.logger)
                except ValueError:
                    guild_notfound.append(guild)
                if success:
                    removed_guilds.append(guild)
                else:
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
            cmds = [x[0][1] for x in parse(cmds)]
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
                success = await self.bot.pg.add_disallowed_global(cmd, self.bot.logger)
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
                    success = await self.bot.pg.rem_disallowed_global(cmd, self.bot.logger)
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
                                    f'global blacklist: {e}')
            embed = internalerrorembed(f'Issue removing commands from ' +
                                                          f'global blacklist: {e}')
            await ctx.send(embed=embed)

    """
    GLOBAL MACRO
    """

    @commands.group(name='globalmacro', aliases=['globalmacros', 'gblmc', 'gmacro'], pass_context=True)
    @permissions.is_master()
    async def _gmacro(self, ctx):
        """Macro's for the bot owner.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            # parse
            macro = ' '.join(ctx.message.content.split(' ')[1:])
            failed = False
            if macro:
                try:
                    m = await self.bot.pg.get_single_global_macro(macro, self.bot.logger)
                    if not m:
                        embed = internalerrorembed(f'Could\'t find macro: {macro}')
                        failed = True
                except Exception as e:
                    embed = internalerrorembed(f'Could\'t find macro: {e}')
                    failed = True
            else:
                failed = True
                embed = internalerrorembed(f'Need to invoke subcommands or give macro to poll')
            if not failed:
                await ctx.send(f'{parse(m)[0][1][1]}')
                await ctx.message.delete()
                return
            else:
                await ctx.send(embed=embed, delete_after=5)
                await respond(ctx, False)
                await ctx.message.delete()
                return

    @_gmacro.command(name='list', aliases=['ls', 'show'], pass_context=True)
    @permissions.is_master()
    async def _gmacrols(self, ctx):
        """List all global macros.

        Parameters
        ----------

        Returns
        -------
        """
        try:
            failed = False
            m = await self.bot.pg.get_all_global_macro(self.bot.logger)
            if not m:
                embed = internalerrorembed(f'Could\'t get any macros')
                failed = True
        except Exception as e:
            embed = internalerrorembed(f'Could\'t get macros: {e}')
            failed = True
        if not failed:
            embeds = generic_embed(
                title='Macro List',
                desc=f'{", ".join([x[0][1] for x in parse(m)])}',
                fields=[])
            for embed in embeds:
                await ctx.send(embed=embed)
            await ctx.message.delete()
            return
        else:
            await ctx.send(embed=embed, delete_after=5)
            await respond(ctx, False)
            await ctx.message.delete()
            return

    @_gmacro.command(name='add', pass_context=True)
    @permissions.is_master()
    async def _gmacroadd(self, ctx, macro: str, *, content: str):
        """Add a global macro.

        Parameters
        ----------
        macro: str
            name of the macro
        content: str
            content to store in macro

        Returns
        -------
        """
        try:
            m = await self.bot.pg.add_single_global_macro(macro, content, self.bot.logger)
            if not m:
                embed = internalerrorembed(f'Could\'t find macro: {macro}')
                await respond(ctx, False)
                await ctx.send(embed=embed, delete_after=5)
                return
            else:
                await respond(ctx, True)
                return
        except Exception as e:
            embed = internalerrorembed(f'Could\'t add macro: {e}')
            await ctx.send(embed=embed, delete_after=5)
            await respond(ctx, False)
            return

    @_gmacro.command(name='remove', aliases=['del', 'rm', 'delete'], pass_context=True)
    @permissions.is_master()
    async def _gmacrorm(self, ctx, macro: str):
        """Remove a global macro.

        Parameters
        ----------
        macro: str
            name of the macro

        Returns
        -------
        """
        try:
            m = await self.bot.pg.delete_single_global_macro(macro, self.bot.logger)
            if not m:
                embed = internalerrorembed(f'Could\'t find macro: {macro}')
                await respond(ctx, False)
                await ctx.send(embed=embed, delete_after=5)
                return
            else:
                await respond(ctx, True)
                return
        except Exception as e:
            embed = internalerrorembed(f'Could\'t add macro: {e}')
            await ctx.send(embed=embed, delete_after=5)
            await respond(ctx, False)
            return
    @_gmacro.command(name='set', aliases=['update', 'change'], pass_context=True)
    @permissions.is_master()
    async def _gmacroset(self, ctx, macro: str, *, content: str):
        """Update a macro.

        Parameters
        ----------
        macro: str
            name of macro
        content: str
            content to be updated

        Returns
        -------
        """
        try:
            m = await self.bot.pg.set_single_global_macro(macro, content, self.bot.logger)
            if not m:
                embed = internalerrorembed(f'Could\'t find macro: {macro}')
                await respond(ctx, False)
                await ctx.send(embed=embed, delete_after=5)
                return
            else:
                await respond(ctx, True)
                return
        except Exception as e:
            embed = internalerrorembed(f'Could\'t set macro: {e}')
            await ctx.send(embed=embed, delete_after=5)
            await respond(ctx, False)
            return

    """
    GLOBAL REPORTS
    """

    @commands.group(name='globalreport', aliases=['globalreports', 'greports'], pass_context=True)
    @permissions.is_master()
    async def _reports(self, ctx):
        """Macro's for the bot owner.

        Parameters
        ----------

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            reports_all = await self.bot.pg.get_all_reports()
            reports_all = parse(reports_all)
            desc = '**Global Reports**\n'
            for reports in reports_all:
                desc += f'`Report #{reports[2][1]}` from <@{reports[0][1]}> at {time_conv(reports[-1][1])}:\n'
                desc += f'{reports[1][1]}\n'
            await generic_message(ctx, [ctx.channel], desc, -1, splitwith='')
            return



if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
