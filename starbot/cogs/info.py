"""."""

# internal modules
import datetime

# external modules
import discord
from discord.ext import commands
from discord.utils import snowflake_time

# relative modules
from cogs.utilities import (Colours, permissions)
from cogs.utilities.functions import (current_time,
    get_role, get_member, parse, time_conv) # noqa
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.message_general import generic_message
from cogs.utilities.embed_dialog import respond
from cogs.utilities import embed_errors as eembeds

# global attributes
__all__ = ('Info',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(Info(bot))
    print('Loaded Info')


class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    """
    PERMISSIONS
    """
    @commands.command(name='permissions', aliases=['perms', 'permission'])
    @commands.guild_only()
    async def _perms(self, ctx: commands.Context, *, user: str=None):
        """Get your permissions.

        If you have > manage role perms then you can
        get the permissions level of other users.

        Parameters
        ----------
        user: str
            Optional parameter of a user

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'permissions'):
            return
        if not user:
            target = ctx.author
        else:
            if not ctx.channel.permissions_for(ctx.author).manage_roles:
                embed = eembeds.userpermissionerrorembed('permissions [user]. Use the normal permission command', 'manage_roles')
                await ctx.send(embed=embed, delete_after=5)
                await respond(ctx, False)
                return
            else:
                target = get_member(ctx, user)
        perms = ctx.channel.permissions_for(target)
        perms = list(map(lambda x: str(x).upper() + '`', [': `'.join(map(str, x)) for x in perms]))
        title = f'Permissions for {target.name}: {target.id}\n'
        desc = 'User is bot Owner/Dev\n' if (str(target.id) == self.bot.config.owner_id.value) or (str(target.id) == self.bot.config.devel_id.value) else ''
        desc += 'User is guild owner\n' if (str(target.id) == str(ctx.guild.owner.id)) else ''
        desc += '\n'
        fields = "\n".join(perms)
        await generic_message(ctx, [ctx.channel], f'{title}{desc}{fields}\n\n{current_time()}', -1)
        return


    @commands.command(aliases=['id', 'snowflake'])
    @commands.guild_only()
    async def snowflakeid(self, ctx: commands.Context, *, argument: str):
        """Add or remove a user to blacklist global list.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'snowflakeid'):
            return
        argument = int(extract_member_id(argument))
        dt = time_conv(snowflake_time(argument))
        await generic_message(ctx, [ctx.channel], f'`{dt}`', -1)

    """
    GENERAL STATS
    """
    @commands.command()
    async def ping(self, ctx):
        """Ping the bot.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'ping'):
            return
        latency = self.bot.latency * 1000
        embedping = generic_embed(title="Ping!",
            fields=[[f"🏓 Latency", latency]],
            desc="Ping the bot!",
            color=Colours.COMMANDS)[0]
        await ctx.send(embed=embedping)


    @commands.command(aliases=['botstats', 'botinfo', 'support', 'botinvite', 'invitebot'])
    @commands.guild_only()
    async def stats(self, ctx):
        """Prints out general stats/links for the bot.

        Parameters
        ----------

        Returns
        ----------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'stats'):
            return
        now = datetime.datetime.utcnow()
        uptime = time_conv(now - self.bot.start_time)

        glist = self.bot.guilds
        all_u = self.bot.users
        bot = len([u for u in all_u if u.bot])
        fields = []
        v = (self.bot.config.githash.value, self.bot.config.version.value)

        # Guild Info
        fields.append(['Guild Count', len(glist)])
        fields.append(['User Count', f'{len(all_u)}({bot}bots)'])
        fields.append(['Bot Invite', f'[Invite link Click!]({self.bot.config.bot_key.value}) to invite {ctx.guild.me.mention} to your server!'])
        fields.append(['Support invite', f'[Invite link Click!]({self.bot.config.support_server.value}) to join the bot {ctx.guild.me.mention}\'s support server!'])
        fields.append(['Github', f'[External link Click!]({self.bot.config.github.value}) to view the bot {ctx.guild.me.mention}\'s GitHub repo!'])
        fields.append(['Uptime', uptime])
        fields.append(['Version', v[1]])
        fields.append(['GitHash', v[0]])

        embeds = generic_embed(
            title=f'Bot Stats',
            desc='',
            fields=fields,
            footer=current_time()
        )
        for embed in embeds:
            await ctx.send(embed=embed)

    @commands.command(aliases=['server_info', 'guild_info', 'serverinfo'])
    @commands.guild_only()
    async def guildinfo(self, ctx):
        """Show server information."""
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'guildinfo'):
            return
        guild = ctx.guild
        online = len([m.status for m in guild.members if m.status != discord.Status.offline])
        total_users = len(guild.members)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        passed = ctx.message.created_at - guild.created_at
        created_at = f"This guild has been around for {time_conv(passed)}!"
        fields = []
        title = 'Info on: ' + guild.name
        fields.append(["Region", str(guild.region)])
        fields.append(["Users", f"{online}/{total_users}"])
        fields.append(["Text Channels", str(text_channels)])
        fields.append(["Voice Channels", str(voice_channels)])
        fields.append(["Roles", str(len(guild.roles))])
        fields.append(["Owner", str(guild.owner.mention)])
        fields.append(["Server ID", str(guild.id)])
        fields.append(["Created", guild.created_at])

        if guild.icon_url:
            embeds = generic_embed(title=title, desc=created_at, fields=fields, footer=current_time(), url=guild.icon_url)
        else:
            embeds = generic_embed(title=title, desc=created_at, fields=fields, footer=current_time())

        for embed in embeds:
            await ctx.send(embed=embed)

    @commands.command(aliases=['getuser'])
    @commands.guild_only()
    async def userinfo(self, ctx: commands.Context, *, user: str):
        """Get info on a user.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'userinfo'):
            return
        user = get_member(ctx, user)
        if not user:
            await respond(ctx, False)
            return
        title = f'User info for: {user.mention}'
        desc = ''
        fields = []
        fields.append(['User\'s Username', user.name])
        fields.append(['User\'s Nickname', user.nick])
        fields.append(['User\'s Discrim', user.discriminator])
        fields.append(['UserId', user.id])
        fields.append(['Roles', ', '.join([x.name for x in user.roles])])
        fields.append(['Creation Date', time_conv(user.created_at)])
        fields.append(['Joined', time_conv(user.joined_at)])
        fields.append(['Avatar', str(user.avatar_url)])
        embeds = generic_embed(title=title, desc=desc, fields=fields, thumbnail=str(user.avatar_url), footer=current_time())

        for embed in embeds:
            await ctx.send(embed=embed)

    @commands.command(aliases=['roleinfo'])
    @commands.guild_only()
    async def inrole(self, ctx: commands.Context, *, roles: str):
        """Ping roles.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'inrole'):
            return
        role = get_role(ctx, roles)
        if isinstance(role, type(None)):
            await respond(ctx, False)
            return
        try:
            if await self.bot.pg.is_single_joininfo(ctx.guild.id, role.id):
                t = await self.bot.pg.get_single_joininfo(ctx.guild.id, role.id, self.bot.logger)
                desc = f'Info about the role:\n{parse(t)[0][-2][1]}'
            else:
                desc = ''
            embeds = generic_embed(
                title=f'Users in role: {role.name}',
                desc=desc,
                fields=[['Users', ', '.join([x.mention for x in role.members])]],
                footer=current_time())
        except Exception as e:
            self.bot.logger.info(f'Error getting role info: {e}')
            print(f'Error getting role info: {e}')
            await respond(ctx, False)
            return
        for embed in embeds:
            await ctx.send(embed=embed)
            return


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    test()
    print('Test Passed')

# end of code

# end of file
