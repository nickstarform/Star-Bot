"""."""

# internal modules
import random
import textwrap
import subprocess
import os
import sys

# external modules
import discord
from discord.ext import commands
import asyncio

# relative modules
from cogs.utilities import (permissions,)
from cogs.utilities.functions import (current_time,
    get_role, parse, flatten) # noqa
from cogs.utilities.embed_dialog import respond, confirm
from cogs.utilities import embed_errors as eembeds
from cogs.utilities.embed_mod import guildreport
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.guild_manip_functions import createrole

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
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'report'):
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
            # print(e)
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
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'suggest'):
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
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'remindme'):
            return
        pass


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
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'echo'):
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
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'pingrole'):
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

    @commands.group(name='roles', aliases=['role', 'joinrole', 'rolejoin', 'iam', 'a'])
    @commands.guild_only()
    async def _role(self, ctx):
        """Joinable roles.

        Parameters
        ----------

        Returns
        ----------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'role'):
            return
        if (ctx.invoked_subcommand is None):
            roles = await self.bot.pg.get_all_joinable_roles(ctx.guild.id)
            # print(roles)
            roles = flatten([get_role(ctx, str(role)) for role in roles])
            # print(roles)
            if len(roles) > 0:
                embeds = generic_embed(
                    title='Joinable Roles',
                    desc=", ".join([r.name for r in roles]),
                    fields=[],
                    footer=current_time())
                for embed in embeds:
                    await ctx.send(embed=embed)
                    return
            else:
                await ctx.channel.send(embed=eembeds.internalerrorembed(f'No joinable roles found in guild'), delete_after=5)
                await respond(ctx, False)
            return

    @_role.command(name='add', aliases=['in', 'join'])
    async def _roleadd(self, ctx: commands.Context, *, roles: str):
        """Join roles.

        Parameters
        ----------
        roles: str
            roles to join, comma separated

        Returns
        ----------
        """
        try:
            roles = flatten([get_role(ctx, role) for role in roles.split(',')])
            if isinstance(roles, type(None)) or len(roles) == 0:
                await ctx.channel.send(embed=eembeds.internalerrorembed(f'Roles: <@&{">,<&".join(roles)}> not found!'), delete_after=5)
                await respond(ctx, False)
                return
            joinableroles = await self.bot.pg.get_all_joinable_roles(ctx.guild.id)
            if len(joinableroles) == 0:
                await ctx.channel.send(embed=eembeds.internalerrorembed(f'No joinable roles found'), delete_after=5)
                await respond(ctx, False)
                return
            jroles = []
            for role in roles:
                if role.id in joinableroles:
                    jroles.append(role)
            base = ctx.author.roles
            base += jroles
            await ctx.author.edit(roles=base)
            await respond(ctx, True)
        except Exception as e:
            print('Error adding single joinrole to user:', e)
            await respond(ctx, False)
        pass

    @_role.command(name='remove', aliases=['rm', 'del', 'not', 'leave'])
    async def _rolerm(self, ctx: commands.Context, *, roles: str):
        """Leave roles.

        Parameters
        ----------
        roles: str
            roles to leave, comma separated

        Returns
        ----------
        """
        try:
            member = ctx.author
            roles = flatten([get_role(ctx, x) for x in roles.split(',')])
            roles = list(set(member.roles) - set(roles))
            await member.edit(roles=roles)
            await respond(ctx, True)
        except Exception as e:
            print('Error removing:', e)
            await respond(ctx, False)
        pass

    """
    COLOUR CMDS
    """
    def _does_colourrole_exist(self, guild, role):
        role = role.strip('#')
        role = f'#{role}'
        for r in guild.roles:
            if r.name.lower() == role.lower():
                return True
        return False

    def _is_hex(self, role):
        role = role.strip('#')
        try:
            _ = int(role, 16)
            return True
        except:
            return False

    def _is_colourrole(self, role):
        role = role.name.lower().strip('#')
        try:
            _ = int(role, 16)
            return True
        except:
            return False

    def _clamp(self, x):
        return max(0, min(x, 255))

    def _random_rgb(self):
        return [self._clamp(random.randint(0, 254)) for x in range(3)]

    def _rgb_2_hex(self, x):
        return "#{0:02x}{1:02x}{2:02x}".format(*x)

    def _hex_2_rgb(self, x):
        x = x.strip('#')
        a = x[0:2], x[2:4], x[4:-1]
        r, g, b = [int(x, 16) for x in a]
        return r, g, b

    def _random_hex(self):
        return self._rgb_2_hex(self._random_rgb()).upper()

    @commands.group(name='colour', aliases=['color', 'colors',
                                            'colours', 'colourrole'])
    @commands.guild_only()
    async def _colour(self, ctx):
        """Hex colour roles.

        Parameters
        ----------

        Returns
        ----------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'colour'):
            return
        if not self.bot.guild_settings[ctx.guild.id]['colour_enabled']:
            await ctx.send(embed=eembeds.internalerrorembed(f'Colour role not enabled here.'), delete_after=15)
            await respond(ctx, False)
            return
        if (ctx.invoked_subcommand is None):
            roles = [r for r in ctx.guild.roles if self._is_colourrole(r)]
            if len(roles) > 0:
                embeds = generic_embed(
                    title='Colour joinable Roles',
                    desc=", ".join([r.name for r in roles]),
                    fields=[],
                    footer=current_time())
                for embed in embeds:
                    await ctx.send(embed=embed)
                    return
            else:
                await ctx.channel.send(embed=eembeds.internalerrorembed(f'No colour roles found in guild. Set your own!'), delete_after=5)
                await respond(ctx, False)
            return

    @_colour.command(name='add')
    async def _colouradd(self, ctx: commands.Context, role: str):
        """Hex colour role to add.

        Parameters
        ----------
        role: str
            Hex color role `#FFFFFF`

        Returns
        ----------
        """
        await self._colour_genrm(ctx)
        await self._colour_createadd(ctx, role)
        return

    @_colour.command(name='remove', aliases=['rm', 'del', 'leave'])
    async def _colourrm(self, ctx: commands.Context):
        """Hex colour role to remove.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        await self._colour_genrm(ctx)
        return

    async def _colour_genrm(self, ctx: commands.Context):
        rolecheck = [x for x in ctx.author.roles
                     if self._is_hex(x.name)]
        if len(rolecheck) > 0:
            # remove from role
            role = rolecheck[0]
            base = list(set(ctx.author.roles) - set(rolecheck))
            if len(base) != len(ctx.author.roles):
                try:
                    success = await ctx.author.edit(roles=base)
                    await respond(ctx, True)
                    return
                except Exception as e:
                    await ctx.channel.send(embed=eembeds.internalerrorembed(f'Couldn\'t set your roles, removal: {e}'), delete_after=15)
                    await respond(ctx, False)
                    return
            else:
                await respond(ctx, True)
                return
        else:
            await respond(ctx, True)
            return


    @_colour.command(name='show', aliases=['list', 'ls'])
    async def _colourshow(self, ctx: commands.Context):
        """Already set colour roles.

        Parameters
        ----------

        Returns
        ----------
        """
        roles = [r for r in ctx.guild.roles if self._is_colourrole(r)]
        if len(roles) > 0:
            embeds = generic_embed(
                title='Colour joinable Roles',
                desc=", ".join([r.name for r in roles]),
                fields=[],
                footer=current_time())
            for embed in embeds:
                await ctx.send(embed=embed)
                return
        else:
            await ctx.channel.send(embed=eembeds.internalerrorembed(f'No colour roles found in guild. Set your own!'), delete_after=5)
            await respond(ctx, False)
        return

    @_colour.command(name='random', aliases=['rnd'])
    async def _colourrnd(self, ctx: commands.Context):
        """Ping roles.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        role = self._random_hex()
        await self._colour_genrm(ctx)
        await self._colour_createadd(ctx, role)
        return


    async def _colour_createadd(self, ctx: commands.Context, role: str):
        """Ping roles.

        Parameters
        ----------
        roles: str
            roles to ping, can be comma separated

        Returns
        ----------
        """
        role = f"#{role.upper().strip('#')}"
        if self._does_colourrole_exist(ctx.guild, role):
            # set user to join it
            role = discord.utils.find(lambda r: r.name.upper() == role, ctx.guild.roles)
            base = ctx.author.roles
            base.append(role)
            try:
                success = await ctx.author.edit(roles=base)
                await respond(ctx, True)
                return
            except Exception as e:
                await ctx.channel.send(embed=eembeds.internalerrorembed(f'Couldn\'t set your roles in colourcreateddd: {e}'), delete_after=15)
                await respond(ctx, False)
                return
        else:
            # create role
            # set user to join
            base_role = await self.bot.pg.get_colourtemplate(ctx.guild.id, self.bot.logger)
            base_role = base_role[0].items().__next__()[1]
            if base_role:
                success = await createrole(self.bot, ctx, role, base_role, color=True)
                base = ctx.author.roles
                if success[0]:
                    base.append(success[1])
                    try:
                        await ctx.author.edit(roles=base)
                        await respond(ctx, True)
                        return
                    except Exception as e:
                        await ctx.channel.send(embed=eembeds.internalerrorembed(f'Something went wrong in colourcreateadd editting roles: {e}'), delete_after=15)
                        await respond(ctx, False)
                        return
            else:
                await ctx.channel.send(embed=eembeds.internalerrorembed(f'The colour role hasn\'t been setup properly. Yell at your admins'), delete_after=15)
                await respond(ctx, False)
                return
        await ctx.channel.send(embed=eembeds.internalerrorembed(f'Something went wrong in colourcreateadd'), delete_after=15)
        await respond(ctx, False)
        return

    @_colour.command(name='prune', aliases=['purge', 'clean'])
    @permissions.is_admin()
    async def _colourprune(self, ctx: commands.Context, ignore: bool=False):
        """This will prune out inactive colour roles or active ones.

        Parameters
        ----------
        ignore: bool
            if True will remove all colour roles

        Returns
        ----------
        """
        if not await confirm(ctx, f'This will manually prune inactive colour roles and is irreversable. You set ignore={ignore}. If `True` it will remove roles with members in them too.', 10):
                await respond(ctx, False)
                return
        to_del = []
        for r in ctx.guild.roles:
            if self._is_colourrole(r):
                if (len(r.members) == 0) or ignore:
                    to_del.append(r.name)
                    try:
                        await r.delete()
                    except Exception as e:
                        await ctx.channel.send(embed=eembeds.internalerrorembed(f'Something went wrong in colour pruning: {e}'), delete_after=15)
                        await respond(ctx, False)
                        return
        embeds = generic_embed(
            title='Colour Roles Pruned',
            desc=f', '.join(to_del),
            fields=[],
            footer=current_time())
        for embed in embeds:
            await ctx.send(embed=embed)
        await respond(ctx, True)
        return

    """
    CODING
    """
    # get readthedocs for master branch


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
