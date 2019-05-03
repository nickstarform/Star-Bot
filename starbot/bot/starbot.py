"""Starbot Main File."""

# internal modules
import psutil
import datetime
from time import time, sleep
from logging import Formatter, INFO, StreamHandler, getLogger
import importlib
import sys
from collections import Counter

# external modules
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Bot

# relative modules
from cogs.utilities import Controller, permissions
from cogs.utilities.functions import current_time, flatten
from config import Config

# global attributes
__all__ = ('Starbot', )
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class Starbot(Bot):

    def __init__(self, config, logger,
                 pg: Controller,
                 guild_settings: dict, current_giveaways: dict, blglobal: list, react: list):
        """Initialization."""
        self.pg = pg
        self.guild_settings = guild_settings
        self._loaded_extensions = []
        self.current_giveaways = current_giveaways
        self.start_time = datetime.datetime.utcnow()
        self.logger = logger
        self.status = ['with Python', 'prefix s!']
        self.config = config
        self.proc = psutil.Process()
        self.blglobal = blglobal
        self.current_react = react

        # in case of even further spam, add a cooldown mapping
        # for people who excessively spam commands
        self.spam_control = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)

        # A counter to auto-ban frequent spammers
        # Triggering the rate limit 5 times in a row will auto-ban the user from the bot.
        self._auto_spam_count = Counter()

        super().__init__(command_prefix=self.get_prfx)

    @classmethod
    async def get_instance(cls):
        """Generator for db/cache."""
        # setup logger
        logger = getLogger('star-bot')
        console_handler = StreamHandler()
        console_handler.setFormatter(Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))  # noqa
        logger.addHandler(console_handler)
        logger.setLevel(INFO)
        # setup postgres
        pg = None
        while not pg:
            try:
                pg = await Controller.get_instance(
                    logger=logger, connect_kwargs=Config['psql_cred'].value)
            except Exception as e:
                logger.critical(f'Error initializing DB - trying again in 5 seconds')
                logger.debug(f'Error: {e}')
                sleep(5)
        guild_settings = await pg.get_guild_settings()
        current_giveaways = await pg.get_all_giveaways(True, logger)

        # initalize blacklisting
        # this is an effort to reduce db polling
        blglobal = await pg.get_all_blacklist_guild_global()
        logger.info(f'Blacklisted guilds: {blglobal}')
        tmp = await pg.get_all_blacklist_users_global()
        logger.info(f'Blacklisted users: {tmp}')
        blglobal += tmp
        blglobal = flatten(blglobal)
        react = []
        for guild in guild_settings:
            t = await pg.get_allguild_reacts(guild, logger)
            val = ''.join([str(val) for (key, val) in t.items()])
            if val:
                react.append(int(val))
        return cls(Config, logger, pg, guild_settings, current_giveaways, blglobal, react)

    async def get_prfx(self, bot, message):
        try:
            if not isinstance(message.guild, type(None)):
                return self.guild_settings[message.guild.id]['prefix']
            else:
                return 's!'
        except Exception as e:
            self.logger.info(f'{e}')
            return 's!'

    async def on_ready(self):
        try:
            self.logger.info(f'\nServers: {len(self.guild_settings)}\n'
                             f'Servers: {self.guild_settings.keys()}')
        except Exception as e:
            self.logger.warning(f'Issue getting server settings: {e}')
        self.logger.info(f'\nLogged in\n'
                         f'Name: {self.user.name}\n'
                         f'ID: {self.user.id}\n'
                         f'Version: {self.config["version"].value}\n'
                         f'Git Hash: {self.config["githash"].value}')
        i = 0
        delay = 10
        le = len(self.status)
        while i < le:
            le = len(self.status)
            status = self.status[i]
            await self.change_presence(activity=discord.Game(name=status))
            await asyncio.sleep(delay)
            i += 1
            if i >= len(self.status):
                await self.change_presence(activity=discord.Game(name=f'in {len(self.guild_settings)} guilds'))
                i = i % le
                await asyncio.sleep(delay)

    async def on_message(self, ctx):
        # user is bot, ignore
        if ctx.author.bot:
            return
        # check for prefix asking
        if not isinstance(ctx.guild, type(None)):
            if (self.user.id in [x.id for x in ctx.mentions]):
                if not (('prefix' in ctx.content.lower()) or ('help' in ctx.content.lower())):
                    return
                try:
                    await ctx.author.create_dm()
                    await ctx.author.dm_channel.send(f'The prefix is usually `s!`. DM <@{self.config.owner_id.value}> if something is awry or join the support server {self.bot.config.support_server.value}.')
                    return
                except:
                    return
        # user is dev or owner always run
        if (int(ctx.author.id) == int(self.config.devel_id.value)) or\
           (int(ctx.author.id) == int(self.config.owner_id.value)):
            await self.process_commands(ctx)
        # check if user global bl
        elif (ctx.author.id not in self.blglobal):
            if isinstance(ctx.guild, type(None)):
                # handle reports
                return
            # see if guild global bl
            if (ctx.guild.id in self.blglobal):
                await ctx.guild.leave()
                return
            # check if user/channel bl on guild level
            if  (((ctx.author.id not in self.guild_settings[ctx.guild.id]['blacklist_users']) and
                  (ctx.channel.id not in self.guild_settings[ctx.guild.id]['blacklist_channels'])) or
                 (ctx.author.id == ctx.guild.owner.id)):
                if not self.guild_settings[ctx.guild.id]['invites_allowed'] and ('discord.gg' in ctx.content):
                    await ctx.delete()
                    return
                await self.process_commands(ctx)
        else:
            return

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
