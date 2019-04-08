"""."""

# internal modules
import urllib
import aiohttp
import re
import urllib.parse
import random
import math
import datetime

# external modules
import discord
from discord.ext import commands
from discord.utils import snowflake_time
import requests

# relative modules
from cogs.utilities import (Colours, permissions)
from cogs.utilities.functions import (current_time, extract_id,
    get_role, get_member, parse, time_conv, flatten) # noqa
from cogs.utilities.embed_general import generic_embed, MAX_LEN
from cogs.utilities.message_general import generic_message
from cogs.utilities.embed_dialog import respond
from cogs.utilities import embed_errors as eembeds
from cogs.utilities import embed_general as gembed

# global attributes
__all__ = ('General',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(General(bot))
    print('Loaded General')


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    """
    MISC
    """
    @commands.command(aliases=['id', 'snowflake'])
    @commands.guild_only()
    async def snowflakeid(self, ctx, *, argument: str):
        """Add or remove a user to blacklist global list.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'snowflakeid'):
            return
        argument = int(extract_member_id(argument))
        dt = time_conv(snowflake_time(argument))
        await generic_message(ctx, [ctx.channel], f'`{dt}`', -1)

    @commands.group(aliases=['say', 'repeat'])
    @commands.guild_only()
    async def echo(self, ctx, *, message):
        """Echo.

        Parameters
        ----------
        message: str
            Message to echo

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'echo'):
            return
        if ctx.invoked_subcommand is None:
            await ctx.channel.send(f'{message}')

    @echo.command(aliases=['to', 'in'])
    @permissions.is_manager()
    async def channel(self, ctx, channels: str, *, message: str):
        """Send to channel(s).

        Comma separated list of channel mentionables/ids or 
        single channel as first 

        Parameters
        ----------
        channels: str
            channel ids/mentionables comma separated, nospaces
        message: str
            Message to echo

        Returns
        -------
        """
        channels = [extract_channel_id(x) for x in channels.split(',')]
        for channelid in channels:
            try:
                channel = ctx.guild.get_channel(channelid)
                await channel.send(f'{message}')
            except:
                await ctx.channel.send(embed=eembeds.internalerrorembed(f'Channel <#{channelid}> not found!'))
                await respond(ctx, False)
                return

    """
    GENERAL STATS
    """
    @commands.command()
    async def ping(self, ctx):
        """Add or remove a user to blacklist global list.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'ping'):
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
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'stats'):
            return
        now = datetime.datetime.utcnow()
        uptime = time_conv(now - self.bot.uptime)

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
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'guildinfo'):
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
    async def userinfo(self, ctx, *, user: str):
        """Get info on a user.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'userinfo'):
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
        fields.append(['Creation Date', time_conv(user.user.created_at)])
        fields.append(['Joined', time_conv(user.joined_at)])
        fields.append(['Avatar', user.avatar_url])
        embeds = generic_embed(title=title, desc=desc, fields=fields, url=avatar_url, footer=current_time())

        for embed in embeds:
            ctx.send(embed=embed)

    """
    ROLE COMMANDS
    """
    @commands.command(aliases=['ping_role'])
    @permissions.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def pingrole(self, ctx, *, roles: str):
        """Ping roles.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'pingrole'):
            return
        roles = flatten([get_role(ctx, x) for x in roles.split(',')])
        if isinstance(roles, type(None)) or len(roles) == 0:
            await respond(ctx, False)
            return
        roles = [[r, r.mentionable] for r in roles]
        mention_str = ""
        for role in roles:
            await role[0].edit(mentionable=True)
            mention_str += f'{role[0].mention} '
        await ctx.send(mention_str)
        await ctx.message.delete()
        for role in roles:
            await role[0].edit(mentionable=role[1])

    @commands.command(aliases=['roleinfo'])
    @commands.guild_only()
    async def inrole(self, ctx, *, roles: str):
        """Ping roles.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'inrole'):
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

    @commands.group(name='role', aliases=['joinrole', 'rolejoin', 'iam'])
    @commands.guild_only()
    async def _role(self, ctx):
        """Ping roles.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'role'):
            return
        try:
            run = False
            if (ctx.invoked_subcommand is None):
                roles = ' '.join(ctx.message.clean_content.split(' ')[1:])
                run = True
            elif (ctx.subcommand_passed.lower() == 'add'):
                roles = ' '.join(ctx.message.clean_content.split(' ')[2:])
                run = True
            if run:
                roles = flatten([get_role(ctx, role) for role in roles.replace(' ', '').split(',')])
                if isinstance(roles, type(None)) or len(roles) == 0:
                    await ctx.channel.send(embed=eembeds.internalerrorembed(f'Roles: <@&{">,<&".join(roles)}> not found!'), delete_after=5)
                    await respond(ctx, False)
                    return
                base = ctx.author.roles
                base += roles
                await ctx.author.edit(roles=base)
                await respond(ctx, True)
        except Exception as e:
            print('Error adding single joinrole to user:', e)
            await respond(ctx, False)
        pass

    @_role.command(name='add')
    async def _roleadd(self, ctx, *, roles: str):
        """Ping roles.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        pass

    @_role.command(name='remove', aliases=['rm', 'del', 'not'])
    async def _rolerm(self, ctx, *, roles: str):
        """Ping roles.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        try:
            roles = roles.replace(' ', '')
            member = ctx.author
            roles = flatten([get_role(ctx, x) for x in roles.split(',')])
            roles = list(set(member.roles) - set(roles))
            await member.edit(roles=roles)
            await respond(ctx, True)
        except Exception as e:
            print('Error removing:', e)
            await respond(ctx, False)
        pass



if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    test()
    print('Test Passed')

# end of code

# end of file
