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
from cogs.utilities.functions import (current_time, extract_member_id, extract_guild_id, parse)
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.embed_dialog import respond
from cogs.utilities.embed_errors import internalerrorembed

# global attributes
__all__ = ('Owner',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(Owner(bot))
    print('Loaded owner')


class Owner(commands.Cog):
    """Blacklist Global commands."""

    def __init__(self, bot):
        self.bot = bot

    """
    BOT CONFIG
    """
    @commands.command()
    @permissions.is_master()
    async def guildlist(self, ctx):
        """Add or remove a user to blacklist global list.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

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
        ctx: :func: commands.Context
            the context command object

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
    async def config(self, ctx):
        """Display Config.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

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

    @config.command()
    async def guild(self, ctx, *, gid: str=None):
        """Check a specific guild configuration.
        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

        Returns
        -------
        """
        try:
            if not gid:
                gid = extract_guild_id(ctx.message.clean_content)
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
    async def set_playing(self, ctx, *, game: str=None):
        if game:
            await self.bot.change_presence(activity=discord.Game(game))
        await respond(ctx, True)
        pass

    @commands.command(hidden=True)
    @permissions.is_master()
    async def change_username(self, ctx, *, new_username: str):
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

    @commands.command(hidden=True)
    @permissions.is_master()
    async def set_playing(self, ctx, *, game: str=None):
        if game:
            await self.bot.change_presence(activity=discord.Game(game))
        await respond(ctx, True)
        pass

    @commands.command(hidden=True)
    @permissions.is_master()
    async def change_username(self, ctx, *, new_username: str):
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
        ctx: :func: commands.Context
            the context command object

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
    async def _a(self, ctx, uids: str=None):
        """Add user to global blacklist.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        uids: str
            List of id, comma separated

        Returns
        -------
        """
        print(type(ctx))
        added_users = []
        msg = uids.replace(' ', '')
        if ',' in msg:
            users = [extract_member_id(x) for x in msg.split(',')]
        else:
            users = [msg]
        users = [x for x in users if x != '']

        try:
            for user in users:
                success = await self.bot.pg.add_blacklist_user_global(user)
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
                embed = embed_errors.internalerrorembed(f'Error adding users to global blacklist')
                await ctx.send(embed=embed)
                return
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding users to global blacklist {e}')
            embed = embed_errors.internalerrorembed(f'Error adding users to global blacklist {e}')
            await ctx.send(embed=embed)

    @blacklistglobaluser.command(name='remove', aliases=['rem', 'del', 'rm'])
    async def _r(self, ctx, uids: str=None):
        """Removes a user from the blacklist.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        uids: str
            List of id, comma separated

        Returns
        -------
        """
        removed_users = []
        user_notfound = []
        msg = uids.replace(' ', '')
        if ',' in msg:
            users = [extract_member_id(x) for x in msg.split(',')]
        else:
            users = [msg]
        users = [x for x in users if x != '']
        try:
            for user in users:
                success = False
                try:
                    success = await self.bot.pg.rem_blacklist_user_global(user)
                except ValueError:
                    user_notfound.append(user)
                if success:
                    removed_users.append(user)
            fields = []
            if removed_users:
                fields += [['PASS.)', f'<@{x}>'] for x in removed_users]
            if user_notfound:
                fields += [['FAIL.)', f'<@{x}>'] for x in user_notfound]
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
            embed = embed_errors.internalerrorembed(f'Issue removing users from ' +
                                                          f'global blacklist: {e}')
            await ctx.send(embed=embed)

    @commands.group(aliases=['blgg'], pass_context=True)
    @permissions.is_master()
    async def blacklistglobalguild(self, ctx):
        """Add or remove a guild to blacklist global list.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

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
    async def _a(self, ctx):
        """Add guild to global blacklist.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        uids: str
            List of id, comma separated

        Returns
        -------
        """
        print(type(self))
        print(type(ctx))
        print(self.bot.config)
        added_guilds = []
        msg = ctx.message.replace(' ', '')
        if ',' in msg:
            guilds = [extract_guild_id(x) for x in msg.split(',')]
        else:
            guilds = [msg]
        guilds = [x for x in guilds if x != '']

        try:
            for guild in guilds:
                success = await self.bot.pg.add_blacklist_guild_global(guild)
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
                embed = embed_errors.internalerrorembed(f'Error adding guilds to global blacklist')
                await ctx.send(embed=embed)
                return
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding guilds to global blacklist {e}')
            embed = embed_errors.internalerrorembed(f'Error adding guilds to global blacklist {e}')
            await ctx.send(embed=embed)

    @blacklistglobalguild.command(name='remove', aliases=['rem', 'del', 'rm'])
    async def _r(self, ctx, gids: str=None):
        """Removes a guild from the blacklist.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        gids: str
            List of id, comma separated

        Returns
        -------
        """
        removed_guilds = []
        guild_notfound = []
        msg = gids.replace(' ', '')
        if ',' in msg:
            guilds = [extract_guild_id(x) for x in msg.split(',')]
        else:
            guilds = [msg]
        guilds = [x for x in guilds if x != '']
        try:
            for guild in guilds:
                success = False
                try:
                    success = await self.bot.pg.rem_blacklist_user_global(guild)
                except ValueError:
                    guild_notfound.append(guild)
                if success:
                    removed_guilds.append(guild)
            fields = []
            if removed_guilds:
                fields += [['PASS.)', f'<@{x}>'] for x in removed_guilds]
            if guild_notfound:
                fields += [['FAIL.)', f'<@{x}>'] for x in guild_notfound]
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
            self.bot.logger.warning(f'Issue removing guilds from ' +
                                    f'global blacklist: {e}')
            embed = embed_errors.internalerrorembed(f'Issue removing guilds from ' +
                                                          f'global blacklist: {e}')
            await ctx.send(embed=embed)

    @commands.group(aliases=['globalcommands', 'blgc'], pass_context=True)
    @permissions.is_master()
    async def commandsglobal(self, ctx):
        """Add or remove a command to blacklist global list.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

        Returns
        -------
        """
        if ctx.invoked_subcommand is None:
            cmds = await self.bot.pg.get_all_disallowed_global()
            if isinstance(cmds, type(None)):
                cmds = []
            if len(cmds) > 0:
                title = 'Commands blacklisted globally'
                desc = ', '.join(users)
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

    @commandsglobal.command(name='add', pass_context=True)
    async def _a(self, ctx, cmds: str=None):
        """Add command to global blacklist.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        uids: str
            List of id, comma separated

        Returns
        -------
        """
        added_cmds = []
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
                desc += ', '.join(added_cmds)
                embeds = generic_embed(
                    title=title,
                    desc=desc,
                    fields=[],
                    colours=Colours.COMMANDS,
                    footer=current_time()
                )
            else:
                self.bot.logger.info(f'Error adding Commands to global blacklist')
                embed = embed_errors.internalerrorembed(f'Error adding Commands to global blacklist')
                await ctx.send(embed=embed)
                return
            for embed in embeds:
                await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding Commands to global blacklist {e}')
            embed = embed_errors.internalerrorembed(f'Error adding Commands to global blacklist {e}')
            await ctx.send(embed=embed)

    @commandsglobal.command(name='remove', aliases=['rem', 'del', 'rm'])
    async def _r(self, ctx, cmds: str=None):
        """Removes a command from the blacklist.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        cmds: str
            List of cmds, comma separated

        Returns
        -------
        """
        removed_cmds = []
        cmds_notfound = []
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
                except ValueError:
                    user_notfound.append(cmd)
                if success:
                    removed_cmds.append(cmd)
            fields = []
            if removed_cmds:
                fields += [['PASS.)', f'{x}'] for x in removed_cmds]
            if user_notfound:
                fields += [['FAIL.)', f'{x}'] for x in cmds_notfound]
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
            embed = embed_errors.internalerrorembed(f'Issue removing commands from ' +
                                                          f'global blacklist: {e}')
            await ctx.send(embed=embed)


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
