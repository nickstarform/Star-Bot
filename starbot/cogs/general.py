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
from cogs.utilities.embed_mod import guildreport

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
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'permissions'):
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

    """
    ADDING REPORT FUNCTION
    """
    @commands.command(name='report', aliases=['reportmessage', 'reportthis'])
    @commands.guild_only()
    async def _report(self, ctx: commands.Context):
        """Report the most recent message to the modteam.

        Will report the most recent message before this one.
        Deletes your message and will attempt to DM you with
        the report. Will also do, in order until 1 works,
        report to Mod Channel (if set), report to server_owner,
        or report to bot owner. Abusing this command will get
        you/your guild banned from the bot permanently.

        You can also DM the bot with this command to report
        something. Follow this format please:
        >report [guild_id optional] stuff to report

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'report'):
            return
        rchan = await self.bot.pg.get_report_channel(ctx.guild.id, self.bot.logger)
        guild_owner = ctx.guild.owner

        report = []
        async for message in ctx.channel.history(limit=3, before=ctx.message):
            report.append(message)
        being_reported = [m.author for m in report]
        embeds = guildreport(ctx, ctx.message.author,
                             being_reported,
                             ctx.message.content, report)
        try:
            t = "\n".join([": ".join([r.author.mention, r.content]) for r in report])
            await self.bot.pg.add_report(ctx.author.id, f'FromUser: <@{ctx.author.id}>, Messages:\n{t}', self.bot.logger)  # noqa
        except Exception as e:
            self.bot.logger.warning(f'Error adding report: {e}')
            print(e)
            pass
        for embed in embeds:
            fail = False
            if (rchan is not None) and (int(rchan) > 1E15):
                try:
                    (ctx.guild.get_channel(int(rchan))).send(embed=embed)
                except Exception as e:
                    self.bot.logger.warning(f'Error sending report to {rchan}: {e}')
                    fail = True
            elif guild_owner is not None:
                try:
                    if not guild_owner.dm_channel:
                        await guild_owner.create_dm()
                    await guild_owner.dm_channel.send(embed=embed)
                except Exception as e:
                    self.bot.logger.warning(f'Error sending report to {guild_owner.id}: {e}')
                    fail = True
            else:
                try:
                    owner = self.bot.get_user(self.bot.config.owner_id.value)
                    if not owner.dm_channel:
                        await owner.create_dm()
                    await owner.dm_channel.send(embed=embed)
                except Exception as e:
                    self.bot.logger.warning(f'Error sending report to {owner.id}: {e}')
                    fail = True
            try:
                if not ctx.author.dm_channel:
                    await ctx.author.create_dm()
                await ctx.author.dm_channel.send(embed=embed)
            except Exception as e:
                self.bot.logger.warning(f'Error sending report to {ctx.author.id}: {e}')
        try:
            if not ctx.author.dm_channel:
                await ctx.author.create_dm()
            await ctx.author.dm_channel.send(f'Sent in the report. Please be patient. Abusing this function will get you/your guild banned. {current_time()}')
        except Exception as e:
            self.bot.logger.warning(f'Error sending report to {ctx.author.id}: {e}')
        await ctx.message.delete()
        pass

    """
    ADD SUGGEST FUNCTION
    """
    @commands.command(aliases=['suggestion', 'wishlist', 'features'])
    async def suggest(self, ctx: commands.Context, *, suggestions: str):
        """Send a suggestion to the bot owner.

        Will attempt to send a suggestion to first the bot
        support server (if set) or the bot owner.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'suggest'):
            return
        # check if DM
        pass

    """
    MISC
    """
    @commands.command()
    @commands.guild_only()
    async def remindme(self, ctx: commands.Context, *, argument: str):
        """Set a reminder for yourself or in the channel.

        Take the following time string or any combination
        thereof:
            `1y1mo1w1d1h1m1s`
        If cannot parse string, it will just dm you immediately.

        Examples:
            > remindme 2mo1d1s Learn how to code in python
            > remindme channel 2h Will start the tourney soon.
            > remindme Just a quick reminder

        Parameters
        ----------
        argument: str
            Try to parse this

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'remindme'):
            return
        pass


    @commands.command(aliases=['id', 'snowflake'])
    @commands.guild_only()
    async def snowflakeid(self, ctx: commands.Context, *, argument: str):
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
    async def echo(self, ctx: commands.Context, *, message: str):
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
    async def channel(self, ctx: commands.Context, channels: str, *, message: str):
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
    async def userinfo(self, ctx: commands.Context, *, user: str):
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
    async def pingrole(self, ctx: commands.Context, *, roles: str):
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
    async def inrole(self, ctx: commands.Context, *, roles: str):
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
    async def _roleadd(self, ctx: commands.Context, *, roles: str):
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
    async def _rolerm(self, ctx: commands.Context, *, roles: str):
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
