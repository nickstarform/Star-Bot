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
from cogs.utilities.functions import (current_time,
    extract_id, flatten,
    parse, ModAction, bannedmember,
    get_role, get_member)
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.message_general import generic_message
from cogs.utilities.embed_dialog import respond, confirm
from cogs.utilities import embed_errors as eembed
from cogs.utilities import embed_log
from cogs.utilities.guild_manip_functions import createrole


# global attributes
__all__ = ('Moderation',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(Moderation(bot))
    print('Loaded Moderation')


class Moderation(commands.Cog):
    """Blacklist Global commands."""

    def __init__(self, bot):
        """Blacklist Global commands."""
        self.bot = bot
        super().__init__()

    """
    BASIC PERM MANIPULATION
    """

    async def add_perms(self, user, channel):
        """Add a user to channels perms."""
        try:
            await channel.set_permissions(user, read_messages=True)
        except Exception as e:
            self.bot.logger.warning(f'{e}')

    async def remove_perms(self, user, channel):
        """Remove a users perms on a channel."""
        try:
            await channel.set_permissions(user, read_messages=False)
        except Exception as e:
            self.bot.logger.warning(f'{e}')

    """
    BASIC ROLE MANIPULATION
    """

    @commands.group(aliases=['editjoinroles', 'changejoinrole'])
    @commands.guild_only()
    @permissions.admin_or_permissions(manage_roles=True)
    async def changejoinroles(self, ctx):
        """Manage servers joinable/self-assignable roles.

        Careful as this includes reaction roles if you have those setup.
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'changejoinroles'):
            return
        if ctx.invoked_subcommand is None:
            assignable_roles = []
            assignable_role_ids = await self.bot.pg.get_all_joinable_roles(ctx.guild.id)
            if not isinstance(assignable_role_ids, type(None)) and len(assignable_role_ids) > 0:
                for i in range(len(assignable_role_ids)):
                    assignable_role_ids[i] = ctx.guild.get_role(int(assignable_role_ids[i]))
                embeds = generic_embed(
                    title=f'Current Joinable Roles',
                    desc=', '.join([x.name for x in assignable_role_ids]),
                    fields=[],
                    footer=current_time())
            else:
                embeds = generic_embed(
                    title=f'No Joinable Roles are set',
                    desc='',
                    fields=[],
                    footer=current_time())

            for embed in embeds:
                await ctx.send(embed=embed)

    @changejoinroles.command(name='add')
    async def _cjra(self, ctx: commands.Context, base_role: str=None, *, roles: str=None):
        """Add to joinable list.

        If the role isn't found, it will create the role.

        Parameters
        ----------
        member: str
            Member to change
        roles: str
            id(s)/mentionables of the roles to add

        Returns
        -------
        """
        if isinstance(roles, type(None)) and isinstance(base_role, type(None)) :
            await generic_message(ctx, [ctx.channel], f'You need to specify at least 1 role to add', 5)
            await respond(ctx, False)
            return
        elif isinstance(roles, type(None)):
            roles = base_role
            base_role = None

        t = roles
        tb = base_role
        found_role = []
        not_found = []
        if base_role:
            base_role = get_role(ctx, tb)
        for r in roles.replace(' ', '').split(','):
            role = get_role(ctx, r)
            if not isinstance(role, type(None)):
                found_role.append(role)
            else:
                not_found.append(r)
        for i in range(len(not_found)):
            i = len(not_found) - 1 - i
            r = not_found[::-1][i]

            if base_role:
                success = await createrole(self.bot, ctx, r, base_role)
                if success[0]:
                    found_role.append(success[1])
                    del not_found[i]
        for r in found_role:
            success = await self.bot.pg.add_joinable_role(ctx.guild.id, r.id, self.bot.logger)
        embeds = generic_embed(
            title='Joinable roles',
            desc='Tried to add the following roles',
            fields=[['ADDED', ','.join([x.name for x in found_role])],['FAILED', ','.join([x for x in not_found])]
            ],
            footer=current_time(),
                    colours=Colours.SUCCESS)
        for embed in embeds:
            await ctx.send(embed=embed)

    @changejoinroles.command(name='remove', aliases=['rm', 'del', 'delete'])
    async def _cjrr(self, ctx: commands.Context, *, roles: str):
        """Remove joinable roles.

        Parameters
        ----------
        member: str
            Member to change
        roles: str
            id(s)/mentionables of the roles to remove

        Returns
        -------
        """
        if roles.lower() == 'all':
            if not await confirm(ctx, f'This will remove all the  from the role and is irreversable.', 10):
                await respond(ctx, False)
                return
            allroles = await self.bot.pg.get_all_joinable_roles(ctx.guild.id)
            allroles = list(map(str, allroles))
            passed = []
            failed = []
            for r in allroles:
                success = await self.bot.pg.remove_joinable_role(ctx.guild.id, r, self.bot.logger)
                if success:
                    passed.append(r)
                else:
                    failed.append(r)
            if (len(passed) > 0) or (len(failed) > 0):
                embeds = generic_embed(
                    title='Joinable roles',
                    desc='Tried to remove the following roles',
                    fields=[['REMOVED', '<@&' + '>,<&'.join(passed) + '>'],['FAILED', '<@&' + '>,<&'.join(failed) + '>']],
                    footer=current_time(),
                    colours=Colours.SUCCESS)
            else:
                embeds = generic_embed(
                    title='Joinable roles',
                    desc='Tried to remove the following roles',
                    fields=[['ATTEMPED BUT FAILED', '<@&' + '>,<&'.join(allroles) + '>']],
                    footer=current_time(),
                    colours=Colours.ERROR)
            for embed in embeds:
                await ctx.send(embed=embed)
            return
        passed = []
        failed = []
        for r in roles.replace(' ', '').split(','):
            role = get_role(ctx, r)
            try:
                success = await self.bot.pg.remove_joinable_role(ctx.guild.id, role.id, self.bot.logger)
            except Exception as e:
                await ctx.send(embed=eembed.internalerrorembed(f'Error removing joinableroles: {e}'), delete_after=5)
                await respond(ctx, False)
                return
            if success:
                passed.append(str(role.id))
            else:
                failed.append(r)
        if (len(passed) > 0) or (len(failed) > 0):
            embeds = generic_embed(
                title='Joinable roles',
                desc='Tried to remove the following roles',
                fields=[['REMOVED', '<@&' + '>,<&'.join(passed) + '>'],['FAILED', '<@&' + '>,<&'.join(failed) + '>']],
                footer=current_time(),
                colours=Colours.SUCCESS)
        else:
            embeds = generic_embed(
                title='Joinable roles',
                desc='Tried to remove the following roles',
                fields=[['ATTEMPED BUT FAILED', '<@&' + '>,<&'.join(allroles) + '>']],
                footer=current_time(),
                colours=Colours.ERROR)
        for embed in embeds:
            await ctx.send(embed=embed)
        return

    @changejoinroles.command(name='info')
    async def _cjri(self, ctx: commands.Context, role: str, *, info: str):
        """Replace/add the joinable roles info.

        Parameters
        ----------
        member: str
            Member to change
        role: str
            id/mentionables of the role to set

        Returns
        -------
        """
        try:
            role = get_role(ctx, role)
        except:
            await ctx.send(embed=eembed.internalerrorembed(f'Error setting joinablerole info: {e}'), delete_after=5)
            await respond(ctx, False)
            return

        if await self.bot.pg.is_single_joininfo(ctx.guild.id, role.id):
            success = await self.bot.pg.set_single_joininfo(ctx.guild.id, role.id, info, self.bot.logger)
            embed = generic_embed(
                title=f'Joinable Role Info',
                desc=f'Set <@&{role.id}> with the info:\n{info}',
                fields=[],
                footer=current_time(),
                colours=Colours.SUCCESS)[0]
        else:
            success = await self.bot.pg.add_single_joininfo(ctx.guild.id, role.id, info, self.bot.logger)
            if success:
                embed = generic_embed(
                    title=f'Joinable Role Info',
                    desc=f'Added <@&{role.id}> with the info:\n{info}',
                    fields=[],
                    footer=current_time(),
                    colours=Colours.SUCCESS)[0]
            else:
                embed = generic_embed(
                    title=f'Joinable Role Info',
                    desc=f'Failed to set <@&{role.id}> with the info:\n{info}',
                    fields=[],
                    footer=current_time(),
                    colours=Colours.ERROR)[0]
        await ctx.send(embed=embed)
        return

    @commands.command(aliases=['prunerole', 'purgerole'])
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def cleanrole(self, ctx: commands.Context, *, role: str):
        """Remove all users from role.

        Parameters
        ----------
        member: str
            Member to change
        roles: str
            id(s)/mentionables of the roles to clean

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'cleanrole'):
            return
        if not await confirm(ctx, f'This will remove everyone from the role and is irreversable.', 10):
            await respond(ctx, False)
            return
        t = role
        role = get_role(ctx, role)
        if not role:
            await respond(ctx, False)
            await ctx.send(embed=eembed.rolenotfoundembed(f'<@&{t}>'), delete_after=5)
            return
        count = 0
        for user in role.members:
            try:
                local_roles = user.roles.copy()
                local_roles.remove(found_role)
                await user.edit(roles=local_roles)
                count += 1
            except Exception as e:
                self.bot.logger.warning(f'Issue cleaning role: {e}')
        embed = generic_embed(
            title=f'Cleaned Role',
            desc=f'Removed {count} people from the {role.name} role.',
            footer=current_time(),
            colours=Colours.SUCCESS)[0]
        await ctx.send(embed=embed)
        return

    @commands.group(aliases=['setroles', 'giverole'])
    @permissions.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def setrole(self, ctx):
        """Change the user's roles."""
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'setrole'):
            return 
        if ctx.invoked_subcommand is None:
            await respond(ctx, False)
            ctx.send(embed=embed_errors.internalerrorembed(f'Invoke a subcommand, you most likely meant `add`'), delete_after=5)
            return

    @setrole.command(name='add', aliases=['give'])
    async def _roleadd(self, ctx: commands.Context, member: str, *, roles: str):
        """Give the users these roles.

        Parameters
        ----------
        member: str
            Member to change
        roles: str
            id(s)/mentionables of the roles to add

        Returns
        -------
        """
        try:
            roles = roles.replace(' ', '')
            t = member
            member = get_member(ctx, member)
            if not member:
                await generic_message(ctx, [ctx.channel], f'Couldn\'t find user <@{t}>', 5)
                await respond(ctx, False)
                return
            roles = flatten([get_role(ctx, x) for x in roles.split(',')])
            roles += member.roles
            await member.edit(roles=roles)
            await respond(ctx, True)
        except Exception as e:
            print('Error adding:', e)
            await respond(ctx, False)
        pass

    @setrole.command(name='replace', aliases=['set'])
    async def _rolerepl(self, ctx: commands.Context, member: str, *, roles: str):
        """Give the users these roles.

        Parameters
        ----------
        member: str
            Member to change
        roles: str
            id(s)/mentionables of the roles to add

        Returns
        -------
        """
        try:
            roles = roles.replace(' ', '')
            member = get_member(ctx, member)
            if not member:
                await generic_message(ctx, [ctx.channel], f'Couldn\'t find user <@{t}>', 5)
            roles = flatten([get_role(ctx, x) for x in roles.split(',')])
            await member.edit(roles=roles)
            await respond(ctx, True)
        except Exception as e:
            print('Error replace:', e)
            await respond(ctx, False)
        pass

    @setrole.command(name='remove', aliases=['del', 'rm'])
    async def _rolerm(self, ctx: commands.Context, member: str, *, roles: str):
        """Give the users these roles.

        Parameters
        ----------
        member: str
            Member to change
        roles: str
            id(s)/mentionables of the roles to add

        Returns
        -------
        """
        try:
            roles = roles.replace(' ', '')
            member = get_member(ctx, member)
            if not member:
                await generic_message(ctx, [ctx.channel], f'Couldn\'t find user <@{t}>', 5)
            roles = flatten([get_role(ctx, x) for x in roles.split(',')])
            roles = list(set(roles) - set(member.roles))
            await member.edit(roles=roles)
            await respond(ctx, True)
        except Exception as e:
            print('Error removing:', e)
            await respond(ctx, False)
        pass

    """
    BASIC MESSAGE MANIPULATION
    """
    @commands.command()
    @permissions.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def prune(self, ctx: commands.Context, amount: str='10', user: str=None):
        """Purge a set number of messages.

        Parameters
        ----------
        amount: int
            Integer for delete, defaults to 10
        user: str
            Id of the user to purge

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'prune'):
            return
        try:
            _ = int(amount)
        except:
            tmp = user
            user = amount
            amount = tmp
        try:
            if int(amount) > 1E6:
                user = get_member(ctx, a)
                amount = 10
        except:
            pass

        if not isinstance(user, type(None)):
            try:
                user = get_member(ctx, user)
            except:
                user = None

        try:
            await ctx.message.delete()
            async for message in ctx.channel.history(limit=int(amount)):
                if user:
                    if message.author.id != user.id:
                        continue
                await message.delete()
            await generic_message(ctx, [ctx.channel], f'Deleted messages', 5)
            return
        except discord.Forbidden as e:
            await respond(ctx, False)
            return await ctx.send(embed=eembed.botpermissionerrorembed('purge', 'manage_messages'), delete_after=10)  # noqa
        except Exception as e:
            await respond(ctx, False)
            self.bot.logger.warning(f'Error purging messages: {e}')
            return

    @commands.command()
    @permissions.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def clearchat(self, ctx):
        """Purge a channel.

        Use all to signify deleting every message in the channel greedy

        Parameters
        ----------
        amount: int
            Integer for delete, defaults to 10
        user: str
            Id of the user to purge

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'clearchat'):
            return
        if not await confirm(ctx, f'Do you want clear out this channel? (Irreversable)', 10): # noqa
            return

        hist = [message async for message in ctx.channel.history(limit=100)
                if message]
        old = hist[0]
        while len(hist) > 0:
            failed = False
            try:
                await ctx.channel.delete_messages(hist)
            except Exception as e:
                failed = True
            if failed:
                for message in hist:
                    try:
                        await message.delete()
                    except Exception as e:
                        pass
            hist = [message async for message in ctx.channel.history(limit=100)
                    if message]
            if ctx.message.clear_content.lower().replace(' ', '') != 'all':
                hist = []

    """
    KICKING
    """
    @commands.group()
    @permissions.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def kick(self, ctx):
        """Kick a user.

        Parameters
        ----------
        amount: int
            Integer for delete, defaults to 10
        user: str
            Id of the user to purge

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'kick'):
            return
        if not ctx.invoked_subcommand:
            content = ' '.join(ctx.message.content.split(' ')[1:])
            member = content.split(' ')[0]
            reason = ' '.join(content.split(' ')[1:])
            ids = member
            member = get_member(ctx, ids)
            if member is None:
                    await generic_message(ctx, [ctx.channel],
                        f"Couldn't resolve member <@{ids}>.",
                        5)
                    await respond(ctx, False)
                    return
            if reason is None or len(str(reason)) == 0:
                    await generic_message(ctx, [ctx.channel],
                        "You need to supply a reason, try again.",
                        5)
                    await respond(ctx, False)
                    return
            footer = await self.bot.pg.get_kick_footer(ctx.guild.id, self.bot.logger)
            if (len(reason) + len(footer) + 25) > 500:
                    await generic_message(ctx, [ctx.channel],
                        "Mesage too long...",
                        5)
                    await respond(ctx, False)
                    return
            if await confirm(ctx, f'**Kick** {member.mention} for {reason}', 10):
                embed = generic_embed(
                    title='❗KICKED❗',
                    desc=f'You have been kicked from {ctx.guild.name}',
                    fields=[['Reason', reason], ['Time', current_time()]],
                    footer=footer,
                    colours=Colours.ERROR)[0]
                try:
                    try:
                        await member.create_dm()
                        await member.dm_channel.send(embed=embed)
                    except Exception as e:
                        await generic_message(ctx, [ctx.channel],
                            f"Error messaging user!: {e}",
                            5)
                        self.bot.logger.warning(f'Error messaging user!: {e}')
                    await member.kick(reason=f'by: {ctx.author} for: {reason}')
                    await respond(ctx, True)
                    try:
                        await self.bot.pg.add_single_moderation(
                            ctx.guild.id,
                            ctx.author.id,
                            member.id,
                            reason,
                            ModAction.KICK,
                            self.bot.logger
                        )
                    except Exception as e:
                        await respond(ctx, False)
                        await generic_message(ctx, [ctx.channel],
                            f"Error storing modaction!: {e}",
                            5)
                        self.bot.logger.warning(f'Error storing modaction: {e}')
                except Exception as e:
                    await respond(ctx, False)
                    await generic_message(ctx, [ctx.channel],
                        f"Error kicking user!: {e}",
                        5)
                    self.bot.logger.warning(f'Error kicking user!: {e}')
                    return
                if self.bot.guild_settings[ctx.guild.id]['modlog_enabled']:
                    try:
                        embed = embed_log.kickembed(member, ctx.author, reason)
                        mod_logs = await self.bot.pg.get_all_modlogs(ctx.guild.id)
                        for channel_id in mod_logs:
                            await (self.bot.get_channel(channel_id)).send(
                                embed=embed)
                    except Exception as e:
                        await respond(ctx, False)
                        await generic_message(ctx, [ctx.channel],
                            f"Issue posting to mod log!: {e}",
                            5)
                        self.bot.logger.warning(f'Issue posting to mod log: {e}')
            else:
                await respond(ctx, False)
                await ctx.send("Cancelled kick", delete_after=3)


    @kick.command(aliases=['test', 'demo', 'show'])
    async def _kicktest(self, ctx):
        """Test the kick message.

        This will demo both the dm'ed message
        and the log message.

        Parameters
        ----------

        Returns
        -------
        """
        embeds = []
        footer = await self.bot.pg.get_kick_footer(ctx.guild.id, self.bot.logger)
        embed = generic_embed(
            title='<TESTING>❗KICKED❗',
            desc=f'You have been kicked from {ctx.guild.name}',
            fields=[['Reason', 'REASON WILL GO HERE'], ['Time', current_time()]],
            footer=footer,
            colours=Colours.ERROR)[0]
        embeds.append(embed)
        embed = embed_log.kickembed(self.bot.user, ctx.author, 'REASON WILL GO HERE')
        embeds.append(embed)
        for embed in embeds:
            await ctx.send(embed=embed)

    """
    BANNING
    """

    @commands.command()
    @permissions.has_permissions(ban_members=True)
    @commands.guild_only()
    async def logban(self, ctx: commands.Context, member: str, *,
                     reason: str=None):
        """Log a manual ban.
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'logban'):
            return
        member = await bannedmember(ctx, member)
        reason = reason if reason else member.reason
        member = member.user
        if not member:
            await respond(ctx, False)
            return
        if self.bot.guild_settings[ctx.guild.id]['modlog_enabled']:
            try:
                if not await confirm(ctx,
                    f'**LOGBAN** {member.mention} for {reason}', 10):  # noqa
                    return
                try:
                    await self.bot.pg.add_single_moderation(
                        ctx.guild.id,
                        ctx.author.id,
                        member.id,
                        reason,
                        ModAction.BAN,
                        self.bot.logger
                    )
                except Exception as e:
                    await respond(ctx, False)
                    await generic_message(ctx, [ctx.channel],
                        f"Error storing modaction!: {e}",
                        5)
                    self.bot.logger.warning(f'Error storing modaction: {e}')
            except Exception as e:
                await respond(ctx, False)
                await generic_message(ctx, [ctx.channel],
                    f"Error logbanning user!: {e}",
                    5)
                self.bot.logger.warning(f'Error logbanning user!: {e}')
                return
            if self.bot.guild_settings[ctx.guild.id]['modlog_enabled']:
                try:
                    embed = embed_log.banembed(member, ctx.author, reason)
                    mod_logs = await self.bot.pg.get_all_modlogs(ctx.guild.id)
                    for channel_id in mod_logs:
                        await (self.bot.get_channel(channel_id)).send(
                            embed=embed)
                except Exception as e:
                    await respond(ctx, False)
                    await generic_message(ctx, [ctx.channel],
                        f"Issue posting to mod log!: {e}",
                        5)
                    self.bot.logger.warning(f'Issue posting to mod log: {e}')

    @logban.error
    async def logban_error(self, ctx: commands.Context, error):
        self.bot.logger.warning(f'Banned_user argument not found in ban list.')
        await ctx.send(
            embed=embeds.LogbanErrorEmbed(),
            delete_after=3
        )
 
    @commands.group()
    @permissions.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def ban(self, ctx):
        """Ban a user.

        Parameters
        ----------
        amount: int
            Integer for delete, defaults to 10
        user: str
            Id of the user to purge

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'ban'):
            return
        if not ctx.invoked_subcommand:
            content = ' '.join(ctx.message.content.split(' ')[1:])
            member = content.split(' ')[0]
            reason = ' '.join(content.split(' ')[1:])
            ids = member
            member = get_member(ctx, ids)
            if member is None:
                    await generic_message(ctx, [ctx.channel],
                        f"Couldn't resolve member <@{ids}>.",
                        5)
                    await respond(ctx, False)
                    return
            if reason is None or len(str(reason)) == 0:
                    await generic_message(ctx, [ctx.channel],
                        "You need to supply a reason, try again.",
                        5)
                    await respond(ctx, False)
                    return
            footer = await self.bot.pg.get_ban_footer(ctx.guild.id, self.bot.logger)
            if (len(reason) + len(footer) + 25) > 500:
                    await generic_message(ctx, [ctx.channel],
                        "Mesage too long...",
                        5)
                    await respond(ctx, False)
                    return
            if await confirm(ctx, f'**BAN** {member.mention} for {reason}', 10):
                embed = generic_embed(
                    title='❗BANNED❗',
                    desc=f'You have been banned from {ctx.guild.name}',
                    fields=[['Reason', reason], ['Time', current_time()]],
                    footer=footer,
                    colours=Colours.ERROR)[0]
                try:
                    try:
                        await member.create_dm()
                        await member.dm_channel.send(embed=embed)
                    except Exception as e:
                        await generic_message(ctx, [ctx.channel],
                            f"Error messaging user!: {e}",
                            5)
                        self.bot.logger.warning(f'Error messaging user!: {e}')
                    await member.ban(reason=f'by: {ctx.author} for: {reason}')
                    await respond(ctx, True)
                    try:
                        await self.bot.pg.add_single_moderation(
                            ctx.guild.id,
                            ctx.author.id,
                            member.id,
                            reason,
                            ModAction.BAN,
                            self.bot.logger
                        )
                    except Exception as e:
                        await respond(ctx, False)
                        await generic_message(ctx, [ctx.channel],
                            f"Error storing modaction!: {e}",
                            5)
                        self.bot.logger.warning(f'Error storing modaction: {e}')
                except Exception as e:
                    await respond(ctx, False)
                    await generic_message(ctx, [ctx.channel],
                        f"Error banning user!: {e}",
                        5)
                    self.bot.logger.warning(f'Error banning user!: {e}')
                    return
                if self.bot.guild_settings[ctx.guild.id]['modlog_enabled']:
                    try:
                        embed = embed_log.banembed(member, ctx.author, reason)
                        mod_logs = await self.bot.pg.get_all_modlogs(ctx.guild.id)
                        for channel_id in mod_logs:
                            await (self.bot.get_channel(channel_id)).send(
                                embed=embed)
                    except Exception as e:
                        await respond(ctx, False)
                        await generic_message(ctx, [ctx.channel],
                            f"Issue posting to mod log!: {e}",
                            5)
                        self.bot.logger.warning(f'Issue posting to mod log: {e}')
            else:
                await respond(ctx, False)
                await ctx.send("Cancelled ban", delete_after=3)


    @ban.command(name='test', aliases=['demo', 'show'])
    async def _bantest(self, ctx):
        """Test the ban message.

        This will demo both the dm'ed message
        and the log message.

        Parameters
        ----------

        Returns
        -------
        """
        embeds = []
        footer = await self.bot.pg.get_ban_footer(ctx.guild.id, self.bot.logger)
        embed = generic_embed(
            title='<TESTING>❗BANNED❗',
            desc=f'You have been banned from {ctx.guild.name}',
            fields=[['Reason', 'REASON WILL GO HERE'], ['Time', current_time()]],
            footer=footer,
            colours=Colours.ERROR)[0]
        embeds.append(embed)
        embed = embed_log.banembed(self.bot.user, ctx.author, 'REASON WILL GO HERE')
        embeds.append(embed)
        for embed in embeds:
            await ctx.send(embed=embed)


    @commands.group(aliases=['rmban'])
    @permissions.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx):
        """Unbans a user.

        Will unban the user. You can put member # reason
        to forgive a ban action, otherwise will insert new
        modaction

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'unban'):
            return
        if not ctx.invoked_subcommand:
            content = ' '.join(ctx.message.content.split(' ')[1:])
            member = await bannedmember(ctx, content.split(' ')[0]).user
            try:
                t = int(content.split(' ')[1])
                index = t
                reason = ' '.join(content.split(' ')[2:])
            except:
                index = -1
                reason = ' '.join(content.split(' ')[1:])
            if member is None:
                    await generic_message(ctx, [ctx.channel],
                        f"Couldn't resolve member <@{content.split(' ')[0]}>.",
                        5)
                    await respond(ctx, False)
                    return
            if reason is None or len(str(reason)) == 0:
                    await generic_message(ctx, [ctx.channel],
                        "You need to supply a reason, try again.",
                        5)
                    await respond(ctx, False)
                    return
            footer = current_time()
            if (len(reason) + len(footer) + 25) > 500:
                    await generic_message(ctx, [ctx.channel],
                        "Mesage too long...",
                        5)
                    await respond(ctx, False)
                    return
            if await confirm(ctx, f'**UNBAN** {member.mention} for {reason}', 10):
                try:
                    await ctx.guild.unban(member, reason=f'by: {ctx.author} for: {reason}')
                    await respond(ctx, True)
                    try:
                        if index != -1:
                            await self.bot.pg.set_single_moderation(
                                ctx.guild.id,
                                member.id,
                                ctx.author.id,
                                index,
                                ModAction.BAN,
                                reason,
                                True,
                                self.bot.logger
                            )
                        else:
                            await self.bot.pg.add_single_moderation(
                                ctx.guild.id,
                                ctx.author.id,
                                member.id,
                                reason,
                                ModAction.BAN,
                                self.bot.logger
                            )
                    except Exception as e:
                        await respond(ctx, False)
                        await generic_message(ctx, [ctx.channel],
                            f"Error storing modaction!: {e}",
                            5)
                        self.bot.logger.warning(f'Error storing modaction: {e}')
                except Exception as e:
                    await respond(ctx, False)
                    await generic_message(ctx, [ctx.channel],
                        f"Error unbanning user!: {e}",
                        5)
                    self.bot.logger.warning(f'Error unbanning user!: {e}')
                    return
                if self.bot.guild_settings[ctx.guild.id]['modlog_enabled']:
                    try:
                        embed = embed_log.unbanembed(member, ctx.author, reason)
                        mod_logs = await self.bot.pg.get_all_modlogs(ctx.guild.id)
                        for channel_id in mod_logs:
                            await (self.bot.get_channel(channel_id)).send(
                                embed=embed)
                    except Exception as e:
                        await respond(ctx, False)
                        await generic_message(ctx, [ctx.channel],
                            f"Issue posting to mod log!: {e}",
                            5)
                        self.bot.logger.warning(f'Issue posting to mod log: {e}')
            else:
                await respond(ctx, False)
                await ctx.send("Cancelled unban", delete_after=3)

    @unban.command(name='test', aliases=['demo', 'show'])
    async def _unbantest(self, ctx):
        """Test the unban message.

        This will demo both the dm'ed message
        and the log message.

        Parameters
        ----------

        Returns
        -------
        """
        embeds = []
        footer = current_time()
        embed = embed_log.unbanembed(self.bot.user, ctx.author, 'REASON WILL GO HERE')
        embeds.append(embed)
        for embed in embeds:
            await ctx.send(embed=embed)

    """
    MESSAGING
    """
    @commands.command(aliases=['mdm'])
    @commands.guild_only()
    @permissions.admin_or_permissions(manage_guild=True)
    async def massdm(self, ctx: commands.Context, role: discord.Role, *, message: str):
        """Sends a DM to all Members with the given Role.
        Allows for the following customizations:
          `{member}` is the member being messaged
          `{role}` is the role through which they are being messaged
          `{server}` is the server through which they are being messaged
          `{sender}` is you, the person sending the message
        """

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            log.warning("Failed to delete command message: insufficient permissions")
        except:
            log.warning("Failed to delete command message")

        for member in role.members:
            try:
                await member.send(message.format(member=member, role=role, server=ctx.guild, sender=ctx.author))
            except discord.Forbidden:
                log.warning("Failed to DM user {0} (ID {0.id}): insufficient permissions".format(member))
                continue
            except:
                self.bot.logger.warning("Failed to DM user {0} (ID {0.id})".format(member))
                continue

    """
    ADD WARNINGS AND MODERATIONS
    """

# end of code

# end of file
