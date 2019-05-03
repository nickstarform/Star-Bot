"""."""

# internal modules
import psutil
import heapq
import os
from io import BytesIO
import sys
import datetime
import random

# external modules
import traceback
import discord
from discord.ext import commands
import matplotlib
import matplotlib.pyplot as plt
import asyncio

# relative modules
from cogs.utilities import (Colours, permissions)
from cogs.utilities.functions import (current_time, extract_id,
                                      get_member, get_role,
                                      parse, get_channel, flatten,
                                      extract_time, time_conv,
                                      is_id)
from cogs.utilities.embed_general import generic_embed
from cogs.utilities.message_general import generic_message
from cogs.utilities.embed_dialog import respond, iterator, confirm
from cogs.utilities.embed_errors import internalerrorembed, panicerrorembed

# global attributes
__all__ = ('Administration',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


# setup matplotlib correctly
plt.switch_backend('agg')


def setup(bot):
    bot.add_cog(Administration(bot))
    print('Loaded Administration')


def __unload(self):
    self._giveaway_task.cancel()


class NoWinnerFound(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors
    pass


class Administration(commands.Cog):
    """Administrative commands."""

    def __init__(self, bot):
        """Administrative commands."""
        self.bot = bot
        self._giveaway_task = bot.loop.create_task(self.giveaway_loop())
        self.emoji = f'\U0001f5f3'
        super().__init__()

    """
    BOTSTUFF
    """
    @commands.command()
    @permissions.is_admin()
    @commands.guild_only()
    async def change_nickname(self, ctx: commands.Context,
                              *, new_username: str):
        """Change the bot nickname.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'change_nickname', only_global=True):
            return
        bot_user = ctx.guild.me
        try:
            await bot_user.edit(nick=new_username)
            await respond(ctx, True)
        except Exception as e:
            await respond(ctx, False)
            self.bot.logger.warning(f'Error changing bots nickname: {e}')

    @commands.command(name='leaveguild')
    @permissions.is_admin()
    @commands.guild_only()
    async def _leaveg(self, ctx: commands.Context):
        """Change the bot nickname.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'leaveguild', only_global=True):
            return
        if not await confirm(ctx, f'```\nAre you sure you want the bot to leave?\n```', 15):
            await respond(ctx, False)
            return
        await ctx.guild.leave()

    """
    MODIFY CONFIGURATION
    """

    @commands.group(aliases=['configure'])
    @permissions.is_admin()
    @commands.guild_only()
    async def config(self, ctx):
        """Display Config.

        Use `config setup` to setup all your guild params.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'configure', only_global=True):
            return
        if ctx.invoked_subcommand is None:
            gid = ctx.guild.id
            try:
                tmp = await self.bot.pg.get_guild(gid, self.bot.logger)
                tmp = [[key, val] for (key, val) in tmp.items()]
                config = []
                for i in range(len(tmp)):
                    row = tmp[i][0]
                    if 'channels' in row and isinstance(tmp[i][1], list):
                        config.append([row, [f'<#{x}>' for x in tmp[i][1]]])
                    elif 'roles' in row and isinstance(tmp[i][1], list):
                        config.append([row, [f'<@&{x}>' for x in tmp[i][1]]])
                    elif 'users' in row and isinstance(tmp[i][1], list):
                        config.append([row, [f'<@{x}>' for x in tmp[i][1]]])
                    else:
                        config.append([row, tmp[i][1]])
                ctitle = f'{ctx.guild.name} Configuration'
                cdesc = ''

                embeds = generic_embed(
                    title=ctitle,
                    desc=cdesc,
                    fields=config,
                    footer=current_time(),
                    colours=Colours.COMMANDS
                )
                for embed in embeds:
                    await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(embed=internalerrorembed(f'Problem checking guild config: {e}'), delete_after=5)  # noqa
                await respond(ctx, False)
                self.bot.logger.warning(f'Error trying to return guild config: {e}')  # noqa

    @config.command(name='setup', aliases=['start', 'first'])
    async def _configsetup(self, ctx: commands.Context):
        """General setup for guild settings..

        This will step through all of the parameters to set for the guild.
        You will have the ability to keep the old values.

        Parameters
        ----------

        Returns
        -------
        """
        # gather the settings
        try:
            params = None
            e = None
            params = await self.bot.pg.get_guild(ctx.guild.id, self.bot.logger)
            failed = False
        except Exception as ec:
            e = ec
            failed = True
        if isinstance(params, type(None)) or failed:
            await ctx.send(embed=internalerrorembed(f'Problem checking guild config: {e}'), delete_after=5)  # noqa
            await respond(ctx, False)
            self.bot.logger.warning(f'Error trying to return guild config: {e}')  # noqa
            return
        # now start question logic
        questions = {}
        params = [[key, val] for (key, val) in params.items()]
        for i in range(len(params)):
            key, val = params[i]
            if key not in ('currtime', 'guild_id'):
                dt = str(type(val)).strip('< class').strip('>')
                if (('id' in key) or ('channel' in key) or ('role' in key) or ('user' in key)):  # noqa
                    key = f'Please set the value for {key}. Must be id ({dt})'
                else:
                    key = f'Please set the value for {key} ({dt})'
                questions[key] = val
        # ask questions now
        try:
            questions, final = await iterator(ctx, questions, 20, True, False)
        except Exception as e:
            await ctx.send(embed=internalerrorembed(f'Problem checking set config: {e}'), delete_after=5)  # noqa
            await respond(ctx, False)
            self.bot.logger.warning(f'Error trying to set guild config: {e}')  # noqa
            return
        if not final:
            return
        # gather the difference between original and response
        for key in list(final.keys()):
            if key in questions.keys():
                if final[key] == questions[key]:
                    final.pop(key)
                    continue
            val = final[key]
            final.pop(key)
            key = key[len('Please set the value for '):].split(' ')[0].strip('.')  # noqa
            final[key] = val

        # now read back these to user
        config = [[key, val] for (key, val) in final.items()]
        questions.clear()
        for i in range(len(config)):
            row = config[i][0]
            if 'channels' in row and isinstance(config[i][1], list):
                config[i] = [row, [f'<#{x}>' for x in config[i][1]]]
            elif 'roles' in row and isinstance(config[i][1], list):
                config[i] = [row, [f'<@&{x}>' for x in config[i][1]]]
            elif 'users' in row and isinstance(config[i][1], list):
                config[i] = [row, [f'<@{x}>' for x in config[i][1]]]
        ctitle = f'{ctx.guild.name} Configuration'
        if len(config) > 0:
            cdesc = 'These are the values that have been asked to changed.'
        else:
            cdesc = 'No values changed'

        embeds = generic_embed(
            title=ctitle,
            desc=cdesc,
            fields=config,
            footer=current_time(),
            colours=Colours.COMMANDS
        )
        for embed in embeds:
            await ctx.send(embed=embed)
        if len(config) == 0:
            return
        await ctx.send('Are these changes okay? [y/n]', delete_after=15)
        responded = await ctx.bot.wait_for("message",
                                           timeout=15,
                                           check=lambda message:
                                           message.author == ctx.message.author)  # noqa
        if responded.content.lower()[0] != 'y':
            await respond(ctx, False)
            await responded.delete()
            return
        else:
            await responded.delete()
        # now apply changes
        passed, failed = await self.bot.pg.set_multiple_records(ctx.guild.id, final, self.bot.logger)  # noqa
        return

    @config.command(name='change', aliases=['set', 'fix'])
    async def _configset(self, ctx: commands.Context, key: str, *, val: str):
        """Change a specific guild configuration.

        This is fine tuned and MUST match the exact specifications
        size of a record row for schema.guild. If it is unable to match
        it will not change that value and continue.

        Parameters
        ----------
        key: str:
            the exact col name
        value: str
            the value to input to

        Returns
        -------
        """
        # gather guild
        guild = ctx.guild
        gid = guild.id
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

    @config.command(name='prefix')
    async def _prefixchange(self, ctx: commands.Context, prefix: str):
        """Set prefix for guild.

        Must be <= 2 chars

        Parameters
        ----------
        prefix: str
            Prefix to set

        Returns
        -------
        """
        if len(prefix.strip()) > 2:
            await generic_message(ctx, [ctx.channel], f'Prefix `{prefix.strip()}` invalid. It needs to be <= 2 chars.', 5)
            await respond(ctx, False)
            return
        try:
            success = await self.bot.pg.set_prefix(
                ctx.guild.id,
                prefix,
                self.bot.logger
            )
            if success:
                self.bot.guild_settings[ctx.guild.id]['prefix'] = prefix
            await generic_message(ctx, [ctx.channel], f'Prefix `{prefix.strip()}` has been set.', 5)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong setting the prefix.')
            await ctx.send(embed=local_embed, delete_after=5)
            await respond(ctx, False)
            return

    @config.command(name='banfooter', aliases=['setban', 'setbanfooter'])
    async def _set_ban_footer(self, ctx: commands.Context, *, footer: str):
        """Set ban footer.

        Parameters
        ----------
        footer: str
            String of ban footer to set

        Returns
        -------
        """
        try:
            success = await self.bot.pg.set_ban_footer(
                ctx.guild.id,
                footer,
                self.bot.logger
            )
            await generic_message(ctx, [ctx.channel], f'Ban footer has been set to `{footer}`.', 15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong setting the ban footer.')
            await ctx.send(embed=local_embed, delete_after=5)
            await respond(ctx, False)
            return

    @config.command(name='kickfooter', aliases=['setkickfooter', 'setkick'])
    async def _set_kick_footer(self, ctx: commands.Context, *, footer: str):
        """Set kick footer.

        Parameters
        ----------
        footer: str
            String to set footer to

        Returns
        -------
        """
        try:
            success = await self.bot.pg.set_ban_footer(
                ctx.guild.id,
                footer,
                self.bot.logger
            )
            await generic_message(ctx, [ctx.channel], f'Ban footer has been set to `{footer}`.', 15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong setting the ban footer.')
            await ctx.send(embed=local_embed, delete_after=5)
            await respond(ctx, False)
            return

    @config.command(name='setinvites')
    async def _invites(self, ctx, status: bool):
        """Toggle autodeletion of invites.

        Parameters
        ----------
        status: bool
            status of invites allow (True doesn't delete)

        Returns
        ----------
        """
        try:
            success = await self.bot.pg.set_invites_allowed(
                ctx.guild.id,
                status)
            await generic_message(ctx, [ctx.channel], f'External discord invite has been set to `{status}`.', 15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong setting the invites.')
            await ctx.send(embed=local_embed, delete_after=5)
            await respond(ctx, False)
            return

    @config.command(name='setcolour', aliases=['enablecolour'])
    async def _enablecolour(self, ctx, status: bool):
        """Toggle ability to use colour roles.

        Parameters
        ----------
        status: bool
            If true users can join colour roles

        Returns
        ----------
        """
        try:
            success = await self.bot.pg.set_colour_enabled(
                ctx.guild.id,
                status)
            if success:
                self.bot.guild_settings[ctx.guild.id]['colour_enabled'] = status
                await generic_message(ctx, [ctx.channel], f'Colour role has been set to `{status}`.', 15)
                await respond(ctx, True)
                return
            else:
                await respond(ctx, False)
                return
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong setting the colour role status.')
            await ctx.send(embed=local_embed, delete_after=5)
            await respond(ctx, False)
            return

    @config.command(name='colourtemplate', aliases=['colourrole'])
    async def _setcolourtemplate(self, ctx, *, role: str):
        """Toggle ability to use colour roles.

        Parameters
        ----------
        status: bool
            If true users can join colour roles

        Returns
        ----------
        """
        base_role = get_role(ctx, role)
        if base_role:
            success = await self.bot.pg.set_colourtemplate(ctx.guild.id, base_role.id, self.bot.logger)
        else:
            success = False

        if success:
            await respond(ctx, True)
            return
        else:
            await generic_message(ctx, [ctx.channel], f'Something went wrong with setting template colour role <@&{role}>.', 15)
            await respond(ctx, False)
            return

    @config.command(name='welcomemessage', aliases=['setwelcome', 'changewelcome'])
    @commands.guild_only()
    async def _welcomemessage(self, ctx, *, content: str=None):
        """Set the welcome message.

        Use `\%server\%, \%user\% to specify either.`

        Parameters
        ----------
        content: str
            content to set the welcome message to

        Returns
        -------
        """
        if content is None:
            local_embed = internalerrorembed('Please also give the content to se the welcome message to. Use `\%server\%, \%user\% to specify either.`')
            await ctx.send(embed=local_embed, delete_after=20)
            return
        try:
            success = await self.bot.pg.set_welcome_message(
                ctx.guild.id,
                content,
                self.bot.logger)
            await generic_message(ctx, [ctx.channel], f'Welcome message has been set to `{content}`.', 15)
            await respond(ctx, True)
        except Exception as e:
            local_embed = internalerrorembed('Something went wrong welcome channel.')
            await ctx.send(embed=local_embed, delete_after=5)
            await respond(ctx, False)
            return

    """
    CHATSTATS
    """

    def create_chart(self, top, others, channel):
        plt.clf()
        sizes = [x[1] for x in top]
        labels = ["{} {:g}%".format(x[0], x[1]) for x in top]
        if len(top) >= 20:
            sizes = sizes + [others]
            labels = labels + ["Others {:g}%".format(others)]
        if len(channel.name) >= 19:
            channel_name = '{}...'.format(channel.name[:19])
        else:
            channel_name = channel.name
        title = plt.title("Stats in #{}".format(channel_name), color="white")
        title.set_va("top")
        title.set_ha("center")
        plt.gca().axis("equal")
        colors = ('r', 'darkorange', 'gold', 'y', 'olivedrab',
                  'green', 'darkcyan', 'mediumblue', 'darkblue',
                  'blueviolet', 'indigo', 'orchid',
                  'mediumvioletred', 'crimson', 'chocolate',
                  'yellow', 'limegreen', 'forestgreen',
                  'dodgerblue', 'slateblue', 'gray')
        pie = plt.pie(sizes, colors=colors, startangle=0)
        plt.legend(pie[0], labels, bbox_to_anchor=(0.7, 0.5),
                   loc="center", fontsize=10,
                   bbox_transform=plt.gcf().transFigure, facecolor='#ffffff')
        plt.subplots_adjust(left=0.0, bottom=0.1, right=0.45)
        image_object = BytesIO()
        plt.savefig(image_object, format='PNG', facecolor='#36393E')
        image_object.seek(0)
        return image_object

    @commands.command(name='chatchart', aliases=['chartchat', 'chatstats'])
    @commands.cooldown(1, 30, commands.BucketType.channel)
    @permissions.is_admin()
    async def _charting(self, ctx: commands.Context, channel: str=None):
        """Generate pie chart of ast 5000 messages in channel.

        Parameters
        ----------
        channel: str
            Optional channel to pass

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'chatchart', only_global=True):
            return
        e = discord.Embed(description="Loading...", colour=0x00ccff)
        e.set_thumbnail(url="https://i.imgur.com/vSp4xRk.gif")
        em = await ctx.send(embed=e)
        if channel is None:
            channel = ctx.message.channel
        else:
            channel = get_channel(ctx, channel)
        history = []
        if not channel.permissions_for(ctx.message.author).read_messages == True:
            await em.delete()
            return await ctx.send("You're not allowed to access that channel.")
        try:
            async for msg in channel.history(limit=5000):
                history.append(msg)
        except discord.errors.Forbidden:
            await em.delete()
            return await ctx.send("No permissions to read that channel.")
        msg_data = {'total count': 0, 'users': {}}

        for msg in history:
            if len(msg.author.name) >= 20:
                short_name = '{}...'.format(msg.author.name[:20]).replace("$", "\$")
            else:
                short_name = msg.author.name.replace("$", "\$")
            whole_name = '{}#{}'.format(short_name, msg.author.discriminator)
            if msg.author.bot:
                pass
            elif whole_name in msg_data['users']:
                msg_data['users'][whole_name]['msgcount'] += 1
                msg_data['total count'] += 1
            else:
                msg_data['users'][whole_name] = {}
                msg_data['users'][whole_name]['msgcount'] = 1
                msg_data['total count'] += 1

        for usr in msg_data['users']:
            pd = float(msg_data['users'][usr]['msgcount']) / float(msg_data['total count'])
            msg_data['users'][usr]['percent'] = round(pd * 100, 1)

        top_ten = heapq.nlargest(20, [(x, msg_data['users'][x][y])
                                      for x in msg_data['users']
                                      for y in msg_data['users'][x]
                                      if y == 'percent'], key=lambda x: x[1])
        others = 100 - sum(x[1] for x in top_ten)
        img = self.create_chart(top_ten, others, channel)
        await em.delete()
        await ctx.send(file=discord.File(fp=img, filename="chart.png"))

    @_charting.error
    async def charting_error(self, ctx, error):
        await ctx.send(f'{error}', delete_after=5)
        await respond(ctx, False)
        return

    """
    GIVEAWAY
    """
    def giveaway_start_message(self, description, gifter, endtime):
        # startup giveaway🎊
        title = f'🎉Giveaway Started🎉'
        embeds = generic_embed(
            title=title,
            desc=f'{description} given by {gifter.mention}\nReact with {self.emoji} to win!\n',
            color=Colours.CHANGE_G,
            fields=[],
            footer=f'Current: {current_time()}•Ends: {time_conv(endtime)}',
        )[0]
        return embeds

    @commands.group(name='giveaway', aliases=['raffle', ])
    @permissions.is_admin()
    async def _giveaway(self, ctx: commands.Context):
        """Bulk giveaway commands. Will just list any active.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'giveaway', only_global=True):
            return
        if isinstance(ctx.invoked_subcommand, type(None)):
            title = f'Current Giveaways'
            if len(self.bot.current_giveaways) == 0:
                desc = 'No active giveaways'
                fields = []
            else:
                desc = ''
                fields = [[key, val] for key, val in self.bot.current_giveaways.items()]
                for i, f in enumerate(fields):
                    f = await self.bot.pg.get_single_giveaways(f[0], True, self.bot.logger)
                    if not f:
                        continue
                    message = await ctx.channel.fetch_message(int(f['countdown_message_id']))
                    tmp = message.jump_url
                    time = time_conv(f['endtime'] - datetime.datetime.utcnow())
                    if time[-3:] == 'ago':
                        time = f'Ended {time}'
                    else:
                        time = f'Ends in {time}'
                    fields[i][1] = f'{f["content"]}\n[Giveaway Count]({tmp})\n{time}'
            embeds = generic_embed(title=title, desc=desc, fields=fields, footer=current_time(), colors=Colours.COMMANDS)
            for embed in embeds:
                await ctx.send(embed=embed)
            pass

    @_giveaway.command(name='create', aliases=['start', ])
    async def _giveawaycreate(self, ctx: commands.Context, num_winners: int,
                              time: str, gifter: str, *, description: str):
        """Start a new Giveaway.

        Parameters
        ----------
        num_winners: int
            number of winners
        time: str
            time from now for the giveaway to end supports
            #y#mo#w#d#h#m#s format
        gifter: str
            id/mention of the gifter

        Returns
        -------
        """
        if len(description) > 40:
            await respond(ctx, False)
            await ctx.send(embed=internalerrorembed(f'Description is too long. Try again'), delete_after=15)
            return
        # gather time
        try:
            time = datetime.timedelta(seconds=extract_time(time))  # noqa time in seconds from now
            currtime = datetime.datetime.utcnow()
            endtime = currtime + time
        except Exception as e:
            self.bot.logger.warning(f'Time set invalid {e}')
            await respond(ctx, False)
            await ctx.send(embed=internalerrorembed(f'Time set invalid {e}. Try again'), delete_after=15)
            return
        # gather user
        try:
            gifter = get_member(ctx, gifter)
        except discord.NotFound as e:
            self.bot.logger.warning(f'gifter invalid {e}')
            await ctx.send(embed=internalerrorembed(f'Couldn\'t set the gifter {e}.'), delete_after=15)
            return

        # startup giveaway🎊
        if num_winners > 1:
            embeds = self.giveaway_start_message(description + f'\n{num_winners} winners!', gifter, endtime)
        else:
            embeds = self.giveaway_start_message(description + f'\n{num_winners} winner!', gifter, endtime)
        msg = await ctx.send(embed=embeds)
        await msg.add_reaction(self.emoji)

        # now add to db and cache
        try:
            status = await self.bot.pg.add_giveaway(ctx.guild.id, ctx.channel.id, msg.id, gifter.id, description, num_winners, currtime, endtime, logger=self.bot.logger)
            if status:
                self.bot.current_giveaways[msg.id] = endtime
                await ctx.message.delete()
        except Exception as e:
            self.bot.logger.warning(f'Something went wrong {e}')
            await ctx.send(embed=panicerrorembed(f'Something went terribly wrong. {e}'), delete_after=15)
            return

        if self._giveaway_task.done():
            self._giveaway_task = self.bot.loop.create_task(self.giveaway_loop())
        return

    @_giveaway.command(name='cancel', aliases=['stop', 'quit'])
    async def _gcancel(self, ctx: commands.Context, message_id: int):
        """Cancel a giveaway early, no winners.

        Parameters
        ----------
        message_id: int
            id of the message to cancel. Has to be the countdown message

        Returns
        -------
        """
        try:
            message = await ctx.channel.fetch_message(message_id)
        except (discord.NotFound, discord.HTTPException) as e:
            await ctx.send(embed=internalerrorembed(f'Couldn\'t find message with ID {message_id} in the giveaway channel! {e}'), delete_after=15)
            await respond(ctx, False)
            return
        giveaway = await self.bot.pg.get_single_giveaways(message_id, True, self.bot.logger)
        if not giveaway:
            return
        if not await confirm(ctx, f'Are you sure you want to stop this giveaway with no winners: **{giveaway}**', 15):
            return
        await message.clear_reactions()
        await respond(ctx, False, message)
        embed = message.embeds[0]
        embed.title = f'🎉Giveaway Cancelled🎉'
        thing = giveaway['content']
        embed.description = f'{ctx.author.mention} cancelled the giveaway with no winners!'
        await message.edit(embed=embed)
        await self.giveaway_removal(ctx.channel, giveaway, [])
        await ctx.send(f'Giveaway has been removed', delete_after=15)
        await ctx.message.delete()
        return

    @_giveaway.command(name='end', aliases=['early', 'endearly'])
    async def _gend(self, ctx: commands.Context, message_id: int):
        """Stop a giveaway early, choose winners.

        Parameters
        ----------
        message_id: int
            id of the message to cancel. Has to be the countdown message

        Returns
        -------
        """
        try:
            message = await ctx.channel.fetch_message(message_id)
        except (discord.NotFound, discord.HTTPException) as e:
            await ctx.send(embed=internalerrorembed(f'Couldn\'t find message with ID {message_id} in the giveaway channel! {e}'), delete_after=15)
            await respond(ctx, False)
            return
        if message.id not in self.bot.current_giveaways.keys():
            return
        if not await confirm(ctx, f'Are you sure you want to stop this giveaway and choose winners: **{message.jump_url}**', 15):
            return
        giveaway = await self.bot.pg.get_single_giveaways(message_id, True, self.bot.logger)
        await self.bot.pg.update_giveaway(giveaway['countdown_message_id'], ['endtime'], [datetime.datetime.utcnow()], self.bot.logger)
        giveaway = await self.bot.pg.get_single_giveaways(message_id, True, self.bot.logger)
        await self.gteardown(giveaway)
        await ctx.message.delete()
        return

    @_giveaway.command(name='reroll')
    async def _reroll(self, ctx: commands.Context, message_id: int, num_winners: int):
        """Reroll a giveaway based on a message/giveaway ID.

        Parameters
        ----------
        message_id: int
            id of the message to reroll. Has to be the countdown message
        num_winners: int
            number of winners

        Returns
        -------
        """
        try:
            message = await ctx.channel.fetch_message(message_id)
        except (discord.NotFound, discord.HTTPException) as e:
            await ctx.send(embed=internalerrorembed(f'Couldn\'t find message with ID {message_id} in the giveaway channel! {e}'), delete_after=15)
            await respond(ctx, False)
            return

        # don't allow rerolling a giveaway which is running
        if message.id in self.bot.current_giveaways.keys():
            await ctx.send(embed=internalerrorembed('This giveaway is still running! Rerolling can only be done after it has ended.'), delete_after=15)
            await respond(ctx, False)
            return

        # gather giveaway
        try:
            giveaway = await self.bot.pg.get_single_giveaways(message_id, False, self.bot.logger)
            users = await self.roll_user(message, giveaway)
        except (AttributeError, IndexError) as e:
            await respond(ctx, False)
            return await ctx.send(embed=internalerrorembed(f'Couldn\'t find message with ID {message_id} in the giveaway channel! {e}'), delete_after=15)

        if not giveaway:
            await respond(ctx, False)
            return

        try:
            winner = await self.roll_user(message, giveaway)
            winner = winner[:min([num_winners, len(winner)])]
        except NoWinnerFound as e:
            await ctx.send(e)
            await respond(ctx, False)
            return
        else:
            content = ''
            if len(winner) == 0:
                await ctx.send(embed=internalerrorembed(f'Something went wrong rerolling{e}'), delete_after=15)
                return
            elif len(winner) == 1:
                content += f'The giveaway **{giveaway["content"]}** has been rerolled and {winner[0].mention} is a new winner!'
            else:
                content += f'The giveaway **{giveaway["content"]}** has been rerolled and {[w.mention for w in winner]} are the new winners!'
            await ctx.send(content)
            winner = [w.id for w in winner]
            await self.bot.pg.update_giveaway(giveaway['countdown_message_id'], ['winners_id'], [winner + giveaway['winners_id']], self.bot.logger)
        await ctx.message.delete()
        return

    async def giveaway_loop(self):
        # run until Config.__len__ returns 0
        try:
            # Data isn't loaded until ready
            await self.bot.wait_until_ready()
            coros = []
        except Exception as e:
            self.bot.logger.warning(f'Error with giveaway loop startup: {e}')
            return
        try:
            i = 0
            le = len(self.bot.current_giveaways)
            while i < le:
                keys = list(self.bot.current_giveaways.keys())
                message_id, endtime = keys[i], self.bot.current_giveaways[keys[i]]
                now = datetime.datetime.utcnow()
                remaining = endtime - now
                remaining = int(remaining.total_seconds())
                if remaining <= 0:
                    giveaway = await self.bot.pg.get_single_giveaways(message_id, True, self.bot.logger)
                    await self.gteardown(giveaway)
                else:
                    coros.append(await self.gtimer(message_id, remaining))
                i += 1
            if len(coros) > 0:
                await asyncio.gather(*coros)
        except Exception as e:
            self.bot.logger.warning(f'Error with giveaway loop: {e}\n```py\n{traceback.format_exc()}\n```')

    async def gtimer(self, message_id: int, remaining: int):
        """Helper function for starting the raffle countdown.

        This function will silently pass when the unique raffle id is not found or
        if a raffle is empty. It will call `gteardown` if the ID is still
        current when the sleep call has completed.
        Parameters
        ----------
        guild : Guild
            The guild object
        message_id : int
            giveaway message id
        remaining : int
            Number of seconds remaining until the raffle should end
        """
        await asyncio.sleep(remaining)
        giveaway = await self.bot.pg.get_single_giveaways(message_id, True, self.bot.logger)
        if giveaway:
            await self.gteardown(giveaway)

    async def gteardown(self, giveaway):
        try:
            winners = []
            guild = self.bot.get_guild(giveaway['guild_id'])
            channel = guild.get_channel(giveaway['channel_id'])
            message = await channel.fetch_message(giveaway['countdown_message_id'])
            message_id = message.id
        except discord.NotFound as e:
            pass
        except Exception as e:
            self.bot.logger.warning(f'Error with giveaway teardown: {e}')
        else:
            winners = await self.roll_user(message, giveaway)
        if not isinstance(winners, list):
            return
        if len(winners) > 0:
            winners = [w.id for w in winners]
            await self.bot.pg.update_giveaway(message_id, ['winners_id', ], [winners,], self.bot.logger)
            win_msg = await self.giveaway_message(channel, winners, giveaway)
            await self.bot.pg.update_giveaway(message_id, ['status', 'winner_message_id'], [True, win_msg.id], self.bot.logger)
            giveaway = await self.bot.pg.get_single_giveaways(message_id, False, self.bot.logger)
            await self.giveaway_complete(message, giveaway)
        await self.giveaway_removal(channel, giveaway, winners)
        pass

    async def roll_user(self, message: discord.Message, giveaway) -> discord.Member:
        # work on this to handle if num winners > num reactors
        try:
            reaction = next(filter(lambda x: x.emoji == self.emoji, message.reactions), None)
        except StopIteration:  # if a moderator deleted the emoji for some reason
            raise NoWinnerFound(f'Couldn\'t find giveaway emoji {self.emoji} on specified message')
            return []
        if isinstance(reaction, type(None)):
            return []
        try:
            users = [user for user in await reaction.users().flatten() if message.guild.get_member(user.id) and not user.bot]
        except Exception as e:
            return await message.channel.send(embed=internalerrorembed(f'Couldn\'t find users on message with ID {message.id} in the giveaway channel! {e}'))
            self.bot.logger.warning(f'Couldn\'t find users on message with ID {message.id} in the giveaway channel! {e}')
            return []
        if not users:
            raise NoWinnerFound('No human reacted with the giveaway emoji on this message')
            return []
        else:
            sampling = random.sample(users, min(len(users), giveaway['num_winners']))
            return sampling

    async def giveaway_removal(self, channel: discord.TextChannel, giveaway, winners: list):
        message_id = giveaway['countdown_message_id']
        del self.bot.current_giveaways[message_id]
        if len(winners) > 0:
            pass
        else:
            await self.bot.pg.update_giveaway(message_id, ['status', 'winners_id', 'winner_message_id'], [True, [], 0], self.bot.logger)
        pass

    async def giveaway_complete(self, message, giveaway):
        embed = message.embeds[0]
        winner = giveaway["winners_id"]
        winner = [await message.guild.fetch_member(x) for x in winner]
        embed.title = f'🎉Giveaway Ended🎉'
        thing = giveaway['content']
        if len(winner) == 1:
            embed.description = f'{winner[0].mention} won {thing}!'
        else:
            embed.description = f'\n{",".join([w.mention for w in winner])} won {thing}!'
        tmp = message.jump_url

        embed.description += f'\nCheckout [the win message]({tmp})'
        await message.edit(embed=embed)

    async def giveaway_message(self, channel, winners, giveaway):
        message = 'Congratulations '
        winners = list(map(lambda w: channel.guild.get_member(int(w)), winners))
        message += f','.join([x.mention for x in winners])
        message += f'. You won **{giveaway["content"]}**'
        message += f' DM <@{giveaway["gifter_id"]}>'
        return await channel.send(message)

    """
    Reaction Role Setup
    """
    class RDtype(commands.Converter):
        async def convert(self, ctx, argument):
            try:
                argument = str(argument).lower()
                dtype = ('role', 'channel', 'category').index(argument)
                return dtype
            except:
                raise commands.BadArgument(f'Dtype must be found within: ' + ','.join(('role', 'channel', 'category')) + f'\n{argument}') from None                    

    @commands.command(name='quickreact', aliases=['qr', ])
    @permissions.has_permissions(manage_server=True)
    async def _qr(self, ctx: commands.Context, dtype: RDtype, *, content: str):
        """Quickly setup react system.

        The reactions are on a group and destination type system. So you can group reactions together by a similar grouping. When using the quickreact, this auto setups a new group. Modify this via `reactgroup`. Notice the single quotes for the group name in the content parameter

        Parameters
        ----------
        dtype: str
            Type of the destinations for the reactions: role, channel, category
        content: str
            'group name' destination id/mention | ...

        Returns
        -------

        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'quickreact', only_global=True):
            return
        # gather groupname
        first_i, second_i = None, None
        try:
            first_i = content.index("'")
            second_i = content[first_i + 1:].index("'")
        except ValueError:
            group_name = ' \n'
        else:
            group_name = content[first_i + 1:second_i + 1] + '\n'
        # get to first param
        i = 0
        while not is_id(content[i]):
            i += 1
        content = content[i:].split('|')
        if len(content) > 20:
            content, left = content[0:20], content[20:]
            await ctx.send(f'Can only setup 20 at a time per message, so rerun the command with `{ctx.prefix}qr {"|".join(left)}`')
        react_message = await ctx.send('🚧This message is under construction. Will serve as the base for reaction system. Don\'t delete!🚧')
        guild_id = ctx.guild.id
        success = []
        failed = []
        newcontent = f'**{group_name}**\n'
        newcontent += '```\n'
        print(content)
        for i, dest in enumerate(content):
            i += int('1F1E6', 16)
            print(dest)
            dest = extract_id(dest)
            if dest in success:
                continue
            try:
                if dtype == 0:
                    target = ctx.guild.get_role(int(dest))
                    target._type = 'role'
                elif dtype >= 1:
                    target = ctx.guild.get_channel(int(dest))
                    target._type = 'Channel'
                if not target:
                    raise RuntimeError
            except Exception as e:
                print('Error in fetching:' + str(e))
                failed.append(dest)
                continue
            try:
                status = await self._radd(ctx,
                                     base_message_id=react_message.id,
                                     base_channel_id=react_message.channel.id,
                                     guild_id=guild_id,
                                     target_id=target.id,
                                     group_id=-1,
                                     group_name=group_name,
                                     name=target.name,
                                     dtype=dtype,
                                     url='',
                                     react_id=i,
                                     info='')
            except Exception as e:
                print('Error in adding:' + str(e))
                status = False
            if status:
                success.append(dest)
                self.bot.current_react.append(int(''.join([str(val) for val in [react_message.id, i]])))
                reaction = chr(i)
                print(reaction)
                await react_message.add_reaction(reaction)
                newcontent += f'{reaction}: {target._type} {target.name}\n'
            else:
                failed.append(dest)
        if len(success) > 0:
            newcontent += '```'
            await react_message.edit(content=newcontent)
            await ctx.message.delete()
        else:
            await ctx.send(embed=internalerrorembed(f'Something went wrong setting up the react system: {success}, {failed}'), delete_after=20)
            await respond(ctx, False)
            return

    @commands.group(name='reactsetup', aliases=['rs', ])
    @permissions.has_permissions(manage_server=True)
    async def _rsetup(self, ctx: commands.Context):
        """Complete react setup system.

        The reactions are on a group and destination type system. So you can group reactions together by a similar grouping. When using the quickreact, this auto setups a new group. Modify this via `reactgroup`. Notice the single quotes for the group name in the content parameter

        Parameters
        ----------
        dtype: str
            Type of the destinations for the reactions: role, channel, category
        content: str
            'group name' destination id : info about the role | ...

        Returns
        -------

        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx, 'reactsetup', only_global=True):
            return
        # gather groupname
        react_message = await ctx.send('🚧This message is under construction. Will serve as the base for reaction system. Don\'t delete!🚧')
        guild_id = ctx.guild.id
        success = []
        failed = []
        iterator_i = 0
        iterator_status = True
        while iterator_status:
            questions = {'What is the name of the group\'s target': '',
                         'What is the target (must match type)': 'id or mentionable',
                         'What is the type of the target': 'role',
                         'What is the name of the target (blank for target.name resolution)': '',
                         'What is the url for the target': '',
                         'What is the info for the target': ''}
            steps = await iterator(ctx, questions, 25, False)

    async def _rdisplay():
        pass
    async def _rlist():
        pass
    async def _radd(*args, **kwargs):
        return True
    async def _rdel():
        pass



if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
