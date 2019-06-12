"""."""

# internal modules
import psutil

# external modules
import discord
from discord.ext import commands
import asyncio

# relative modules
from cogs.utilities import (Colours, permissions)
from cogs.utilities.functions import (current_time, extract_id, parse, time_conv)
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.message_general import generic_message
from cogs.utilities.embed_dialog import respond, confirm
from cogs.utilities.embed_errors import internalerrorembed
from config import Config

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
        print(blguild, bluser, blcmd)
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
        print(mem)
        tmem = self.bot.proc.memory_full_info().uss / 1024 ** 2
        cpu = self.bot.proc.cpu_percent() / psutil.cpu_count()
        fields.append(['CPU Usage', cpu])
        fields.append(['Memory', f'PS {mem["used"] / (1000 ** 3)}GB ({mem["percent"]}%) vs Proc {tmem}%'])
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

    @commands.group(aliases=['gconfig', 'gconfigure'])
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

    @globalconfig.command(name='reload', aliases=['refresh'])
    @permissions.is_master()
    async def _gconfigreload(self, ctx):
        """Display Config.

        Parameters
        ----------

        Returns
        -------
        """
        self.bot.logger.info(f'Old configuration: {self.bot.config.__members__}')
        self.bot.config = Config
        self.bot.logger.info(f'New configuration: {self.bot.config.__members__}')
        await respond(ctx, True)
        return

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
            print('config', config, )
            config = parse(config)
            guild = self.bot.get_guild(int(gid))
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
            print('built embed')
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Problem checking guild config: {e}'), delete_after=15)
            await respond(ctx, False)
            self.bot.logger.warning(f'Error trying to return guild config: {e}')

    @globalconfig.command()
    async def guildremove(self, ctx: commands.Context, *, gid: str=None):
        """Remove a guild from the db.

        Parameters
        ----------

        Returns
        -------
        """
        try:
            if not gid:
                gid = str(ctx.guild.id)
            else:
                gid = extract_id(gid, 'guild')
            if not gid:
                await respond(ctx, False)
                raise Exception('gid not defined.... maybe in dm or incorrect guild id')
            guild = self.bot.get_guild(int(gid))
            if isinstance(guild, type(None)):
                raise Exception('Couldn\'t find guild')
            if not await confirm(ctx, f'Do you want to reset {guild.name} <{gid}> [<@{guild.owner.id}>] guild config?', 10):
                return
            if not await self.bot.pg.drop_guild(guild.id, self.bot.logger):
                raise Exception('Couldn\'t drop the guild')
            await ctx.send(f'Successfully removed guild <{guild.name}>.')
            await respond(ctx, True)
            return

        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Problem reseting guild config: {e}'), delete_after=15)
            await respond(ctx, False)
            self.bot.logger.warning(f'Error trying to reset guild config: {e}')
            return

    @globalconfig.command(aliases=['guildchange'])
    async def changeguild(self, ctx: commands.Context, gid: str, key: str, *, val: str):
        """Change a specific guild configuration.

        This is fine tuned and MUST match the exact specifications
        size of a record row for schema.guild. If it is unable to match
        it will not change that value and continue.

        Parameters
        ----------
        guild_id: str
            guild id
        key: str:
            the exact col name
        value: str
            the value to input to

        Returns
        -------
        """
        # gather guild
        try:
            gid = extract_id(gid, 'guild')
            guild = self.bot.get_guild(int(gid))
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Problem checking guild config: {e}'), delete_after=5)
            await respond(ctx, False)
            self.bot.logger.warning(f'Error trying to return guild config: {e}')
            return
        # get values at first
        try:
            old = await self.bot.pg.get_single_record(gid, key, self.bot.logger)
            # verify change
            if not await confirm(ctx, f'Do you want to change {guild.name} <{gid}> [<@{guild.owner.id}>] guild config of {key} from {old} to {val}?', 10):
                return
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Problem checking guild config: {e}'), delete_after=5)
            await respond(ctx, False)
            self.bot.logger.warning(f'Error trying to return guild config: {e}')
            return
        # now set values
        try:
            success = await self.bot.pg.set_single_record(gid, key, val, self.bot.logger)
            if not success:
                await ctx.send(embed=internalerrorembed(f'Couldnt set guild config.'), delete_after=5)
                await respond(ctx, False)
                return
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Problem setting guild config: {e}'), delete_after=5)
            await respond(ctx, False)
            self.bot.logger.warning(f'Error trying to setting guild config: {e}')
            return
        try:
            await ctx.send(f'Changed {gid} guild config', delete_after=15)
            await respond(ctx, True)
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Problem return guild config: {e}'), delete_after=5)
            await respond(ctx, False)
            self.bot.logger.warning(f'Error trying to return guild config: {e}')
        return

    """
    STATUS
    """
    @commands.command()
    @permissions.is_master()
    async def set_playing(self, ctx: commands.Context, *, game: str=None):
        if game:
            await self.bot.change_presence(activity=discord.Game(game))
        await respond(ctx, True)
        pass

    @commands.command()
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
            if len(reports_all) == 0:
                desc = 'No global reports'
            await generic_message(ctx, [ctx.channel], desc, -1, splitwith='')
            return


    @commands.command(name='addguild', aliases=['guildadd'], hidden=True)
    @commands.is_owner()
    async def _add_guild(self, ctx, gid: str=None):
        """Manually add guild to db.

        Parameters
        ----------

        Returns
        -------
        """
        if not isinstance(gid, type(None)):
            guild = extract_id(gid, 'guild')
            if isinstance(guild, type(None)):
                guild = ctx.guild.id
        else:
            guild = ctx.guild.id
        try:
            await self.bot.pg.add_guild(guild)
            config = await self.bot.pg.get_single_guild_settings(guild)
            self.bot.guild_settings[guild] = config
            await respond(ctx, True)
            return
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Error adding guild to db: {e}'))
            await respond(ctx, False)
            self.bot.logger.warning(f'Error adding guild to db: {e}')
            return

    @commands.command(name='restart', aliases=['reboot',])
    @commands.is_owner()
    async def do_restart(self, ctx):
        embed = discord.Embed(description='📡**`- Initialising...`**📡', colour=0xab00c5)
        msg = await ctx.send(embed=embed)

        await asyncio.sleep(2)

        embed.description = '🛑**`- Offline...`**🛑'
        embed._colour = discord.Colour(0xc12400)
        await msg.edit(embed=embed)
        raise KeyboardInterrupt

    @commands.command(name='logout', aliases=['turnoff', 'poweroff'])
    @commands.is_owner()
    async def shutdown(bot, *, reason=None):
        """Somewhat clean shutdown with basic debug info."""
        await bot.logout()

        print(f'\n\nShutting down due to {type(reason).__name__}...\n{"="*30}\n')
        print(f'{datetime.datetime.utcnow()} || UTC\n\nPython: {sys.version}\nPlatform: {sys.platform}/{os.name}\n'
              f'Discord: {discord.__version__}\n\n{"="*30}\n')

        await asyncio.sleep(1)
        if isinstance(reason, KeyboardInterrupt):
            sys.exit(1)  # Systemd will think it failed and restart our service cleanly.
        sys.exit(0)


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
