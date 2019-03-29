"""."""

# internal modules

# external modules
import discord
from discord.ext import commands

# relative modules
from cogs.utilities import Colours, generic_embed, current_time, extract_member_id, extract_guild_id

# global attributes
__all__ = ('BlackListGlobal',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class BlackListGlobal():
    """Blacklist Global commands."""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.group(aliases=['blgu'])
    @checks.is_master()
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
            users = await self.bot.pg_utils.get_all_blacklist_users_global()
            if len(users) > 0:
                title = 'Users in global blacklist'
                desc = '<@'
                desc += '>, <@'.join(users)
                desc += '>'
            else:
                desc = ''
                title = 'No users in global blacklist'
            embed = generic_embed(
                title=title,
                desc=desc,
                fields=[],
                footer=current_time(),
                colours=Colours.COMMANDS
            )
            await ctx.send(embed=embed)

    @blacklistglobaluser.command()
    async def add(self, ctx):
        """Add user to global blacklist.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

        Returns
        -------
        """
        added_users = []
        msg = ctx.clean_content.replace(' ', '')
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
                embed = generic_embed(
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
        except Exception as e:
            self.bot.logger.info(f'Error adding users to global blacklist {e}')
            embed = embed_errors.internalerrorembed(f'Error adding users to global blacklist {e}')
            await ctx.send(embed=embed)

    @blacklistglobaluser.command(aliases=['rem', 'del', 'rm'])
    async def remove(self, ctx):
        """Removes a user from the blacklist."""
        removed_users = []
        user_notfound = []
        msg = ctx.clean_content.replace(' ', '')
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
            embed = generic_embed(
                title=title,
                desc=desc,
                fields=fields,
                colours=Colours.COMMANDS,
                footer=current_time()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue removing users from ' +
                                    f'global blacklist: {e}')
            embed = embed_errors.internalerrorembed(f'Issue removing users from ' +
                                                          f'global blacklist: {e}')
            await ctx.send(embed=embed)


    @commands.group(aliases=['blgg'])
    @checks.is_master()
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
            guilds = await self.bot.pg_utils.get_all_blacklist_guild_global()
            if len(guilds) > 0:
                title = 'Guilds in global blacklist'
                desc = '<'
                desc += '>, <'.join(guilds)
                desc += '>'
            else:
                desc = ''
                title = 'No guilds in global blacklist'
            embed = generic_embed(
                title=title,
                desc=desc,
                fields=[],
                footer=current_time(),
                colours=Colours.COMMANDS
            )
            await ctx.send(embed=embed)

    @blacklistglobalguild.command()
    async def add(self, ctx):
        """Add guild to global blacklist.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object

        Returns
        -------
        """
        added_guilds = []
        msg = ctx.clean_content.replace(' ', '')
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
                embed = generic_embed(
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
        except Exception as e:
            self.bot.logger.info(f'Error adding guilds to global blacklist {e}')
            embed = embed_errors.internalerrorembed(f'Error adding guilds to global blacklist {e}')
            await ctx.send(embed=embed)

    @blacklistglobalguilds.command(aliases=['rem', 'del', 'rm'])
    async def remove(self, ctx):
        """Removes a guild from the blacklist."""
        removed_guilds = []
        guild_notfound = []
        msg = ctx.clean_content.replace(' ', '')
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
            embed = generic_embed(
                title=title,
                desc=desc,
                fields=fields,
                colours=Colours.COMMANDS,
                footer=current_time()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue removing guilds from ' +
                                    f'global blacklist: {e}')
            embed = embed_errors.internalerrorembed(f'Issue removing guilds from ' +
                                                          f'global blacklist: {e}')
            await ctx.send(embed=embed)

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
