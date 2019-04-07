"""Starbot Main File."""

# internal modules
import yaml
import datetime
from time import time, sleep
from logging import Formatter, INFO, StreamHandler, getLogger


# external modules
from discord.ext.commands import Bot

# relative modules
from cogs.utilities import Controller, permissions
from cogs.utilities.functions import current_time
from config import Config

# global attributes
__all__ = ('Starbot', )
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


class Starbot(Bot):

    def __init__(self, config, logger,
                 pg: Controller,
                 guild_settings: dict):
        """Initialization."""
        self.pg = pg
        self.guild_settings = {}
        self.start_time = current_time(True)
        self.logger = logger
        self.config = config
        super().__init__(command_prefix=self.get_prfx)


    @classmethod
    async def get_instance(cls):
        """
        async method to initialize the pg_utils class
        """
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
        return cls(Config, logger, pg, guild_settings)

    async def get_prfx(self, bot, message):
        try:
            return self.guild_settings[message.guild.id]['prefix']
        except Exception as e:
            self.logger.info(f'{e}')
            return '!'

    async def on_ready(self):
        try:
            self.guild_settings = await self.pg.get_guild_settings()
            self.logger.info(f'\nServers: {len(self.guild_settings)}\n'
                             f'Servers: {self.guild_settings.keys()}')
        except Exception as e:
            self.logger.warning(f'Issue getting server settings: {e}')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        self.logger.info(f'\nLogged in\n'
                         f'Name: {self.user.name}\n'
                         f'ID: {self.user.id}\n'
                         f'Version: {self.config["version"].value}\n'
                         f'Git Hash: {self.config["githash"].value}')

    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        if (int(ctx.author.id) == int(self.config.devel_id.value)) or\
           (int(ctx.author.id) == int(self.config.owner_id.value)):
            await self.process_commands(ctx)
        elif not await permissions.is_blacklisted(self, ctx):
            await self.process_commands(ctx)
        else:
            return
        if not self.guild_settings[ctx.guild.id]['invites_allowed'] and\
        ('discord.gg' in ctx.content):
            ctx.delete()
            return

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    print('Test Passed')

# end of code

# end of file
