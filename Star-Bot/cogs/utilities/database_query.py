"""Database utility functions."""

# internal modules
from typing import Optional
import datetime
import random

# external modules
from asyncpg import Record, InterfaceError, create_pool
from asyncpg.pool import Pool

# relative modules
from config.config import Config
from cogs.utilities.database_create import make_tables
from cogs.utilities.functions import ModAction

# global attributes
__all__ = ('Controller',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def parse(record: Record) -> Optional[tuple]:
    """Parsing Record values.

    Parameters
    ----------
    record : Record
        The connection pool

    Returns
    ----------
    tuple
        Results from the record in tuple format
    """
    try:
        return tuple(record.values())
    except AttributeError:
        return None


class Controller():
    """Controller Constructor."""

    __slots__ = ('pool', 'logger', 'schema')

    def __init__(self, pool: Pool, logger, schema):
        """Initializer.

        Parameters
        ----------
        pool : Pool
            The connection pool
        logger : str
            The schema to use

        Returns
        ----------
        str
            Either the yaml token if required or false.
        """
        self.pool = pool
        self.schema = schema
        self.logger = logger

    @classmethod
    async def get_instance(cls, connect_kwargs: dict=None,
                           pool: Pool=None,
                           logger=None):
        """Constructing new instance of Controller.

        It will try to create the tables and return the controller

        Parameters
        ----------
        cls : class
            class method inputs the class
        connect_kwargs : kwargs for :func:`asyncpg.connection.connect` function
        pool : Pool
            The connection pool
        logger : str
            The schema to use

        Returns
        ----------
        Controller
            New instance of the controller
        str
            Either the yaml token if required or false.
        """
        schema = Config.psql_dbname.value
        assert logger, (
            'Please provide a logger to the data_controller'
        )
        assert connect_kwargs or pool, (
            'Please either provide a connection pool or '
            'a dict of connection data for creating a new '
            'connection pool.'
        )
        if not pool:
            try:
                pool = await create_pool(**connect_kwargs)
                logger.info('Made Connection pool')
            except InterfaceError as e:
                logger.error(f'{e}')
                raise e
        logger.info('Hold tight, tables being created')
        await make_tables(pool, schema)
        logger.info('Tables created.')
        return cls(pool, logger, schema)

    """
    GLOBAL PROPERTIES
    """
    async def add_blacklist_guild_global(self, guild_id: int, logger): # noqa
        """Add blacklisted guild.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.global
                SET guild_blacklist = (SELECT array_agg(distinct e)
                FROM unnest(array_append(guild_blacklist,$1::bigint)) e);
        """
        try:
            await self.pool.execute(sql, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding guild to blacklist {guild_id}: {e}')
            return False

    async def rem_blacklist_guild_global(self, guild_id: int, logger): # noqa
        """Remove blacklisted user.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        boolean
            success true or false
        """
        guild_list = await self.get_all_blacklist_guild_global()
        guild_list.remove(guild_id)
        sql = f"""
            UPDATE {self.schema}.global SET guild_blacklist = $1
        """
        try:
            await self.pool.execute(sql, guild_id)
        except Exception as e:
            logger.warning(f'Error removing blacklist guild: {e}')
            return False
        return True

    async def get_all_blacklist_guild_global(self): # noqa
        """Get all blacklisted guilds.

        Parameters
        ----------

        Returns
        ----------
        list
            list all of the blacklisted guilds
        """
        sql = f"""
            SELECT guild_blacklist FROM {self.schema}.global;
        """
        guild_list = await self.pool.fetchval(sql)
        return guild_list

    async def is_blacklist_guild_global(self, guild_id: int):
        """Check if guild is a blacklisted.

        Parameters
        ----------
        guild_id: int
            id for the guild to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.global WHERE guild_blacklist @> $2;
        """
        row = await self.pool.fetchrow(sql, [guild_id])
        return True if row else False

    async def add_blacklist_user_global(self, user_id: int, logger): # noqa
        """Add blacklisted user.

        Parameters
        ----------
        user_id: int
            id for the user

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.global
                SET user_blacklist = (SELECT array_agg(distinct e)
                FROM unnest(array_append(user_blacklist,$1::bigint)) e);
        """
        try:
            await self.pool.execute(sql, user_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding user to blacklist {user_id}: {e}')
            return False

    async def rem_blacklist_user_global(self, user_id: int, logger): # noqa
        """Remove blacklisted user.

        Parameters
        ----------
        user_id: int
            id for the user

        Returns
        ----------
        boolean
            success true or false
        """
        user_list = await self.get_all_blacklist_users_global()
        user_list.remove(user_id)
        sql = f"""
            UPDATE {self.schema}.global SET user_blacklist = $1
        """
        try:
            await self.pool.execute(sql, user_list)
        except Exception as e:
            logger.warning(f'Error removing blacklist user: {e}')
            return False
        return True

    async def get_all_blacklist_users_global(self): # noqa
        """Get all blacklisted channels.

        Parameters
        ----------

        Returns
        ----------
        list
            list all of the blacklisted users
        """
        sql = f"""
            SELECT user_blacklist FROM {self.schema}.global;
        """
        user_list = await self.pool.fetchval(sql)
        return user_list

    async def is_blacklist_user_global(self, user_id: int):
        """Check if user is a blacklisted.

        Parameters
        ----------
        user_id: int
            id for the user to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.global WHERE user_blacklist @> $2;
        """
        row = await self.pool.fetchrow(sql, [channel_id])
        return True if row else False

    async def add_report(self, user_id: int, message: str, logger): # noqa
        """Add report from user user.

        Parameters
        ----------
        user_id: int
            id for the user
        message: str
            message from the user

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            INSERT INTO {self.schema}.reports VALUES (user_id = $1,
                message = $2, id = DEFAULT, currtime = DEFAULT)
                ON CONFLICT (id, user_id) DO nothing;
        """
        try:
            await self.pool.execute(sql, user_id, message)
            return True
        except Exception as e:
            logger.warning(f'Error adding report {user_id} {message}: {e}')
            return False

    async def remove_report(self, user_id: int, place: int, logger): # noqa
        """Remove report from user.

        Parameters
        ----------
        user_id: int
            id for the user
        place: int
            placeholder on the report

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            DELETE FROM {self.schema}.reports WHERE user_id = $1 AND id = $2;
        """
        try:
            await self.pool.execute(sql, user_id, place)
        except Exception as e:
            logger.warning(f'Error removing report: {e}')
            return False
        return True

    async def get_all_reports(self): # noqa
        """Get all reports.

        Parameters
        ----------

        Returns
        ----------
        list
            list all of the reports sent
        """
        sql = f"""
            SELECT * FROM {self.schema}.reports;
        """
        report_list = await self.pool.fetchval(sql)
        return report_list

    """
    GUILD DB ACTIONS
    """

    async def add_server(self, guild_id: int):
        """Add guild to db.

        It will try to create the tables and return the controller

        Parameters
        ----------
        guild_id : int
            long int of the guild id

        Returns
        ----------
        """
        sql = f"""
            INSERT INTO {self.schema}.guilds VALUES
                (guild_id = $1, prefix = $2, voice_role_enabled = DEFAULT,
                voice_roles = $3, invites_allowed = DEFAULT,
                voice_logging = DEFAULT,
                voice_channels = $4, cleared_chanels = $5,
                modlog_enabled = DEFAULT,
                modlog_channels = $6, logging_enabled = DEFAULT,
                logging_channels = $7,
                welcome_message = $8, welcome_channels = $9,
                pm_welcome = DEFAULT,
                send_welcome_channel = DEFAULT, report_channel = $10,
                rules_channel = $11,
                joinable_roles = $12, blacklist_channels = $13,
                blacklist_users = $14,
                ban_footer = $15, kick_footer = $16, faq = $17,
                rules = $18, misc = $19,
                bots = $20, channels = $21, currtime = DEFAULT)
                ON CONFLICT (guild_id) DO nothing;
            """

        await self.pool.execute(
            sql,
            guild_id,  # guild_id BIGINT,
            '!',  # prefix varchar(2),
            [],  # voice_channels BIGINT ARRAY,
            [],  # cleared_chanels BIGINT ARRAY,
            [],  # modlog_channels BIGINT ARRAY,
            [],  # logging_channels BIGINT ARRAY,
            f'',  # welcome_message TEXT,
            [],  # welcome_channels BIGINT ARRAY,
            0,  # report_channel BIGINT,
            0,  # rules_channel BIGINT,
            [],  # joinable_roles BIGINT ARRAY
            [],  # blacklist_channels BIGINT ARRAY,
            [],  # blacklist_users BIGINT ARRAY,
            f'This is an automated message',  # ban_footer TEXT,
            f'This is an automated message',  # kick_footer TEXT,
            f'',  # faq TEXT,
            f'',  # rules TEXT,
            f'',  # misc TEXT,
            f'',  # bots TEXT,
            f''  # channels TEXT,
        )

    async def get_guild_settings(self):
        """Main settings for guild.

        Parameters
        ----------

        Returns
        ----------
        dict
            dictionary of the main settings for guilds
        """
        main = {}
        settings = (
            'guild_id',
            'prefix',
            'modlog_enabled',
            'voice_logging',
            'logging_enabled',
            'invites_allowed',
            'pm_welcome',
            'voice_role_enabled')
        sql = f"""
            SELECT {', '.join(settings)}
                FROM {self.schema}.guilds;
            """
        rets = await self.pool.fetch(sql)
        for row in rets:
            for i, setting in enumerate(settings):
                if i == 0:
                    main[row[setting]] = {}
                else:
                    main[row[setting]][setting] = row[setting]
        return main

    async def get_guild(self, guild_id: int, logger):
        """All settings for guild.

        Parameters
        ----------
        guild_id: int
            id for the guild
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        tuple
            tuple of results or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
            """
        try:
            return await self.pool.fetchrow(sql, guild_id)
        except Exception as e:
            logger.warning(f'Error getting guild settings {e}')
            return False

    async def get_all_joinable_roles(self, guild_id: int):
        """Return all joinable roles.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        list
            list of all joinable roles
        """
        sql = f"""
            SELECT joinable_roles FROM {self.schema}.guilds
            WHERE guild_id = $1;
        """
        role_list = await self.pool.fetchval(sql, guild_id)
        return role_list

    async def is_role_joinable(self, guild_id: int, role_id: int):
        """Check if role is joinable.

        Parameters
        ----------
        guild_id: int
            id for the guild
        role_id: int
            id for the role

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
                AND joinable_roles @> $2;
        """

        row = await self.pool.fetchrow(sql, guild_id, [role_id])
        return True if row else False

    async def add_joinable_role(self, guild_id: int, role_id: int,
                                logger):
        """Check if role is joinable.

        Parameters
        ----------
        guild_id: int
            id for the guild
        role_id: int
            id for the role
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET joinable_roles = (SELECT array_agg(distinct e)
                FROM unnest(array_append(joinable_roles,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, role_id, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding role <#{role_id}> to guild {guild_id}: {e}') # noqa
            return False

    async def remove_joinable_role(self, guild_id: int, role_id: int, logger):
        """Remove if role is joinable.

        Parameters
        ----------
        guild_id: int
            id for the guild
        role_id: int
            id for the role
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        role_list = await self.get_all_joinable_roles(guild_id)
        role_list.remove(role_id)
        sql = f"""
            UPDATE {self.schema}.guilds SET joinable_roles = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, role_list, guild_id)
        except Exception as e:
            logger.warning(f'Error removing roles: {e}')
            return False
        return True

    async def get_all_modlogs(self, guild_id: int):
        """Get All modlog channel.

        Returns a list of channel ids for posting mod actions

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        list
            list of channel ids
        """
        sql = f"""
            SELECT modlog_channels FROM {self.schema}.guilds
                WHERE guild_id = $1;
        """
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    async def is_modlog(self, guild_id: int, channel_id: int):
        """Check if channel is modlog.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel to check

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
                AND modlog_channels @> $2;
        """

        row = await self.pool.fetchrow(sql, guild_id, [role_id])
        return True if row else False

    async def add_modlog(self, guild_id: int, channel_id: int, logger):
        """Adding modlog channel.

        Adds a channel to the modlog channel array for the guild

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            channel to add
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET modlog_channels = (SELECT array_agg(distinct e)
                FROM unnest(array_append(modlog_channels,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        boolsql = f"""
            UPDATE {self.schema}.guilds
                SET modlog_enabled = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            await self.pool.execute(boolsql, True, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel <#{channel_id}> to guild {guild_id}: {e}') # noqa
            return False

    async def rem_modlog(self, guild_id: int, channel_id: int, logger):
        """Remove modlog channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            channel to add
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        channel_list = await self.get_all_modlogs(guild_id)
        channel_list.remove(channel_id)
        sql = f"""
            UPDATE {self.schema}.guilds
                SET modlog_channels = $1
                WHERE guild_id = $2;
        """
        boolsql = f"""
            UPDATE {self.schema}.guilds
                SET modlog_enabled = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_list, guild_id)
            if not channel_list:
                await self.pool.execute(boolsql, False, guild_id)
        except Exception as e:
            logger.warning(f'Error removing modlog channel <#{channel_id}>: {e}') # noqa
            return False
        return True

    async def set_prefix(self, guild_id: int, prefix: str, logger):
        """prefix.

        Parameters
        ----------
        guild_id: int
            id for the guild
        prefix: str
            prefix to set
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET prefix = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, prefix, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error setting prefix <{prefix}> for {guild_id}: {e}') # noqa
            return False

    async def set_welcome(self, guild_id: int, dm: bool, logger):
        """Set Welcome to channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        dm: bool
            set channel message for welcome
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET send_welcome_channel = $1
                WHERE guild_id = $2
        """

        try:
            await self.pool.execute(sql, dm, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Issue setting welcome message to channel: {e}')
            return False

    async def set_welcome_pm(self, guild_id: int, dm: bool, logger):
        """Set Welcome PM.

        Parameters
        ----------
        guild_id: int
            id for the guild
        dm: bool
            set dm for welcome
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET pm_welcome = $1
                WHERE guild_id = $2
        """

        try:
            await self.pool.execute(sql, dm, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Issue setting welcome_message: {e}')
            return False

    async def set_welcome_message(self, guild_id: int, message: str, logger):
        """Welcome messages.

        Parameters
        ----------
        guild_id: int
            id for the guild
        message: str
            welcome message
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET welcome_message = $1
                WHERE guild_id = $2
        """

        try:
            await self.pool.execute(sql, message, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Issue setting welcome_message: {e}')
            return False

    async def get_welcome_message(self, guild_id: int, logger):
        """Welcome messages.

        Parameters
        ----------
        guild_id: int
            id for the guild
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        str
            the welcome message
        """
        sql = f"""
            SELECT welcome_message from {self.schema}.guilds
                WHERE guild_id = $1
        """
        try:
            message = await self.pool.fetchrow(sql, guild_id)
            return message['welcome_message']
        except Exception as e:
            logger.warning(f'Error while getting welcome message: {e}')
            return None

    async def get_all_welcome_channels(self, guild_id: int, logger):
        """Get all welcome channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        list
            list all welcome channels
        """
        sql = f"""
            SELECT welcome_channels FROM {self.schema}.guilds
                WHERE guild_id = $1;
        """
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    async def is_welcome_channel(self, guild_id: int, channel_id: int):
        """Check if channel is welcome channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel to check

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
                AND welcome_channels @> $2;
        """

        row = await self.pool.fetchrow(sql, guild_id, [channel_id])
        return True if row else False

    async def add_welcome_channel(self, guild_id: int, channel_id: int, logger): # noqa
        """Add welcome channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET welcome_channels = (SELECT array_agg(distinct e)
                FROM unnest(array_append(welcome_channels,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_welcome_channel(self, guild_id: int, channel_id: int, logger): # noqa
        """Remove welcome channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        channel_list = await self.get_all_welcome_channels(guild_id, logger)
        channel_list.remove(channel_id)
        sql = f"""
            UPDATE {self.schema}.guilds
                SET welcome_channels = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_list, guild_id)
        except Exception as e:
            logger.warning(f'Error removing modlog channel: {e}')
            return False
        return True

    async def set_ban_footer(self, guild_id: int, message: str, logger):
        """Setting the ban message footer.

        Parameters
        ----------
        guild_id: int
            id for the guild
        message: str
            message for the ban footer

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET ban_footer = $1
                WHERE guild_id = $2
        """

        try:
            await self.pool.execute(sql, message, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Issue setting ban footer: {e}')
            return False

    async def get_ban_footer(self, guild_id: int, logger):
        """Get the ban message footer.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        str
            the ban message
        """
        sql = f"""
            SELECT ban_footer from {self.schema}.guilds
                WHERE guild_id = $1
        """
        try:
            message = await self.pool.fetchrow(sql, guild_id)
            return message['ban_footer']
        except Exception as e:
            logger.warning(f'Error while getting ban footer: {e}')
            return None

    async def set_kick_footer(self, guild_id: int, message: str, logger):
        """Setting the kick message footer.

        Parameters
        ----------
        guild_id: int
            id for the guild
        message: str
            message for the kick footer

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET kick_footer = $1
                WHERE guild_id = $2
        """

        try:
            await self.pool.execute(sql, message, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Issue setting kick footer: {e}')
            return False

    async def get_kick_footer(self, guild_id: int, logger):
        """Get the kick message footer.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        str
            the kick message
        """
        sql = f"""
            SELECT kick_footer from {self.schema}.guilds
                WHERE guild_id = $1
        """
        try:
            message = await self.pool.fetchrow(sql, guild_id)
            return message['kick_footer']
        except Exception as e:
            logger.warning(f'Error while getting kick footer: {e}')
            return None

    async def get_all_logger_channels(self, guild_id: int):
        """Get logging channels.

        Parameters
        ----------
        guild_id: int
            id for the guild
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        list
            list of all the logging channels for a guild
        """
        sql = f"""
            SELECT logging_channels FROM {self.schema}.guilds
                WHERE guild_id = $1;
        """
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    async def is_logger_channel(self, guild_id: int, channel_id: int):
        """Check if channel is a logging channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel to check

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
                AND logging_channels @> $2;
        """
        row = await self.pool.fetchrow(sql, guild_id, [channel_id])
        return True if row else False

    async def set_logging_enabled(self, guild_id: int, status: bool):
        """Check logging status.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET logging_enabled = $2
                WHERE guild_id = $1;
        """
        return await self.pool.fetchval(sql, guild_id, status)

    async def add_logger_channel(self, guild_id: int, channel_id: int, logger):
        """Add logging channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET logging_channels = (SELECT array_agg(distinct e)
                FROM unnest(array_append(logging_channels,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        boolsql = f"""
            UPDATE {self.schema}.guilds
                SET logging_enabled = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            await self.pool.execute(boolsql, True, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_logger_channel(self, guild_id: int, channel_id: int, logger):
        """Remove logging channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        channel_list = await self.get_all_logger_channels(guild_id)
        channel_list.remove(channel_id)
        sql = f"""
            UPDATE {self.schema}.guilds
                SET logging_channels = $1
                WHERE guild_id = $2;
        """
        boolsql = f"""
            UPDATE {self.schema}.guilds
                SET logging_enabled = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_list, guild_id)
            if not channel_list:
                await self.pool.execute(boolsql, False, guild_id)
        except Exception as e:
            logger.warning(f'Error removing logging channel: {e}')
            return False
        return True

    async def is_voice_enabled(self, guild_id: int):
        """Check voice enabled.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT voice_role_enabled FROM {self.schema}.guilds
                WHERE guild_id = $1;
        """
        return await self.pool.fetchval(sql, guild_id)

    async def set_voice_enabled(self, guild_id: int, status: bool):
        """Check voice status.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET voice_role_enabled = $2
                WHERE guild_id = $1;
        """
        return await self.pool.fetchval(sql, guild_id, status)

    async def get_all_voice_channels(self, guild_id: int):
        """Get voice all channels.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        list
            list of all the voice channels
        """
        sql = f"""
            SELECT voice_channels FROM {self.schema}.guilds
                WHERE guild_id = $1;
        """
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    async def is_voice_channel(self, guild_id: int, channel_id: int):
        """Check if channel is a logging channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel to check

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
                AND voice_channels @> $2;
        """
        row = await self.pool.fetchrow(sql, guild_id, [channel_id])
        return True if row else False

    async def add_voice_channel(self, guild_id: int, channel_id: int, logger):
        """Add a channel to the voice channel array for the server.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel to add

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET voice_channels = (SELECT array_agg(distinct e)
                FROM unnest(array_append(voice_channels,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        boolsql = f"""
            UPDATE {self.schema}.guilds
                SET voice_logging = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            await self.pool.execute(boolsql, True, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_voice_channel(self, guild_id: int, channel_id: int, logger):
        """Remove a channel to the voice channel array for the server.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel to remove

        Returns
        ----------
        boolean
            true or false
        """
        channel_list = await self.get_all_voice_channels(guild_id)
        channel_list.remove(channel_id)
        sql = f"""
            UPDATE {self.schema}.guilds
                SET voice_channels = $1
                WHERE guild_id = $2;
        """
        boolsql = f"""
            UPDATE {self.schema}.guilds
                SET voice_logging = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_list, guild_id)
            if not channel_list:
                await self.pool.execute(boolsql, False, guild_id)
        except Exception as e:
            logger.warning(f'Error removing logging channel: {e}')
            return False
        return True

    async def get_all_voice_roles(self, guild_id: int):
        """Get all voice roles.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        list
            list of voice roles
        """
        sql = f"""
            SELECT voice_role FROM {self.schema}.guilds
                WHERE guild_id = $1;
        """
        role_list = await self.pool.fetch(sql, guild_id)
        return role_list

    async def is_voice_role(self, guild_id: int, role_id: int):
        """Check if role is a voice role.

        Parameters
        ----------
        guild_id: int
            id for the guild
        role_id: int
            id for the role to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
                AND voice_role @> $2;
        """
        row = await self.pool.fetchrow(sql, guild_id, [role_id])
        return True if row else False

    async def add_voice_role(self, guild_id: int, role_id: int):
        """Add voice role to array.

        Parameters
        ----------
        guild_id: int
            id for the guild
        role_id: int
            id for the role to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET voice_roles = (SELECT array_agg(distinct e)
                FROM unnest(array_append(voice_roles,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        boolsql = f"""
            UPDATE {self.schema}.guilds
                SET voice_role_enabled = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, role_id, guild_id)
            await self.pool.execute(boolsql, True, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding role to server {guild_id}: {e}')
            return False

    async def rem_voice_role(self, guild_id: int, role_id: int, logger):
        """Remove a remove voice role array for the server.

        Parameters
        ----------
        guild_id: int
            id for the guild
        role_id: int
            id for the role to remove

        Returns
        ----------
        boolean
            true or false
        """
        role_list = await self.get_all_voice_roles(guild_id)
        role_list.remove(channel_id)
        sql = f"""
            UPDATE {self.schema}.guilds
                SET voice_channels = $1
                WHERE guild_id = $2;
        """
        boolsql = f"""
            UPDATE {self.schema}.guilds
                SET voice_logging = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_list, guild_id)
            if not channel_list:
                await self.pool.execute(boolsql, False, guild_id)
        except Exception as e:
            logger.warning(f'Error removing logging channel: {e}')
            return False
        return True

    async def set_channels(self, guild_id: int, message: str):
        """Set channel flag.

        Parameters
        ----------
        guild_id: int
            id for the guild
        message: str
            message to store

        Returns
        ----------
        boolean
            status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET channels = $1
                WHERE guild_id = $2;
        """
        await self.pool.execute(sql, message, guild_id)

    async def set_bots(self, guild_id: int, message: str):
        """Set bots flag.

        Parameters
        ----------
        guild_id: int
            id for the guild
        message: str
            message to store

        Returns
        ----------
        boolean
            status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET bots = $1
                WHERE guild_id = $2;
        """
        await self.pool.execute(sql, message, guild_id)

    async def set_misc(self, guild_id: int, message: str):
        """Set misc flag.

        Parameters
        ----------
        guild_id: int
            id for the guild
        message: str
            message to store

        Returns
        ----------
        boolean
            status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET misc = $1
                WHERE guild_id = $2;
        """
        await self.pool.execute(sql, message, guild_id)

    async def set_faq(self, guild_id: int, message: str):
        """Set faq flag.

        Parameters
        ----------
        guild_id: int
            id for the guild
        message: str
            message to store

        Returns
        ----------
        boolean
            status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET faq = $1
                WHERE guild_id = $2;
        """
        await self.pool.execute(sql, message, guild_id)

    async def set_rules(self, guild_id: int, message: str):
        """Set rules flag.

        Parameters
        ----------
        guild_id: int
            id for the guild
        message: str
            message to store

        Returns
        ----------
        boolean
            status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET rules = $1
                WHERE guild_id = $2;
        """
        await self.pool.execute(sql, message, guild_id)

    async def set_channels(self, guild_id: int, message: str):
        """Set channel flag.

        Parameters
        ----------
        guild_id: int
            id for the guild
        message: str
            message to store

        Returns
        ----------
        boolean
            status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET channels = $1
                WHERE guild_id = $2;
        """
        await self.pool.execute(sql, message, guild_id)

    async def get_bots(self, guild_id: int):
        """Get bots flag.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        str
            the message
        """
        sql = f"""
            SELECT bots FROM {self.schema}.guilds WHERE guild_id = $1;
        """
        return await self.pool.execute(sql, guild_id)

    async def get_misc(self, guild_id: int):
        """Get misc flag.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        str
            the message
        """
        sql = f"""
            SELECT misc FROM {self.schema}.guilds WHERE guild_id = $1;
        """
        return await self.pool.execute(sql, guild_id)

    async def get_faq(self, guild_id: int):
        """Get rules flag.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        str
            the message
        """
        sql = f"""
            SELECT rules FROM {self.schema}.guilds WHERE guild_id = $1;
        """
        return await self.pool.execute(sql, guild_id)

    async def get_rules(self, guild_id: int):
        """Get rules flag.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        str
            the message
        """
        sql = f"""
            SELECT rules FROM {self.schema}.guilds WHERE guild_id = $1;
        """
        return await self.pool.execute(sql, guild_id)

    async def set_invites_allowed(self, guild_id: int, status: bool):
        """Set are invites allowed from no mods.

        Parameters
        ----------
        guild_id: int
            id for the guild
        status: bool

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET invites_allowed = $1
                WHERE guild_id = $2;
        """
        await self.pool.execute(sql, status, guild_id)

    async def add_blacklist_channel(self, guild_id: int, channel_id: int, logger): # noqa
        """Add blacklisted channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel to add

        Returns
        ----------
        list
            list all of the blacklisted channels
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET blacklist_channels = (SELECT array_agg(distinct e)
                FROM unnest(array_append(blacklist_channels,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_blacklist_channel(self, guild_id: int, channel_id: int, logger): # noqa
        """Remove blacklisted channel.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel to remove

        Returns
        ----------
        list
            list all of the blacklisted channels
        """
        channel_list = await self.get_all_blacklist_channels(guild_id)
        channel_list.remove(channel_id)
        sql = f"""
            UPDATE {self.schema}.guilds
                SET blacklist_channels = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_list, guild_id)
        except Exception as e:
            logger.warning(f'Error removing blacklist channel: {e}')
            return False
        return True

    async def get_all_blacklist_channels(self, guild_id: int): # noqa
        """Get all blacklisted channels.

        Parameters
        ----------
        guild_id: int
            id for the guild

        Returns
        ----------
        list
            list all of the blacklisted channels
        """
        sql = f"""
            SELECT blacklist_channels FROM {self.schema}.guilds
                WHERE guild_id = $1;
        """
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    async def is_blacklist_channel(self, guild_id: int, channel_id: int):
        """Check if channel is a blacklisted.

        Parameters
        ----------
        guild_id: int
            id for the guild
        channel_id: int
            id for the channel to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
                AND blacklist_channels @> $2;
        """
        row = await self.pool.fetchrow(sql, guild_id, [channel_id])
        return True if row else False

    """
    Moderations
    """
    async def get_moderation_index(self, guild_id: int, user_id: int, logger):
        """Get index for moderation db.

        Parameters
        ----------
        guild_id: int
            guild id
        user_id: int
            user id

        Returns
        -------
        int
            index of next valid moderation for the user
        """
        sql = f"""
            SELECT id FROM {self.schema}.warnings WHERE
                guild_id = $1 AND user_id = $2 ORDER BY id DESC LIMIT 1;
        """
        try:
            return await self.pool.fetch(sql, guild_id, user_id) + 1
        except Exception as e:
            logger.warning(f'Error indexing warnings: {e}')
            return 0

    async def get_moderation_count(self, guild_id: int, user_id: int,
                                   include: bool=False):
        """Gather mod actions.

        Parameters
        ----------
        guild_id: int
            id for the guild
        user_id: int
            id for the user to check
        include: bool
            true false to include actions that were forgiven

        Returns
        ----------
        int
            number of moderations taken, including forgiven
        """
        if include:
            sql = f"""
                SELECT COUNT(userid) FROM {self.schema}.moderation
                    WHERE guild_id = $1 AND userid = $2;
            """
        else:
            sql = f"""
                SELECT COUNT(userid) FROM {self.schema}.moderation
                    WHERE guild_id = $1 AND userid = $2 AND forgiven = False;
            """
        return await self.pool.fetchval(sql, guild_id, user_id, include)

    async def add_single_moderation(self, guild_id: int, mod_id: int,
                                    target_id: int, reason: str,
                                    action_type: ModAction):
        """Add moderation to db.

        Parameters
        ----------
        guild_id: int
            id for the guild
        mod_id: int
            id for the mod
        target_id: int
            id for the user to moderate
        reason: str
            reason for the mod
        action_type: ModAction
            Indicate the type of action

        Returns
        ----------
        bool
            success true or false
        """
        index = await self.get_moderation_index(guild_id, target_id, logging)
        sql = f"""
            INSERT INTO {self.schema}.moderation VALUES (guild_id = $1,
                mod_id = $2, user_id = $3, index_id = $4,
                reason = $5, type = $6, forgiven = DEFAULT, logtime = DEFAULT);
        """
        await self.pool.execute(
            sql,
            guild_id,
            mod_id,
            target_id,
            index,
            reason,
            action_type.value
        )

    async def get_all_moderation(self, guild_id: int, user_id: int,
                                 logger, recent: bool=False):
        """Get all moderation db.

        Parameters
        ----------
        guild_id: int
            id for the guild
        target_id: int
            id for the user to moderate
        recent: bool
            true or false to get only last 6 months

        Returns
        ----------
        list
            list of moderations
        """
        if recent:
            sql = f"""
                SELECT * FROM {self.schema}.moderation
                    WHERE guild_id = $1 AND user_id = $2 AND
                    (logtime >= DATE_TRUNC('month',
                    now()) - INTERVAL '6 month');
            """
        else:
            sql = f"""
                SELECT * FROM {self.schema}.moderation
                    WHERE guild_id = $1 AND user_id = $2;
            """
        try:
            return await self.pool.fetch(sql, guild_id, user_id)
        except Exception as e:
            logger.warning(f'Error retrieving moderations {e}')
            return False

    async def get_single_modaction(self, guild_id: int, user_id: int,
                                   index: int, logger):
        """Get a single moderation db.

        Parameters
        ----------
        guild_id: int
            id for the guild
        user_id: int
            id for the user to moderate
        index: int
            index to grab

        Returns
        ----------
        list
            list of columns from single modaction
        """
        sql = f"""
            SELECT * FROM {self.schema}.moderation
                WHERE guild_id = $1 AND user_id = $2 AND index_id = $3;
        """
        try:
            return await self.pool.fetch(sql, guild_id, user_id, index)
        except Exception as e:
            logger.warning(f'Error retrieving moderation action {e}')
            return False

    async def set_single_modaction(self, guild_id: int, target_id: int,
                                   mod_id: int, index: int,
                                   action_type: ModAction,
                                   reason: str, status: bool, logger):
        """Set a single moderation db.

        Parameters
        ----------
        guild_id: int
            id for the guild
        target_id: int
            id for the user to moderate
        mod_id: int
            id for the mod
        index: int
            index to grab
        reason: str
            reason for the mod
        action_type: ModAction
            Indicate the type of action
        status: bool
            forgiven true false status

        Returns
        ----------
        int
            number of modactions
        """
        sql = f"""
            UPDATE {self.schema}.moderation
                SET reason = $1, mod_id = $2, type = $3,
                forgiven = $4 WHERE guild_id = $5 AND
                user_id = $6 AND index_id = $7;
        """
        try:
            await self.pool.execute(sql, reason, mod_id,
                                    action_type.value,
                                    status, guild_id,
                                    user_id, index)
        except Exception as e:
            logger.warning(f'Error retrieving moderation action {e}')
        return await self.get_moderation_count(guild_id, user_id, False)

    async def delete_single_modaction(self, guild_id: int, forg_mod_id: int,
                                      user_id: int, index: int, logger):
        """Forgive a single moderation db.

        I opted to not include a way to delete modactions
        and rather forgive them.

        Parameters
        ----------
        guild_id: int
            id for the guild
        target_id: int
            id for the user to moderate
        mod_id: int
            id for the mod
        index: int
            index to grab

        Returns
        ----------
        int
            number of modactions
        """
        forgiven_message = f' **Forgiven by <@{forg_mod_id}>** ' +\
            'on {datetime.datetime.now()}'
        original = await self.get_single_modaction(guild_id, user_id,
                                                   index, logger)
        return await self.set_single_modaction(original[0:4],
                                               original[4] + forgiven_message,
                                               True, logger)

    """
    Warnings
    """
    async def get_warning_index(self, guild_id: int, user_id: int, logger):
        """Get index for warnings db.

        Parameters
        ----------
        guild_id: int
            guild id
        user_id: int
            user id

        Returns
        -------
        int
            index of next valid warning for the user
        """
        sql = f"""
            SELECT id FROM {self.schema}.warnings WHERE
                guild_id = $1 AND user_id = $2 ORDER BY id DESC LIMIT 1;
        """
        try:
            return await self.pool.fetch(sql, guild_id, user_id) + 1
        except Exception as e:
            logger.warning(f'Error indexing warnings: {e}')
            return 0

    async def get_warning_count(self, guild_id: int, user_id: int,
                                include: bool):
        """Gather warning count.

        Parameters
        ----------
        guild_id: int
            id for the guild
        user_id: int
            id for the user to check
        include: bool
            true false to include actions that were forgiven

        Returns
        ----------
        int
            number of warnings, including forgiven
        """
        if include:
            sql = f"""
                SELECT COUNT(userid) FROM {self.schema}.warnings
                    WHERE guild_id = $1 AND userid = $2;
            """
        else:
            sql = f"""
                SELECT COUNT(userid) FROM {self.schema}.warnings
                    WHERE guild_id = $1 AND userid = $2 AND forgiven = False;
            """
        return await self.pool.fetchval(sql, guild_id, user_id, include)

    async def add_single_warning(self, guild_id: int, mod_id: int,
                                 target_id: int, reason: str,
                                 major: bool):
        """Add warning to db.

        Parameters
        ----------
        guild_id: int
            id for the guild
        mod_id: int
            id for the mod
        target_id: int
            id for the user to warning
        reason: str
            reason for the warning
        major: bool
            Indicate the type of action

        Returns
        ----------
        bool
            success true or false
        """
        index = await self.get_warning_index(guild_id, target_id, logging)
        sql = f"""
            INSERT INTO {self.schema}.warnings VALUES (guild_id = $1,
                mod_id = $2, user_id = $3, index_id = $4,
                reason = $5, major = $6, forgiven = DEFAULT,
                logtime = DEFAULT);
        """
        await self.pool.execute(
            sql,
            guild_id,
            mod_id,
            target_id,
            index,
            reason,
            major
        )

    async def get_all_warnings(self, guild_id: int, user_id: int,
                               logger, recent: bool=False):
        """Get all warnings db.

        Parameters
        ----------
        guild_id: int
            id for the guild
        target_id: int
            id for the user to warn
        recent: bool
            true or false to get only last 6 months

        Returns
        ----------
        list
            list of warnings
        """
        if recent:
            sql = f"""
                SELECT * FROM {self.schema}.warnings
                    WHERE guild_id = $1 AND user_id = $2 AND
                    (logtime >= DATE_TRUNC('month',
                    now()) - INTERVAL '6 month');
            """
        else:
            sql = f"""
                SELECT * FROM {self.schema}.warnings
                    WHERE guild_id = $1 AND user_id = $2;
            """
        try:
            return await self.pool.fetch(sql, guild_id, user_id)
        except Exception as e:
            logger.warning(f'Error retrieving warnings {e}')
            return False

    async def get_single_warning(self, guild_id: int, user_id: int,
                                 index: int, logger):
        """Get a single warning db.

        Parameters
        ----------
        guild_id: int
            id for the guild
        user_id: int
            id for the user to warn
        index: int
            index to grab

        Returns
        ----------
        list
            list of columns from single warning
        """
        sql = f"""
            SELECT * FROM {self.schema}.warnings
                WHERE guild_id = $1 AND user_id = $2 AND index_id = $3;
        """
        try:
            return await self.pool.fetch(sql, guild_id, user_id, index)
        except Exception as e:
            logger.warning(f'Error retrieving warning {e}')
            return False

    async def set_single_warning(self, guild_id: int, target_id: int,
                                 mod_id: int, index: int, major: bool,
                                 reason: str, status: bool, logger):
        """Set a single moderation db.

        Parameters
        ----------
        guild_id: int
            id for the guild
        target_id: int
            id for the user to warn
        mod_id: int
            id for the mod
        index: int
            index to grab
        reason: str
            reason for the warning
        major: bool
            Indicate the type of action
        status: bool
            forgiven true false status

        Returns
        ----------
        int
            number of warnings
        """
        sql = f"""
            UPDATE {self.schema}.warnings
                SET reason = $1, mod_id = $2, major = $3,
                forgiven = $4 WHERE guild_id = $5 AND
                user_id = $6 AND index_id = $7;
        """
        try:
            await self.pool.execute(sql, reason, mod_id,
                                    major,
                                    status, guild_id,
                                    user_id, index)
        except Exception as e:
            logger.warning(f'Error setting warnings {e}')
        return await self.get_warning_count(guild_id, user_id, False)

    async def delete_single_warning(self, guild_id: int, forg_mod_id: int,
                                    user_id: int, index: int, logger):
        """Forgive a single warnings db.

        I opted to not include a way to delete warnings
        and rather forgive them.

        Parameters
        ----------
        guild_id: int
            id for the guild
        target_id: int
            id for the user to warn
        mod_id: int
            id for the mod
        index: int
            index to grab

        Returns
        ----------
        int
            number of warnings
        """
        forgiven_message = f' **Forgiven by <@{forg_mod_id}>** ' +\
            'on {datetime.datetime.now()}'
        original = await self.get_single_warning(guild_id, user_id,
                                                 index, logger)
        return await self.set_single_warning(original[0:4],
                                             original[4] + forgiven_message,
                                             True, logger)

    """
    JOIN_INFO
    """
    async def add_single_joininfo(self, target_id: int, info: str, logger):
        """Add a single joininfo db.

        Parameters
        ----------
        target_id: int
            id for the target
        info: str
            info about the joinable

        Returns
        ----------
        list
            list of columns from single target_id
        """
        sql = f"""
            INSERT INTO {self.schema}.joinableinfo
                VALUES (target_id = $1, info = $2, currtime = DEFAULT);
        """
        try:
            await self.pool.execute(sql, target_id, info)
        except Exception as e:
            logger.warning(f'Error retrieving join info {e}')
            return False
        return True

    async def get_single_joininfo(self, target_id: int, logger):
        """Get a single warning db.

        Parameters
        ----------
        target_id: int
            id for the target

        Returns
        ----------
        list
            list of columns from single target_id
        """
        sql = f"""
            SELECT * FROM {self.schema}.joinableinfo
                WHERE target_id = $1;
        """
        try:
            return await self.pool.fetch(sql, target_id)
        except Exception as e:
            logger.warning(f'Error retrieving join info {e}')
            return False
        return True

    async def set_single_joininfo(self, target_id: int, info: str, logger):
        """Set a single moderation db.

        Parameters
        ----------
        target_id: int
            id for the target
        info: str
            info about the joinable

        Returns
        ----------
        bool
            success true false
        """
        sql = f"""
            UPDATE {self.schema}.joinableinfo
                SET info = $1 WHERE target_id = $2;
        """
        try:
            await self.pool.execute(sql, info, target_id)
        except Exception as e:
            logger.warning(f'Error setting joininfo {e}')
            return False
        return True

    async def delete_single_joininfo(self, target_id: int, logger):
        """Remove joininfo from DB if parent is deleted.

        Parameters
        ----------
        target_id: int
            id for the target

        Returns
        ----------
        bool
            success true false
        """
        sql = f"""
            DELETE FROM {self.schema}.joinableinfo
                WHERE target_id = $1;
        """
        try:
            await self.pool.execute(sql, target_id)
        except Exception as e:
            logger.warning(f'Error removing joininfo: {e}')
            return False
        return True

    """
    QUOTES
    """
    async def get_allquotedusers(self, guild_id: int, logger):
        """Get all users that were quoted.

        Parameters
        ----------
        guild_id: int
            guild id

        Returns
        -------
        list
            list of user id
        """
        sql = f"""
            SELECT quoted_id FROM {self.schema}.quotes
                WHERE guild_id = $1;
        """
        try:
            return await set(self.pool.fetchall(sql, guild_id))
        except Exception as e:
            logger.warning(f'Error getting quoted users: {e}')
            return False

    async def get_quote_index(self, guild_id: int, logger):
        """Get index for quote db.

        Parameters
        ----------
        guild_id: int
            guild id
        quoted_id: int
            quoted user to poll

        Returns
        -------
        int
            index of next valid quote for the user
        """
        sql = f"""
            SELECT id FROM {self.schema}.quotes WHERE
                guild_id = $1 ORDER BY id DESC LIMIT 1;
        """
        try:
            return await self.pool.fetch(sql, guild_id) + 1
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return 0

    async def hit_single_quote(self, guild_id: int, qid: int, logger):
        """Toggle a hit db.

        Parameters
        ----------
        guild_id: int
            guild id
        qid: int
            quote id

        Returns
        ----------
        bool
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.quotes SET hits = hits + 1
                WHERE guild_id = $1 AND id = $2;
        """
        try:
            return await self.pool.execute(sql, guild_id, qid)
        except Exception as e:
            logger.warning(f'Error hitting quote {e}')
            return False
        return True

    async def get_single_quote(self, guild_id: int, qid: int,
                               to_hit: bool, logger):
        """Get a single quote db.

        Parameters
        ----------
        guild_id: int
            guild id
        qid: int
            quote id
        to_hit: bool
            whether or not to hit the quote

        Returns
        ----------
        list
            list of columns from single quote
        """
        if to_hit:
            await self.hit_single_quote(guild_id, qid, logger)
        sql = f"""
            SELECT * FROM {self.schema}.quotes
                WHERE guild_id = $1 AND id = $2;
        """
        try:
            return await self.pool.fetchall(sql, guild_id, qid)
        except Exception as e:
            logger.warning(f'Error retrieving quote {e}')
            return False
        return True

    async def set_single_quote(self, guild_id: int, quoted_id: int,
                               qid: int, origin_id: int,
                               creator_id: int, content: str, logger):
        """Set a single quote db.

        Parameters
        ----------
        guild_id: int
            guild id
        quoted_id: int
            quoted user id
        qid: int
            quote uniq id
        origin_id: int
            id of message that marks origin
        creator_id: int
            user that created quote
        content: str
            content of quote

        Returns
        ----------
        bool
            success true false
        """
        sql = f"""
            UPDATE {self.schema}.quotes
                SET content = $1, origin_id = $2, quoted_id = $3,
                hits = 0  WHERE guild_id = $4 AND id = $5;
        """
        try:
            await self.pool.execute(sql, content, origin_id,
                                    quoted_id, guild_id, qid)
        except Exception as e:
            logger.warning(f'Error setting quote {e}')
            return False
        return True

    async def delete_single_quote(self, guild_id: int, qid: int, logger):
        """Remove quote from DB.

        Parameters
        ----------
        guild_id: int
            guild id
        qid: int
            quote uniq id

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            DELETE FROM {self.schema}.quotes
                WHERE guild_id = $1 AND id = $2;
        """
        try:
            await self.pool.execute(sql, guild_id, qid)
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False
        return True

    async def add_single_quote(self, guild_id: int, quoted_id: int,
                               origin_id: int, creator_id: int,
                               content: str, logger):
        """Add a single quote db.

        Parameters
        ----------
        guild_id: int
            guild id
        quoted_id: int
            quoted user id
        origin_id: int
            id of message that marks origin
        creator_id: int
            user that created quote
        content: str
            content of quote

        Returns
        -------
        bool
            success true false
        """
        index = await self.get_quote_index(guild_id)
        sql = f"""
            INSERT INTO {self.schema}.quotes VALUES
                (guild_id = $1, origin_id = $2, quoted_id = $3,
                creator_id = $4, content = $5, id = $6,
                hits = 0, currtime = DEFAULT);
        """
        try:
            await self.pool.execute(sql, guild_id, origin_id,
                                    quoted_id, creator_id, content,
                                    index)
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False
        return True

    async def rank_quotes(self, guild_id: int, top: int, logger):
        """Rank X quotes db.

        Parameters
        ----------
        guild_id: int
            guild id
        top: int
            top X number quotes to pull

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            SELECT id FROM {self.schema}.quotes WHERE
                guild_id = $1 ORDER BY hits DESC LIMIT $2;
        """
        try:
            return await self.pool.fetchall(sql, guild_id, top)
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False

    async def get_user_quotes(self, guild_id: int, quoted_id: int, logger):
        """Get all quotes from user.

        Parameters
        ----------
        guild_id: int
            guild id
        quoted_id: int
            quoted user id

        Returns
        -------
        list
            list of user quoted id
        """
        sql = f"""
            SELECT id FROM {self.schema}.quotes
                WHERE guild_id = $1 AND quoted_id = $2;
        """
        try:
            return await self.pool.fetchall(sql, guild_id, quoted_id)
        except Exception as e:
            logger.warning(f'Error getting quoted user: {e}')
            return False

    async def get_allguild_quote_id(self, guild_id: int, logger):
        """Get all quotes in a guild.

        Parameters
        ----------
        guild_id: int
            guild id

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            SELECT id FROM {self.schema}.quotes WHERE guild_id = $1;
        """
        try:
            return await self.pool.fetchall(sql, guild_id, origin_id,
                                            quoted_id, creator_id, content)
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False

    async def get_alluser_quote_id(self, guild_id: int,
                                   quoted_id: int, logger):
        """Get allquotes from a user.

        Parameters
        ----------
        guild_id: int
            guild id
        quoted_id: int
            quoted user id

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            SELECT id FROM {self.schema}.quotes WHERE
                guild_id = $1 AND quoted_id = $2;
        """
        try:
            return await self.pool.fetchall(sql, guild_id, origin_id,
                                            quoted_id, creator_id, content)
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False

    async def get_random_quote(self, guild_id: int, quoted_id: int, logger):
        """Add a single quote db.

        Parameters
        ----------
        guild_id: int
            guild id
        quoted_id: int
            quoted user id

        Returns
        -------
        list
            columns from single quote in guild
        """
        if (len(str(quoted_id)) > 1):
            list_ids = await self.get_alluser_quoted_id(guild_id,
                                                        quoted_id, logger)
        else:
            list_ids = await self.get_allguild_quoted_id(guild_id, logger)
        if len(list_ids) > 1:
            chosen = random.choice(list_ids)
        elif len(list_ids) == 1:
            chosen = list_ids[0]
        else:
            return False
        return await self.get_single_quote(guild_id, chosen, True, logger)

    """
    MACROS
    """
    async def hit_single_macro(self, guild_id: int, name: str, logger):
        """Toggle a hit db.

        Parameters
        ----------
        guild_id: int
            guild id
        name: str
            name of the macro

        Returns
        ----------
        bool
            success true false
        """
        sql = f"""
            UPDATE {self.schema}.macros SET hits = hits + 1
                WHERE guild_id = $1 AND name = $2;
        """
        try:
            return await self.pool.execute(sql, guild_id, name)
        except Exception as e:
            logger.warning(f'Error hitting macro {e}')
            return False
        return True

    async def get_single_macro(self, guild_id: int, name: str,
                               to_hit: bool, logger):
        """Get a single macro db.

        Parameters
        ----------
        guild_id: int
            guild id
        name: str
            name of the macro
        to_hit: bool
            whether or not to hit the macro

        Returns
        ----------
        list
            list of columns from single macro
        """
        if to_hit:
            await self.hit_single_macro(guild_id, name, logger)
        sql = f"""
            SELECT * FROM {self.schema}.macros
                WHERE guild_id = $1 AND name = $2;
        """
        try:
            return await self.pool.fetch(sql, guild_id, name)
        except Exception as e:
            logger.warning(f'Error retrieving quote {e}')
            return False

    async def set_single_macro(self, guild_id: int, name: str,
                               content: str, logger):
        """Set a single macro db.

        Parameters
        ----------
        guild_id: int
            guild id
        name: str
            name of the macro
        content: str
            content of quote

        Returns
        ----------
        bool
            success true false
        """
        sql = f"""
            UPDATE {self.schema}.macros
                SET content = $1, hits = 0 WHERE guild_id = $2 AND name = $3;
        """
        try:
            await self.pool.execute(sql, content, origin_id,
                                    quoted_id, guild_id, qid)
        except Exception as e:
            logger.warning(f'Error setting macro {e}')
            return False
        return True

    async def delete_single_macro(self, guild_id: int, name: str, logger):
        """Remove macro from DB.

        Parameters
        ----------
        guild_id: int
            guild id
        name: str
            name of the macro

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            DELETE FROM {self.schema}.macros
                WHERE guild_id = $1 AND name = $2;
        """
        try:
            await self.pool.execute(sql, guild_id, name)
        except Exception as e:
            logger.warning(f'Error removing macro: {e}')
            return False
        return True

    async def add_single_macro(self, guild_id: int, creator_id: int,
                               name: str, content: str, logger):
        """Add a single macro db.

        Parameters
        ----------
        guild_id: int
            guild id
        creator_id: int
            user that created macro
        name: str
            name of macro
        content: str
            content of macro

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            INSERT INTO {self.schema}.macros VALUES
                (guild_id = $1, creator_id = $2, name = $3, content = $4,
                hits = 0, currtime = DEFAULT);
        """
        try:
            await self.pool.execute(sql, guild_id, creator_id, name, content)
        except Exception as e:
            logger.warning(f'Error adding macro: {e}')
            return False
        return True

    async def rank_macros(self, guild_id: int, top: int, logger):
        """Rank X macros db.

        Parameters
        ----------
        guild_id: int
            guild id
        top: int
            top X number macros to pull

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            SELECT id FROM {self.schema}.macros WHERE
                guild_id = $1 ORDER BY hits DESC LIMIT $2;
        """
        try:
            return await self.pool.fetchall(sql, guild_id, top)
        except Exception as e:
            logger.warning(f'Error removing macro: {e}')
            return False

    async def get_allmacrocreator(self, guild_id: int, logger):
        """Get all users that made macros.

        Parameters
        ----------
        guild_id: int
            guild id

        Returns
        -------
        list
            list of user id
        """
        sql = f"""
            SELECT creator_id FROM {self.schema}.macros
                WHERE guild_id = $1;
        """
        try:
            return await set(self.pool.fetchall(sql, guild_id, creator_id))
        except Exception as e:
            logger.warning(f'Error getting macro: {e}')
            return False

    async def get_creator_macros(self, guild_id: int, creator_id: int, logger):
        """Get all macros from user.

        Parameters
        ----------
        guild_id: int
            guild id
        creator_id: int
            macro created user id

        Returns
        -------
        list
            list of user macro id
        """
        sql = f"""
            SELECT name FROM {self.schema}.macros
                WHERE guild_id = $1 AND creator_id = $2;
        """
        try:
            return await self.pool.fetchall(sql, guild_id, creator_id)
        except Exception as e:
            logger.warning(f'Error getting macro: {e}')
            return False

    async def get_allguild_macro_names(self, guild_id: int, logger):
        """Get all quotes in a guild.

        Parameters
        ----------
        guild_id: int
            guild id

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            SELECT name FROM {self.schema}.macros WHERE guild_id = $1;
        """
        try:
            return await self.pool.fetchall(sql, guild_id)
        except Exception as e:
            logger.warning(f'Error getting macros: {e}')
            return False

    async def get_alluser_macro_name(self, guild_id: int, creator_id: int, logger):
        """Get all macros made from a user.

        Parameters
        ----------
        guild_id: int
            guild id
        creator_id: int
            user id that made macros

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            SELECT name FROM {self.schema}.macros WHERE guild_id = $1 AND creator_id = $2;
        """
        try:
            return await self.pool.fetchall(sql, guild_id, creator_id)
        except Exception as e:
            logger.warning(f'Error getting macro: {e}')
            return False

    """
    REACTS
    """
    async def get_single_react(self, message_id: int,
                               react_id: int, logger):
        """Get a single react db.

        Parameters
        ----------
        guild_id: int
            guild id
        message_id: int
            message id that holds the react info
        react_id: int
            the reaction id

        Returns
        ----------
        list
            list of columns from single react
        """
        sql = f"""
            SELECT * FROM {self.schema}.macros
                WHERE base_message_id = $1 AND react_id = $2;
        """
        try:
            return await self.pool.fetch(sql, message_id, react_id)
        except Exception as e:
            logger.warning(f'Error retrieving react {e}')
            return False

    async def set_single_react(self, base_message_id: int, react_id: int,
                               target_id: int,  guild_id: int, react_role: bool,
                               react_channel: bool, react_category: bool,
                               info: str, logger):
        """Set a single react db.

        Parameters
        ----------
        base_message_id: int
            message id of the base message holding the info
        react_id: int
            react id 
        guild_id: int
            the id of the guild
        target_id: int
            the id of the target to apply
        react_role: bool
            if the apply id is a role
        react_channel: bool
            if the apply id is a channel
        react_category: bool
            if the apply id is a category
        info: str
            information on the target

        Returns
        ----------
        bool
            success true false
        """
        sql = f"""
            UPDATE {self.schema}.reacts
                SET target_id = $1, react_role = $2, react_channel = $3,
                react_category = $4, info = $5, guild_id = $8 WHERE
                base_message_id = $6 AND react_id = $7;
        """
        try:
            status = await self.pool.execute(sql, target_id, react_role,
                                             react_channel,
                                             react_category, info,
                                             base_message_id,
                                             react_id, guild_id)
        except Exception as e:
            logger.warning(f'Error setting react {e}')
            status = False
        if status and react_role:
            await self.set_single_joininfo(target_id, info, logger)
            return True
        if status:
            return True
        return False

    async def delete_single_react(self, guild_id: int, base_message_id: int, react_id: int, logger):
        """Remove react from DB.

        Parameters
        ----------
        guild_id: int
            guild id
        base_message_id: int
            base message that holds react id
        react_id: str
            react id

        Returns
        -------
        bool
            success true false
        """
        rtype = await self.get_single_react(base_message_id, react_id)
        sql = f"""
            DELETE FROM {self.schema}.reacts
                WHERE guild_id = $1 AND base_message_id = $2 AND react_id = $3;
        """
        try:
            status = await self.pool.execute(sql, guild_id, base_message_id, react_id)
        except Exception as e:
            logger.warning(f'Error removing react: {e}')
            status = False
        if status and rtype[0]:
            await self.delete_single_joininfo(rtype[2])
            await self.remove_joinable_role(rtype[2])
            return True
        if status:
            return True
        return False

    async def add_single_react(self, guild_id: int, base_message_id: int,
                               target_id: int, react_id: int, 
                               react_role: bool, react_channel: bool, react_category: bool, 
                               info: str, logger):
        """Add a single react db.

        Parameters
        ----------
        guild_id: int
            guild id
        base_message_id: int
            id of the base message
        target_id: str
            id for the target
        react_id: id
            id for the react
        react_role: bool
            is target a role
        react_channel: bool
            is target a channel
        react_category: bool
            is target a category
        info: str
            info about the target

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            INSERT INTO {self.schema}.reacts VALUES
                (guild_id = $1, base_message_id = $2, target_id = $3,
                react_id = $4, react_role = $5, react_channel = $6,
                react_category = $7, info = $8, currtime = DEFAULT)
                ON CONFLICT (base_message_id, react_id) DO nothing;
        """
        try:
            await self.pool.execute(sql, guild_id, creator_id, name, content)
        except Exception as e:
            logger.warning(f'Error adding react: {e}')
            return False
        if react_role:
            await self.add_joinable_role(target_id)
            await self.add_single_joininfo(target_id, info)
            return True
        return True

    async def get_allguild_reacts(self, guild_id: int, logger):
        """Get all quotes in a guild.

        Parameters
        ----------
        guild_id: int
            guild id

        Returns
        -------
        list
            list of all reacts in guild
        """
        sql = f"""
            SELECT * FROM {self.schema}.reacts WHERE guild_id = $1;
        """
        try:
            return await self.pool.fetchall(sql, guild_id)
        except Exception as e:
            logger.warning(f'Error getting reacts: {e}')
            return False

# end of code

# end of file
