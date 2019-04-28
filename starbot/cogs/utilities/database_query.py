"""Database utility functions."""

# internal modules
import datetime
import random

# external modules
from asyncpg import Record, InterfaceError, create_pool
from asyncpg.pool import Pool

# relative modules
from config import Config
from .database_create import make_tables
from .functions import ModAction, parse

# global attributes
__all__ = ('Controller',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


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
        logger.info(f'Tables created under schema: {schema}.')
        return cls(pool, logger, schema)

    """
    GLOBAL PROPERTIES
    """
    async def add_blacklist_guild_global(self, guild_id: str, logger): # noqa
        """Add blacklisted guild.

        Parameters
        ----------
        guild_id: str
            id for the guild

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            INSERT INTO {self.schema}.globalguildbl
                (guild_id, currtime) VALUES ($1, DEFAULT)
                ON CONFLICT (guild_id) DO NOTHING;
        """
        try:
            await self.pool.execute(sql, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding guild to blacklist {guild_id}: {e}')
            return False

    async def rem_blacklist_guild_global(self, guild_id: str, logger): # noqa
        """Remove blacklisted user.

        Parameters
        ----------
        guild_id: str
            id for the guild

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            DELETE FROM {self.schema}.globalguildbl WHERE guild_id = $1
        """
        try:
            await self.pool.execute(sql, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error removing blacklist guild: {e}')
            return False
        return False

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
            SELECT guild_id FROM {self.schema}.globalguildbl;
        """
        guild_list = await self.pool.fetch(sql)
        return guild_list

    async def is_blacklist_guild_global(self, guild_id: str):
        """Check if guild is a blacklisted.

        Parameters
        ----------
        guild_id: str
            id for the guild to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.globalguildbl WHERE guild_id=$1;
        """
        row = await self.pool.fetchrow(sql, int(guild_id))
        return True if row else False

    async def add_blacklist_user_global(self, user_id: str, logger): # noqa
        """Add blacklisted user.

        Parameters
        ----------
        user_id: str
            id for the user

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            INSERT INTO {self.schema}.globaluserbl
                (user_id, currtime) VALUES ($1, DEFAULT)
                ON CONFLICT (user_id) DO NOTHING;
        """
        try:
            await self.pool.execute(sql,  int(user_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding user to blacklist {user_id}: {e}')
            return False

    async def rem_blacklist_user_global(self, user_id: str, logger): # noqa
        """Remove blacklisted user.

        Parameters
        ----------
        user_id: str
            id for the user

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            DELETE FROM {self.schema}.globaluserbl WHERE user_id = $1
        """
        try:
            return await self.pool.execute(sql, int(user_id))
        except Exception as e:
            logger.warning(f'Error removing blacklist user: {e}')
            return False
        return False

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
            SELECT user_id FROM {self.schema}.globaluserbl;
        """
        user_list = await self.pool.fetch(sql)
        return user_list

    async def is_blacklist_user_global(self, user_id: str):
        """Check if user is a blacklisted.

        Parameters
        ----------
        cmd: str
            cmd to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.globaluserbl WHERE user_id = $1;
        """
        row = await self.pool.fetchrow(sql, int(user_id))
        return True if row else False


    async def add_disallowed_global(self, cmd: str, logger): # noqa
        """Add Disallowed Global Commands.

        Parameters
        ----------
        cmd: str
            cmd to check

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            INSERT INTO {self.schema}.globalcmdbl
                (disallowed_command) VALUES ($1)
                ON CONFLICT (disallowed_command) DO NOTHING;
        """
        try:
            await self.pool.execute(sql, cmd)
            return True
        except Exception as e:
            logger.warning(f'Error adding cmd to disallowed  {cmd}: {e}')
            return False

    async def rem_disallowed_global(self, cmd: str, logger): # noqa
        """Remove Disallowed Global Commands.

        Parameters
        ----------
        cmd: str
            cmd to check

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            DELETE FROM {self.schema}.globalcmdbl WHERE disallowed_command = $1
        """
        try:
            await self.pool.execute(sql, cmd)
        except Exception as e:
            logger.warning(f'Error removing disallowed cmds: {e}')
            return False
        return True

    async def get_all_disallowed_global(self): # noqa
        """Get Disallowed Global Commands.

        Parameters
        ----------

        Returns
        ----------
        list
            list all of the cmds disallowed
        """
        sql = f"""
            SELECT disallowed_command FROM {self.schema}.globalcmdbl;
        """
        cmd_list = await self.pool.fetch(sql)
        return cmd_list

    async def is_disallowed_global(self, cmd: str):
        """Is Disallowed Global Commands.

        Parameters
        ----------
        cmd: str
            cmd to check

        Returns
        ----------
        boolean
            return status true or false
        """
        # SELECT * FROM {self.schema}.global WHERE $1 = ANY (disallowed_commands::int[]) 
        sql = f"""
            SELECT * FROM {self.schema}.globalcmdbl WHERE disallowed_command = $1;
        """
        row = await self.pool.fetchrow(sql, cmd)
        return True if row else False

    async def add_report(self, user_id: str, message: str, logger): # noqa
        """Add report from user user.

        Parameters
        ----------
        user_id: str
            id for the user
        message: str
            message from the user

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            INSERT INTO {self.schema}.reports (user_id, message, id, currtime) VALUES ($1, $2,DEFAULT, DEFAULT)
                ON CONFLICT (id,  user_id) DO nothing;
        """
        try:
            await self.pool.execute(sql,  int(user_id), message)
            return True
        except Exception as e:
            logger.warning(f'Error adding report {user_id} {message}: {e}')
            return False

    async def remove_report(self, user_id: str, place: str, logger): # noqa
        """Remove report from user.

        Parameters
        ----------
        user_id: str
            id for the user
        place: str
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
            await self.pool.execute(sql,  int(user_id),  int(place))
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
        report_list = await self.pool.fetch(sql)
        return report_list


    async def get_all_global_macro(self, logger):
        """Get a single global macro db.

        Parameters
        ----------
        name: str
            name of the macro

        Returns
        ----------
        list
            list of columns from single macro
        """
        sql = f"""
            SELECT * FROM {self.schema}.globalmacros;
        """
        try:
            return await self.pool.fetch(sql)
        except Exception as e:
            logger.warning(f'Error retrieving quote {e}')
            return False


    async def get_single_global_macro(self, name: str, logger):
        """Get a single global macro db.

        Parameters
        ----------
        name: str
            name of the macro

        Returns
        ----------
        list
            list of columns from single macro
        """
        sql = f"""
            SELECT * FROM {self.schema}.globalmacros
                WHERE name = $1;
        """
        try:
            return await self.pool.fetch(sql, name)
        except Exception as e:
            logger.warning(f'Error retrieving quote {e}')
            return False

    async def set_single_global_macro(self, name: str, content: str, logger):
        """Set a single global macro db.

        Parameters
        ----------
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
            UPDATE {self.schema}.globalmacros
                SET content = $2 WHERE name = $1;
        """
        try:
            await self.pool.execute(sql, name, content)
        except Exception as e:
            logger.warning(f'Error setting macro {e}')
            return False
        return True

    async def delete_single_global_macro(self, name: str, logger):
        """Remove global macro from DB.

        Parameters
        ----------
        name: str
            name of the macro

        Returns
        -------
        bool
            success true false
        """
        sql = f"""
            DELETE FROM {self.schema}.globalmacros
                WHERE name = $1;
        """
        try:
            await self.pool.execute(sql, name)
        except Exception as e:
            logger.warning(f'Error removing macro: {e}')
            return False
        return True

    async def add_single_global_macro(self, name: str, content: str, logger):
        """Add a single global macro db.

        Parameters
        ----------
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
            INSERT INTO {self.schema}.globalmacros (name, content, currtime) VALUES
                ($1,$2,DEFAULT);
        """
        try:
            await self.pool.execute(sql, name, content)
        except Exception as e:
            logger.warning(f'Error adding macro: {e}')
            return False
        return True


    """
    GUILD META ACTIONS
    """

    async def add_guild(self, guild_id: str):
        """Add guild to db.

        It will try to create the tables and return the controller

        Parameters
        ----------
        guild_id : str
            long str of the guild id

        Returns
        ----------
        """
        cols = {
                'guild_id': ['', int(guild_id)],
                'prefix': ['', '!'],
                'voice_roles': ['', []],
                'voice_channels': ['', []],
                'cleared_channels': ['', []],
                'modlog_channels': ['', []],
                'logging_channels': ['', []],
                'welcome_message': ['', ''],
                'welcome_channels': ['', []],
                'report_channel': ['', 0],
                'joinable_roles': ['', []],
                'blacklist_channels': ['', []],
                'blacklist_users': ['', []],
                'ban_footer': ['', 'This is an automated message'],
                'kick_footer': ['', 'This is an automated message'],
                'autoroles': ['', []],
                'disallowed_commands': ['', []],
                'colour_template': ['', 0],
        }
        for i, k in enumerate(cols.keys()):
            cols[k][0] = f'${i + 1}'
        print(cols)
        sql = f"""
            INSERT INTO {self.schema}.guilds ({','.join(cols.keys())}) VALUES 
                ({','.join([cols[key][0] for key in cols.keys()])});
            """
        print(sql)

        return await self.pool.execute(sql,*[cols[key][1] for key in cols.keys()])

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
            'colour_enabled',
            'pm_welcome',
            'voice_role_enabled',
            'blacklist_channels',
            'blacklist_users')
        sql = f"""
            SELECT {', '.join(settings)}
                FROM {self.schema}.guilds;
            """
        rets = await self.pool.fetch(sql)
        for row in rets:
            main[int(row['guild_id'])] = {}
            for setting in settings:
                if setting != 'guild_id':
                    main[row['guild_id']][setting] = row[setting]
        return main

    async def get_single_guild_settings(self, guild_id: str):
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
            'colour_enabled',
            'pm_welcome',
            'voice_role_enabled',
            'blacklist_channels',
            'blacklist_users')
        sql = f"""
            SELECT {', '.join(settings)}
                FROM {self.schema}.guilds WHERE guild_id = $1;
            """
        rets = await self.pool.fetch(sql, int(guild_id))
        rets = rets[0]
        main[int(rets['guild_id'])] = {}
        for setting in settings:
            if setting != 'guild_id':
                main[int(rets['guild_id'])][setting] = rets[setting]
        return main

    async def get_guild(self, guild_id: str, logger):
        """All settings for guild.

        Parameters
        ----------
        guild_id: str
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
                WHERE guild_id = $1;
            """
        try:
            return await self.pool.fetchrow(sql, int(guild_id))
        except Exception as e:
            logger.warning(f'Error getting guild settings {e}')
            return False

    async def drop_guild(self, guild_id: str, logger):
        """All settings for guild.

        Parameters
        ----------
        guild_id: str
            id for the guild
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        tuple
            tuple of results or false
        """
        sql = f"""
            DELETE FROM {self.schema}.guilds
                WHERE guild_id = $1;
            """
        try:
            return await self.pool.execute(sql, int(guild_id))
        except Exception as e:
            logger.warning(f'Error removing guild settings {e}')
            return False

    """
    Guild Actions
    """

    async def add_giveaway(self, *args, logger):
        """Add Giveaway to guild.

        Parameters
        ----------
        args:
            The exact parameters in keys

        Returns
        ----------
        boolean
            success true or false
        """
        keys = ('guild_id',
                'channel_id',
                'countdown_message_id',
                'gifter_id',
                'content',
                'num_winners',
                'starttime',
                'endtime',)
        sql = f"""
            INSERT INTO {self.schema}.giveaway
                (_KEYS_,winners_id,status) VALUES (_VALS_,${len(keys)+1},DEFAULT);
        """
        sql = sql.replace('_KEYS_', ','.join(keys))
        sql = sql.replace('_VALS_', '$' + ',$'.join(map(str, range(1, len(keys) + 1))))

        try:
            await self.pool.execute(sql, *args, [])
            return True
        except Exception as e:
            logger.warning(f'Error adding giveaway {args}: {e}')
            return False

    async def update_giveaway(self, message_id, keys, vals, logger):
        """Add Giveaway to guild.

        Parameters
        ----------
        args:
            The exact parameters in keys

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.giveaway SET _KEYS_ WHERE countdown_message_id=${len(keys)+1};
        """
        tmp = ''
        for i in range(len(keys)):
            tmp += f'{keys[i]}=${i + 1}'
            if i < (len(keys) - 1):
                tmp += ','
        sql = sql.replace('_KEYS_', tmp)
        try:
            await self.pool.execute(sql, *vals, int(message_id))
            return True
        except Exception as e:
            logger.warning(f'Error fixing giveaway {keys}, {vals}: {e}')
            return False

    async def get_single_giveaways(self, message_id: str, only_active: bool, logger):
        """Get all Giveaways from guild.

        Parameters
        ----------
        args:
            The exact parameters in keys

        Returns
        ----------
        boolean
            success true or false
        """
        if only_active:
            sql = f"""
                SELECT * FROM {self.schema}.giveaway WHERE countdown_message_id=$1 and status=FALSE;
            """
        else:
            sql = f"""
                SELECT * FROM {self.schema}.giveaway WHERE countdown_message_id=$1;
            """
        try:
            results = await self.pool.fetch(sql, int(message_id))
        except Exception as e:
            logger.warning(f'Error getting giveaway: {e}')
            return False
        if len(results) > 0:
            return dict(results[0])
        else:
            return False

    async def get_all_giveaways_guild(self, guild_id: str, only_active: bool, logger):
        """Get all Giveaways from guild.

        Parameters
        ----------
        args:
            The exact parameters in keys

        Returns
        ----------
        boolean
            success true or false
        """
        default = {}
        if only_active:
            sql = f"""
                SELECT countdown_message_id, endtime FROM {self.schema}.giveaway WHERE status=FALSE AND guild_id = $1;
            """
        else:
            sql = f"""
                SELECT countdown_message_id, endtime FROM {self.schema}.giveaway AND guild_id = $1;
            """
        ret = []
        try:
            results = await self.pool.fetch(sql, int(guild_id))
            if not isinstance(results, type(None)):
                for r in results:
                    default[r['countdown_message_id']] = r['endtime']
        except Exception as e:
            logger.warning(f'Error getting giveaway: {e}')
        return default

    async def get_all_giveaways(self, only_active: bool, logger):
        """Get all Giveaways from guild.

        Parameters
        ----------
        args:
            The exact parameters in keys

        Returns
        ----------
        boolean
            success true or false
        """
        default = {}
        if only_active:
            sql = f"""
                SELECT countdown_message_id, endtime FROM {self.schema}.giveaway WHERE status=FALSE;
            """
        else:
            sql = f"""
                SELECT countdown_message_id, endtime FROM {self.schema}.giveaway;
            """
        ret = []
        try:
            results = await self.pool.fetch(sql)
            if not isinstance(results, type(None)):
                for r in results:
                    default[r['countdown_message_id']] = r['endtime']
        except Exception as e:
            logger.warning(f'Error getting giveaway: {e}')
        return default

    async def add_disallowed(self, guild_id: str, cmd: str, logger): # noqa
        """Add Disallowed guilds Commands.

        Parameters
        ----------
        cmd: str
            cmd to check

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET disallowed_commands = (SELECT array_agg(distinct e)
                FROM unnest(array_append(disallowed_commands,$2::text)) e) WHERE guild_id = $1;
        """
        try:
            await self.pool.execute(sql, int(guild_id), cmd)
            return True
        except Exception as e:
            logger.warning(f'Error adding cmd to disallowed  {cmd}: {e}')
            return False

    async def get_colourtemplate(self, guild_id: str, logger): # noqa
        """Get the colourrole Template.

        Parameters
        ----------

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            SELECT colour_template FROM {self.schema}.guilds
                 WHERE guild_id = $1;
        """
        try:
            return await self.pool.fetch(sql, int(guild_id))
        except Exception as e:
            logger.warning(f'Error getting template for colourrole: {e}')
            return []

    async def set_colourtemplate(self, guild_id: str, role_id: str, logger): # noqa
        """Get the colourrole Template.

        Parameters
        ----------

        Returns
        ----------
        boolean
            success true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                 SET colour_template = $1 WHERE guild_id = $2;
        """
        try:
            return await self.pool.execute(sql, int(role_id), int(guild_id))
        except Exception as e:
            logger.warning(f'Error setting template for colourrole: {e}')
            return False

    async def rem_disallowed(self, guild_id: str, cmd: str, logger): # noqa
        """Remove Disallowed guilds Commands.

        Parameters
        ----------
        cmd: str
            cmd to check

        Returns
        ----------
        boolean
            success true or false
        """
        cmd_list = await self.get_all_disallowed(guild_id)
        cmd_list.remove(cmd)
        sql = f"""
            UPDATE {self.schema}.guilds SET disallowed_commands = $1 WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, cmd_list, int(guild_id))
        except Exception as e:
            logger.warning(f'Error removing disallowed cmds: {e}')
            return False
        return True

    async def get_all_disallowed(self, guild_id: str): # noqa
        """Get Disallowed guilds Commands.

        Parameters
        ----------

        Returns
        ----------
        list
            list all of the cmds disallowed
        """
        sql = f"""
            SELECT disallowed_commands FROM {self.schema}.guilds WHERE guild_id = $1;
        """
        cmd_list = await self.pool.fetchval(sql, int(guild_id))
        return cmd_list

    async def is_disallowed(self, guild_id, cmd: str):
        """Is Disallowed guilds Commands.

        Parameters
        ----------
        cmd: str
            cmd to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds WHERE guild_id = $1 AND disallowed_commands @> $2;
        """
        row = await self.pool.fetchrow(sql, int(guild_id), [cmd])
        return True if row else False

    async def get_all_autoroles(self, guild_id: str):
        """Return all autoroles.

        Parameters
        ----------
        guild_id: str
            id for the guild

        Returns
        ----------
        list
            list of all autoroles
        """
        sql = f"""
            SELECT autoroles FROM {self.schema}.guilds
            WHERE guild_id = $1;
        """
        role_list = await self.pool.fetch(sql, int(guild_id))
        return role_list

    async def is_role_autorole(self, guild_id: str, role_id: str):
        """Check if role is autorole.

        Parameters
        ----------
        guild_id: str
            id for the guild
        role_id: str
            id for the role

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
                AND autoroles @> $2;
        """

        row = await self.pool.fetchrow(sql, int(guild_id), [int(role_id)])
        return True if row else False

    async def add_autorole(self, guild_id: str, role_id: str,
                                logger):
        """Add role to autorole.

        Parameters
        ----------
        guild_id: str
            id for the guild
        role_id: str
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
                SET autoroles = (SELECT array_agg(distinct e)
                FROM unnest(array_append(autoroles,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, int(role_id), int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding role <#{role_id}> to guild {guild_id}: {e}') # noqa
            return False

    async def remove_autorole(self, guild_id: str, role_id: str, logger):
        """Remove if role is autorole.

        Parameters
        ----------
        guild_id: str
            id for the guild
        role_id: str
            id for the role
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        role_list = await self.get_all_autoroles(int(guild_id))
        role_list.remove(int(role_id))
        sql = f"""
            UPDATE {self.schema}.guilds SET autoroles = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, role_list, int(guild_id))
        except Exception as e:
            logger.warning(f'Error removing roles: {e}')
            return False
        return True

    async def get_all_joinable_roles(self, guild_id: str):
        """Return all joinable roles.

        Parameters
        ----------
        guild_id: str
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
        role_list = await self.pool.fetchval(sql, int(guild_id))
        return role_list

    async def is_role_joinable(self, guild_id: str, role_id: str):
        """Check if role is joinable.

        Parameters
        ----------
        guild_id: str
            id for the guild
        role_id: str
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

        row = await self.pool.fetchrow(sql, int(guild_id), [int(role_id)])
        return True if row else False

    async def add_joinable_role(self, guild_id: str, role_id: str,
                                logger):
        """Add role to joinable.

        Parameters
        ----------
        guild_id: str
            id for the guild
        role_id: str
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
            await self.pool.execute(sql, int(role_id), int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding role <@&{role_id}> to guild {guild_id}: {e}') # noqa
            return False

    async def remove_joinable_role(self, guild_id: str, role_id: str, logger):
        """Remove if role is joinable.

        Parameters
        ----------
        guild_id: str
            id for the guild
        role_id: str
            id for the role
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        role_list = await self.get_all_joinable_roles(int(guild_id))
        role_list.remove(int(role_id))
        sql = f"""
            UPDATE {self.schema}.guilds SET joinable_roles = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, role_list, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error removing roles: {e}')
            return False
        return True

    async def get_all_modlogs(self, guild_id: str):
        """Get All modlog channel.

        Returns a list of channel ids for posting mod actions

        Parameters
        ----------
        guild_id: str
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
        channel_list = await self.pool.fetchval(sql, int(guild_id))
        return channel_list

    async def is_modlog(self, guild_id: str, channel_id: str):
        """Check if channel is modlog.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
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

        row = await self.pool.fetchrow(sql, int(guild_id), [int(role_id)])
        return True if row else False

    async def add_modlog(self, guild_id: str, channel_id: str, logger):
        """Adding modlog channel.

        Adds a channel to the modlog channel array for the guild

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
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
            await self.pool.execute(sql, int(channel_id), int(guild_id))
            await self.pool.execute(boolsql, True, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding channel <#{channel_id}> to guild {guild_id}: {e}') # noqa
            return False

    async def rem_modlog(self, guild_id: str, channel_id: str, logger):
        """Remove modlog channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
            channel to add
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        channel_list = await self.get_all_modlogs(int(guild_id))
        channel_list.remove(int(channel_id))
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
            await self.pool.execute(sql, channel_list, int(guild_id))
            if not channel_list:
                await self.pool.execute(boolsql, False, int(guild_id))
        except Exception as e:
            logger.warning(f'Error removing modlog channel <#{channel_id}>: {e}') # noqa
            return False
        return True

    async def set_prefix(self, guild_id: str, prefix: str, logger):
        """prefix.

        Parameters
        ----------
        guild_id: str
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
            await self.pool.execute(sql, prefix, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error setting prefix <{prefix}> for {guild_id}: {e}') # noqa
            return False

    async def set_welcome(self, guild_id: str, dm: bool, logger):
        """Set Welcome to channel.

        Parameters
        ----------
        guild_id: str
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
            await self.pool.execute(sql, dm, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Issue setting welcome message to channel: {e}')
            return False

    async def set_welcome_pm(self, guild_id: str, dm: bool, logger):
        """Set Welcome PM.

        Parameters
        ----------
        guild_id: str
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
            await self.pool.execute(sql, dm, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Issue setting welcome_message: {e}')
            return False

    async def set_welcome_message(self, guild_id: str, message: str, logger):
        """Welcome messages.

        Parameters
        ----------
        guild_id: str
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
            await self.pool.execute(sql, message, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Issue setting welcome_message: {e}')
            return False

    async def get_welcome_message(self, guild_id: str, logger):
        """Welcome messages.

        Parameters
        ----------
        guild_id: str
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
            message = await self.pool.fetchrow(sql, int(guild_id))
            return message['welcome_message']
        except Exception as e:
            logger.warning(f'Error while getting welcome message: {e}')
            return None

    async def get_all_welcome_channels(self, guild_id: str, logger):
        """Get all welcome channel.

        Parameters
        ----------
        guild_id: str
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
        channel_list = await self.pool.fetchval(sql, int(guild_id))
        return channel_list

    async def is_welcome_channel(self, guild_id: str, channel_id: str):
        """Check if channel is welcome channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
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

        row = await self.pool.fetchrow(sql, int(guild_id), [int(channel_id)])
        return True if row else False

    async def add_welcome_channel(self, guild_id: str, channel_id: str, logger): # noqa
        """Add welcome channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
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
            await self.pool.execute(sql, int(channel_id), int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_welcome_channel(self, guild_id: str, channel_id: str, logger): # noqa
        """Remove welcome channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
            id for the channel
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        channel_list = await self.get_all_welcome_channels(int(guild_id), logger)
        channel_list.remove(int(channel_id))
        sql = f"""
            UPDATE {self.schema}.guilds
                SET welcome_channels = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, channel_list, int(guild_id))
        except Exception as e:
            logger.warning(f'Error removing modlog channel: {e}')
            return False
        return True


    async def set_report_channel(self, guild_id: str, channel_id: str, logger):
        """Setting the report channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel: str
            id of the channel

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET report_channel = $1
                WHERE guild_id = $2
        """

        try:
            await self.pool.execute(sql, int(channel_id), int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Issue setting report channel: {e}')
            return False

    async def get_report_channel(self, guild_id: str, logger):
        """Get the ban message footer.

        Parameters
        ----------
        guild_id: str
            id for the guild

        Returns
        ----------
        str
            the ban message
        """
        sql = f"""
            SELECT report_channel from {self.schema}.guilds
                WHERE guild_id = $1
        """
        try:
            message = await self.pool.fetchrow(sql, int(guild_id))
            return message['report_channel']
        except Exception as e:
            logger.warning(f'Error while getting report channel: {e}')
            return None


    async def set_ban_footer(self, guild_id: str, message: str, logger):
        """Setting the ban message footer.

        Parameters
        ----------
        guild_id: str
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
            await self.pool.execute(sql, message, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Issue setting ban footer: {e}')
            return False

    async def get_ban_footer(self, guild_id: str, logger):
        """Get the ban message footer.

        Parameters
        ----------
        guild_id: str
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
            message = await self.pool.fetchrow(sql, int(guild_id))
            return message['ban_footer']
        except Exception as e:
            logger.warning(f'Error while getting ban footer: {e}')
            return None

    async def set_kick_footer(self, guild_id: str, message: str, logger):
        """Setting the kick message footer.

        Parameters
        ----------
        guild_id: str
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
            await self.pool.execute(sql, message, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Issue setting kick footer: {e}')
            return False

    async def get_kick_footer(self, guild_id: str, logger):
        """Get the kick message footer.

        Parameters
        ----------
        guild_id: str
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
            message = await self.pool.fetchrow(sql, int(guild_id))
            return message['kick_footer']
        except Exception as e:
            logger.warning(f'Error while getting kick footer: {e}')
            return None

    async def get_all_logger_channels(self, guild_id: str):
        """Get logging channels.

        Parameters
        ----------
        guild_id: str
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
        channel_list = await self.pool.fetchval(sql, int(guild_id))
        return channel_list

    async def is_logger_channel(self, guild_id: str, channel_id: str):
        """Check if channel is a logging channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
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
        row = await self.pool.fetchrow(sql, int(guild_id), [int(channel_id)])
        return True if row else False

    async def set_logging_enabled(self, guild_id: str, status: bool):
        """Check logging status.

        Parameters
        ----------
        guild_id: str
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
        return await self.pool.fetchval(sql, int(guild_id), status)

    async def add_logger_channel(self, guild_id: str, channel_id: str, logger):
        """Add logging channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
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
            await self.pool.execute(sql, int(channel_id), int(guild_id))
            await self.pool.execute(boolsql, True, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_logger_channel(self, guild_id: str, channel_id: str, logger):
        """Remove logging channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
            id for the channel
        logger: Logger
            logger instance for the bot

        Returns
        ----------
        boolean
            success true or false
        """
        channel_list = await self.get_all_logger_channels(int(guild_id))
        channel_list.remove(int(channel_id))
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
            await self.pool.execute(sql, channel_list, int(guild_id))
            if not channel_list:
                await self.pool.execute(boolsql, False, int(guild_id))
        except Exception as e:
            logger.warning(f'Error removing logging channel: {e}')
            return False
        return True

    async def is_voice_enabled(self, guild_id: str):
        """Check voice enabled.

        Parameters
        ----------
        guild_id: str
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
        return await self.pool.fetchval(sql, int(guild_id))

    async def set_voice_enabled(self, guild_id: str, status: bool):
        """Check voice status.

        Parameters
        ----------
        guild_id: str
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
        return await self.pool.fetchval(sql, int(guild_id), status)

    async def get_all_voice_channels(self, guild_id: str):
        """Get voice all channels.

        Parameters
        ----------
        guild_id: str
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
        channel_list = await self.pool.fetchval(sql, int(guild_id))
        return channel_list

    async def is_voice_channel(self, guild_id: str, channel_id: str):
        """Check if channel is a logging channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
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
        row = await self.pool.fetchrow(sql, int(guild_id), [int(channel_id)])
        return True if row else False

    async def add_voice_channel(self, guild_id: str, channel_id: str, logger):
        """Add a channel to the voice channel array for the server.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
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
            await self.pool.execute(sql, int(channel_id), int(guild_id))
            await self.pool.execute(boolsql, True, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_voice_channel(self, guild_id: str, channel_id: str, logger):
        """Remove a channel to the voice channel array for the server.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
            id for the channel to remove

        Returns
        ----------
        boolean
            true or false
        """
        channel_list = await self.get_all_voice_channels(int(guild_id))
        channel_list.remove(int(channel_id))
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
            await self.pool.execute(sql, channel_list, int(guild_id))
            if not channel_list:
                await self.pool.execute(boolsql, False, int(guild_id))
        except Exception as e:
            logger.warning(f'Error removing logging channel: {e}')
            return False
        return True

    async def get_all_voice_roles(self, guild_id: str):
        """Get all voice roles.

        Parameters
        ----------
        guild_id: str
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
        role_list = await self.pool.fetch(sql, int(guild_id))
        return role_list

    async def is_voice_role(self, guild_id: str, role_id: str):
        """Check if role is a voice role.

        Parameters
        ----------
        guild_id: str
            id for the guild
        role_id: str
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
        row = await self.pool.fetchrow(sql, int(guild_id), [int(role_id)])
        return True if row else False

    async def add_voice_role(self, guild_id: str, role_id: str):
        """Add voice role to array.

        Parameters
        ----------
        guild_id: str
            id for the guild
        role_id: str
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
            await self.pool.execute(sql, int(role_id), int(guild_id))
            await self.pool.execute(boolsql, True, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding role to server {guild_id}: {e}')
            return False

    async def rem_voice_role(self, guild_id: str, role_id: str, logger):
        """Remove a remove voice role array for the server.

        Parameters
        ----------
        guild_id: str
            id for the guild
        role_id: str
            id for the role to remove

        Returns
        ----------
        boolean
            true or false
        """
        role_list = await self.get_all_voice_roles(int(guild_id))
        role_list.remove(int(channel_id))
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
            await self.pool.execute(sql, channel_list, int(guild_id))
            if not channel_list:
                await self.pool.execute(boolsql, False, int(guild_id))
        except Exception as e:
            logger.warning(f'Error removing logging channel: {e}')
            return False
        return True

    async def set_colour_enabled(self, guild_id: str, status: bool):
        """Set colour role enabled.

        Parameters
        ----------
        guild_id: str
            id for the guild
        status: bool

        Returns
        ----------
        boolean
            true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET colour_enabled = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, status, int(guild_id))
            return True
        except:
            return False


    async def set_invites_allowed(self, guild_id: str, status: bool):
        """Set are invites allowed from no mods.

        Parameters
        ----------
        guild_id: str
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
        try:
            await self.pool.execute(sql, status, int(guild_id))
            return True
        except:
            return False

    async def add_blacklist_channel(self, guild_id: str, channel_id: str, logger): # noqa
        """Add blacklisted channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
            id for the channel to add

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET blacklist_channels = (SELECT array_agg(distinct e)
                FROM unnest(array_append(blacklist_channels,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, int(channel_id), int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_blacklist_channel(self, guild_id: str, channel_id: str, logger): # noqa
        """Remove blacklisted channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
            id for the channel to remove

        Returns
        ----------
        boolean
            return status true or false
        """
        channel_list = await self.get_all_blacklist_channels(int(guild_id))
        channel_list.remove(int(channel_id))
        sql = f"""
            UPDATE {self.schema}.guilds
                SET blacklist_channels = $1
                WHERE guild_id = $2;
        """
        try:
            return await self.pool.execute(sql, channel_list, int(guild_id))
        except Exception as e:
            logger.warning(f'Error removing blacklist channel: {e}')
            return False
        return False

    async def get_all_blacklist_channels(self, guild_id: str): # noqa
        """Get all blacklisted channels.

        Parameters
        ----------
        guild_id: str
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
        channel_list = await self.pool.fetchval(sql, int(guild_id))
        return channel_list

    async def is_blacklist_channel(self, guild_id: str, channel_id: str):
        """Check if channel is a blacklisted.

        Parameters
        ----------
        guild_id: str
            id for the guild
        channel_id: str
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
        row = await self.pool.fetchrow(sql, int(guild_id), [int(channel_id)])
        return True if row else False

    async def add_blacklist_user(self, guild_id: str, user_id: str, logger): # noqa
        """Add blacklisted channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        user_id: str
            id for the user to add

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            UPDATE {self.schema}.guilds
                SET blacklist_users = (SELECT array_agg(distinct e)
                FROM unnest(array_append(blacklist_users,$1::bigint)) e)
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, int(user_id), int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error adding user to blacklist {guild_id}: {e}')
            return False

    async def rem_blacklist_user(self, guild_id: str, user_id: str, logger): # noqa
        """Remove blacklisted channel.

        Parameters
        ----------
        guild_id: str
            id for the guild
        user_id: str
            id for the user to remove

        Returns
        ----------
        boolean
            return status true or false
        """
        user_list = await self.get_all_blacklist_users(int(guild_id))
        user_list.remove(int(user_id))
        sql = f"""
            UPDATE {self.schema}.guilds
                SET blacklist_users = $1
                WHERE guild_id = $2;
        """
        try:
            await self.pool.execute(sql, user_list, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error removing blacklist channel: {e}')
            return False
        return False

    async def get_all_blacklist_users(self, guild_id: str): # noqa
        """Get all blacklisted channels.

        Parameters
        ----------
        guild_id: str
            id for the guild

        Returns
        ----------
        list
            list all of the blacklisted channels
        """
        sql = f"""
            SELECT blacklist_users FROM {self.schema}.guilds
                WHERE guild_id = $1;
        """
        user_list = await self.pool.fetch(sql, int(guild_id))
        return user_list

    async def is_blacklist_user(self, guild_id: str, user_id: str):
        """Check if user is a blacklisted.

        Parameters
        ----------
        guild_id: str
            id for the guild
        user_id: str
            id for the user to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.guilds
                WHERE guild_id = $1
                AND blacklist_users @> $2;
        """
        row = await self.pool.fetchrow(sql, int(guild_id), [int(user_id)])
        return True if row else False

    """
    Moderations
    """
    async def get_moderation_index(self, guild_id: str, user_id: str, logger):
        """Get index for moderation db.

        Parameters
        ----------
        guild_id: str
            guild id
        user_id: str
            user id

        Returns
        -------
        int
            index of next valid moderation for the user
        """
        sql = f"""
            SELECT index_id FROM {self.schema}.moderation WHERE
                guild_id = $1 AND user_id = $2 ORDER BY index_id DESC LIMIT 1;
        """
        try:
            val = await self.pool.fetchval(sql, int(guild_id),  int(user_id))
            val = parse(val[0])[0][1]
            return val + 1
        except Exception as e:
            logger.warning(f'Error indexing modactions: {e}')
            return -1

    async def get_moderation_count(self, guild_id: str, user_id: str,
                                   include: bool=False):
        """Gather mod actions.

        Parameters
        ----------
        guild_id: str
            id for the guild
        user_id: str
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
                SELECT COUNT(user_id) FROM {self.schema}.moderation
                    WHERE guild_id = $1 AND user_id = $2;
            """
        else:
            sql = f"""
                SELECT COUNT(user_id) FROM {self.schema}.moderation
                    WHERE guild_id = $1 AND user_id = $2 AND forgiven = False;
            """
        return await self.pool.fetchval(sql, int(guild_id),  int(user_id))

    async def add_single_moderation(self, guild_id: str, mod_id: str,
                                    target_id: str, reason: str,
                                    action_type: ModAction, logger):
        """Add moderation to db.

        Parameters
        ----------
        guild_id: str
            id for the guild
        mod_id: str
            id for the mod
        target_id: str
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
        index = await self.get_moderation_index(int(guild_id), int(target_id), logger)
        if index == -1:
            return False
        sql = f"""
            INSERT INTO {self.schema}.moderation (guild_id,mod_id,user_id,index_id,reason,type,forgiven,logtime) VALUES ($1,$2, $3,$4,$5,$6, DEFAULT, DEFAULT);
        """
        await self.pool.execute(
            sql,
            int(guild_id),
            int(mod_id),
            int(target_id),
            int(index),
            reason,
            int(action_type.value)
        )

    async def get_all_moderation(self, guild_id: str, user_id: str,
                                 logger, recent: bool=False):
        """Get all moderation db.

        Parameters
        ----------
        guild_id: str
            id for the guild
        target_id: str
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
                    now()) - INTERVAL '6 month') AND forgiven = FALSE;
            """
        else:
            sql = f"""
                SELECT * FROM {self.schema}.moderation
                    WHERE guild_id = $1 AND user_id = $2;
            """
        try:
            return await self.pool.fetch(sql, int(guild_id),  int(user_id))
        except Exception as e:
            logger.warning(f'Error retrieving moderations {e}')
            return False

    async def get_single_modaction(self, guild_id: str, user_id: str,
                                   index: str, logger):
        """Get a single moderation db.

        Parameters
        ----------
        guild_id: str
            id for the guild
        user_id: str
            id for the user to moderate
        index: str
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
            return await self.pool.fetch(sql, int(guild_id),  int(user_id), int(index))
        except Exception as e:
            logger.warning(f'Error retrieving moderation action {e}')
            return False

    async def set_single_modaction(self, guild_id: str, target_id: str,
                                   mod_id: str, index: str,
                                   action_type: ModAction,
                                   reason: str, status: bool, logger):
        """Set a single moderation db.

        Parameters
        ----------
        guild_id: str
            id for the guild
        target_id: str
            id for the user to moderate
        mod_id: str
            id for the mod
        index: str
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
            await self.pool.execute(sql, reason, int(mod_id),
                                    action_type.value,
                                    status, int(guild_id),
                                     int(target_id), int(index))
        except Exception as e:
            logger.warning(f'Error retrieving moderation action {e}')
        return await self.get_moderation_count(int(guild_id),  int(target_id), False)

    async def delete_single_modaction(self, guild_id: str, forg_mod_id: str,
                                      user_id: str, index: str, logger):
        """Forgive a single moderation db.

        I opted to not include a way to delete modactions
        and rather forgive them.

        Parameters
        ----------
        guild_id: str
            id for the guild
        target_id: str
            id for the user to moderate
        mod_id: str
            id for the mod
        index: str
            index to grab

        Returns
        ----------
        int
            number of modactions
        """
        forgiven_message = f' **Forgiven by <@{forg_mod_id}>** ' +\
            'on {datetime.datetime.now()}'
        original = await self.get_single_modaction(int(guild_id),  int(user_id),
                                                   int(index), logger)
        o = {}
        for (key, val) in original[0].items():
            o[key] = val
        original = o

        return await self.set_single_modaction(original['guild_id'], original['user_id'], original['mod_id'], int(index), ModAction(original['type']), original['reason'] + forgiven_message,
                                               True, logger)

    """
    Warnings
    """
    async def get_warning_index(self, guild_id: str, user_id: str, logger):
        """Get index for warnings db.

        Parameters
        ----------
        guild_id: str
            guild id
        user_id: str
            user id

        Returns
        -------
        int
            index of next valid warning for the user
        """
        sql = f"""
            SELECT index_id FROM {self.schema}.warnings WHERE
                guild_id = $1 AND user_id = $2 ORDER BY index_id DESC LIMIT 1;
        """
        try:
            return await self.pool.fetchval(sql, int(guild_id),  int(user_id)) + 1
        except Exception as e:
            logger.warning(f'Error indexing warnings: {e}')
            return 0

    async def get_warning_count(self, guild_id: str, user_id: str,
                                include: bool):
        """Gather warning count.

        Parameters
        ----------
        guild_id: str
            id for the guild
        user_id: str
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
                SELECT COUNT(user_id) FROM {self.schema}.warnings
                    WHERE guild_id = $1 AND user_id = $2;
            """
        else:
            sql = f"""
                SELECT COUNT(user_id) FROM {self.schema}.warnings
                    WHERE guild_id = $1 AND user_id = $2 AND forgiven = False;
            """
        return await self.pool.fetchval(sql, int(guild_id),  int(user_id))

    async def add_single_warning(self, guild_id: str, mod_id: str,
                                 target_id: str, reason: str,
                                 major: bool, logging):
        """Add warning to db.

        Parameters
        ----------
        guild_id: str
            id for the guild
        mod_id: str
            id for the mod
        target_id: str
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
        index = await self.get_warning_index(int(guild_id), int(target_id), logging)
        print('Index:',index)
        sql = f"""
            INSERT INTO {self.schema}.warnings (guild_id,
                mod_id, user_id, index_id,
                reason, major, forgiven,
                logtime) VALUES ($1,$2,$3,$4,$5, $6, DEFAULT,DEFAULT) ;
        """
        await self.pool.execute(
            sql,
            int(guild_id),
            int(mod_id),
            int(target_id),
            int(index),
            reason,
            major
        )
        return await self.get_warning_count(guild_id, target_id, False)

    async def get_all_warnings(self, guild_id: str, user_id: str,
                               logger, recent: bool=False):
        """Get all warnings db.

        Parameters
        ----------
        guild_id: str
            id for the guild
        target_id: str
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
                    WHERE guild_id = $1 AND user_id = $2 AND forgiven = FALSE AND
                    (logtime >= DATE_TRUNC('month',
                    now()) - INTERVAL '6 month');
            """
        else:
            sql = f"""
                SELECT * FROM {self.schema}.warnings
                    WHERE guild_id = $1 AND user_id = $2;
            """
        print(sql)
        try:
            return await self.pool.fetch(sql, int(guild_id),  int(user_id))
        except Exception as e:
            logger.warning(f'Error retrieving warnings {e}')
            return False

    async def get_single_warning(self, guild_id: str, user_id: str,
                                 index: str, logger):
        """Get a single warning db.

        Parameters
        ----------
        guild_id: str
            id for the guild
        user_id: str
            id for the user to warn
        index: str
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
            return await self.pool.fetch(sql, int(guild_id),  int(user_id), int(index))
        except Exception as e:
            logger.warning(f'Error retrieving warning {e}')
            return False

    async def set_single_warning(self, guild_id: str, target_id: str,
                                 mod_id: str, index: str, major: bool,
                                 reason: str, status: bool, logger):
        """Set a single moderation db.

        Parameters
        ----------
        guild_id: str
            id for the guild
        target_id: str
            id for the user to warn
        mod_id: str
            id for the mod
        index: str
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
            await self.pool.execute(sql, reason, int(mod_id),
                                    major,
                                    status, int(guild_id),
                                     int(target_id), int(index))
        except Exception as e:
            logger.warning(f'Error setting warnings {e}')
        return await self.get_warning_count(int(guild_id),  int(target_id), False)

    async def delete_single_warning(self, guild_id: str, forg_mod_id: str,
                                    user_id: str, index: str, logger):
        """Forgive a single warnings db.

        I opted to not include a way to delete warnings
        and rather forgive them.

        Parameters
        ----------
        guild_id: str
            id for the guild
        target_id: str
            id for the user to warn
        mod_id: str
            id for the mod
        index: str
            index to grab

        Returns
        ----------
        int
            number of warnings
        """
        forgiven_message = f' **Forgiven by <@{forg_mod_id}>** ' +\
            f'on {datetime.datetime.now()}'
        original = await self.get_single_warning(int(guild_id),  int(user_id),
                                                 int(index), logger)
        original = [x for x in original[0].values()]
        print(original)
        return await self.set_single_warning(*original[0:4], original[6],
                                             original[4] + forgiven_message,
                                             True, logger)

    """
    JOIN_INFO
    """

    async def is_single_joininfo(self, guild_id: str, target_id: str):
        """Check if user is a blacklisted.

        Parameters
        ----------
        guild_id: str
            id for the guild
        user_id: str
            id for the user to check

        Returns
        ----------
        boolean
            return status true or false
        """
        sql = f"""
            SELECT * FROM {self.schema}.joinableinfo
                WHERE guild_id = $1
                AND target_id = $2;
        """
        row = await self.pool.fetchrow(sql, int(guild_id), int(target_id))
        return True if row else False

    async def add_single_joininfo(self, guild_id: str, target_id: str, info: str, logger):
        """Add a single joininfo db.

        Parameters
        ----------
        target_id: str
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
                (target_id, info, guild_id, currtime) VALUES ($1, $2, $3, DEFAULT);
        """
        try:
            await self.pool.execute(sql, int(target_id), info, int(guild_id))
        except Exception as e:
            logger.warning(f'Error retrieving join info {e}')
            return False
        return True

    async def get_single_joininfo(self, guild_id: str, target_id: str, logger):
        """Get a single warning db.

        Parameters
        ----------
        target_id: str
            id for the target

        Returns
        ----------
        list
            list of columns from single target_id
        """
        sql = f"""
            SELECT * FROM {self.schema}.joinableinfo
                WHERE target_id = $1 and guild_id = $2;
        """
        try:
            return await self.pool.fetch(sql, int(target_id), int(guild_id))
        except Exception as e:
            logger.warning(f'Error retrieving join info {e}')
            return False
        return True

    async def set_single_joininfo(self, guild_id: str, target_id: str, info: str, logger):
        """Set a single joinable info.

        Parameters
        ----------
        target_id: str
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
                SET info = $1 WHERE target_id = $2 and guild_id = $3;
        """
        try:
            await self.pool.execute(sql, info, int(target_id), int(guild_id))
        except Exception as e:
            logger.warning(f'Error setting joininfo {e}')
            return False
        return True

    async def delete_single_joininfo(self, target_id: str, logger):
        """Remove joininfo from DB if parent is deleted.

        Parameters
        ----------
        target_id: str
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
            await self.pool.execute(sql, int(target_id))
        except Exception as e:
            logger.warning(f'Error removing joininfo: {e}')
            return False
        return True

    """
    QUOTES
    """
    async def get_allquotedusers(self, guild_id: str, logger):
        """Get all users that were quoted.

        Parameters
        ----------
        guild_id: str
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
            return await set(self.pool.fetch(sql, int(guild_id)))
        except Exception as e:
            logger.warning(f'Error getting quoted users: {e}')
            return False

    async def get_quote_index(self, guild_id: str, logger):
        """Get index for quote db.

        Parameters
        ----------
        guild_id: str
            guild id
        quoted_id: str
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
            return await self.pool.fetchval(sql, int(guild_id)) + 1
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return 0

    async def hit_single_quote(self, guild_id: str, qid: str, logger):
        """Toggle a hit db.

        Parameters
        ----------
        guild_id: str
            guild id
        qid: str
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
            return await self.pool.execute(sql, int(guild_id), int(qid))
        except Exception as e:
            logger.warning(f'Error hitting quote {e}')
            return False
        return True

    async def get_single_quote(self, guild_id: str, qid: str,
                               to_hit: bool, logger):
        """Get a single quote db.

        Parameters
        ----------
        guild_id: str
            guild id
        qid: str
            quote id
        to_hit: bool
            whether or not to hit the quote

        Returns
        ----------
        list
            list of columns from single quote
        """
        if to_hit:
            await self.hit_single_quote(int(guild_id),  int(qid), logger)
        sql = f"""
            SELECT * FROM {self.schema}.quotes
                WHERE guild_id = $1 AND id = $2;
        """
        try:
            return await self.pool.fetch(sql, int(guild_id), int(qid))
        except Exception as e:
            logger.warning(f'Error retrieving quote {e}')
            return False
        return True

    async def set_single_quote(self, guild_id: str, quoted_id: str,
                               qid: str, origin_id: str,
                               creator_id: str, content: str, logger):
        """Set a single quote db.

        Parameters
        ----------
        guild_id: str
            guild id
        quoted_id: str
            quoted user id
        qid: str
            quote uniq id
        origin_id: str
            id of message that marks origin
        creator_id: str
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
            await self.pool.execute(sql, content, int(origin_id),
                                    int(quoted_id), int(guild_id), int(qid))
        except Exception as e:
            logger.warning(f'Error setting quote {e}')
            return False
        return True

    async def delete_single_quote(self, guild_id: str, qid: str, logger):
        """Remove quote from DB.

        Parameters
        ----------
        guild_id: str
            guild id
        qid: str
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
            await self.pool.execute(sql, int(guild_id), int(qid))
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False
        return True

    async def add_single_quote(self, guild_id: str, quoted_id: str,
                               origin_id: str, creator_id: str,
                               content: str, logger):
        """Add a single quote db.

        Parameters
        ----------
        guild_id: str
            guild id
        quoted_id: str
            quoted user id
        origin_id: str
            id of message that marks origin
        creator_id: str
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
            INSERT INTO {self.schema}.quotes (guild_id, origin_id, quoted_id,
                creator_id, content, id,
                hits, currtime) VALUES
                ($1, $2, $3, $4, $5, $6, 0, DEFAULT);
        """
        try:
            await self.pool.execute(sql, int(guild_id), int(origin_id),
                                    int(quoted_id), int(creator_id), content,
                                    int(index))
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False
        return True

    async def rank_quotes(self, guild_id: str, top: str, logger):
        """Rank X quotes db.

        Parameters
        ----------
        guild_id: str
            guild id
        top: str
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
            return await self.pool.fetch(sql, int(guild_id), top)
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False

    async def get_user_quotes(self, guild_id: str, quoted_id: str, logger):
        """Get all quotes from user.

        Parameters
        ----------
        guild_id: str
            guild id
        quoted_id: str
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
            return await self.pool.fetch(sql, int(guild_id), int(quoted_id))
        except Exception as e:
            logger.warning(f'Error getting quoted user: {e}')
            return False

    async def get_allguild_quote_id(self, guild_id: str, logger):
        """Get all quotes in a guild.

        Parameters
        ----------
        guild_id: str
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
            return await self.pool.fetch(sql, int(guild_id), int(origin_id),
                                            int(quoted_id), int(creator_id), content)
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False

    async def get_alluser_quote_id(self, guild_id: str,
                                   quoted_id: str, logger):
        """Get allquotes from a user.

        Parameters
        ----------
        guild_id: str
            guild id
        quoted_id: str
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
            return await self.pool.fetch(sql, int(guild_id), int(origin_id),
                                            int(quoted_id), int(creator_id), content)
        except Exception as e:
            logger.warning(f'Error removing quote: {e}')
            return False

    async def get_random_quote(self, guild_id: str, quoted_id: str, logger):
        """Add a single quote db.

        Parameters
        ----------
        guild_id: str
            guild id
        quoted_id: str
            quoted user id

        Returns
        -------
        list
            columns from single quote in guild
        """
        if (len(str(int(quoted_id))) > 1):
            list_ids = await self.get_alluser_quote_id(int(guild_id),
                                                        int(quoted_id), logger)
        else:
            list_ids = await self.get_allguild_quote_id(int(guild_id), logger)
        if len(list_ids) > 1:
            chosen = random.choice(list_ids)
        elif len(list_ids) == 1:
            chosen = list_ids[0]
        else:
            return False
        return await self.get_single_quote(int(guild_id), chosen, True, logger)

    """
    MACROS
    """
    async def hit_single_macro(self, guild_id: str, name: str, logger):
        """Toggle a hit db.

        Parameters
        ----------
        guild_id: str
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
            return await self.pool.execute(sql, int(guild_id), name)
        except Exception as e:
            logger.warning(f'Error hitting macro {e}')
            return False
        return True

    async def get_single_macro(self, guild_id: str, name: str,
                               to_hit: bool, logger):
        """Get a single macro db.

        Parameters
        ----------
        guild_id: str
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
            await self.hit_single_macro(int(guild_id), name, logger)
        sql = f"""
            SELECT * FROM {self.schema}.macros
                WHERE guild_id = $1 AND name = $2;
        """
        try:
            return await self.pool.fetch(sql, int(guild_id), name)
        except Exception as e:
            logger.warning(f'Error retrieving quote {e}')
            return False

    async def set_single_macro(self, guild_id: str, name: str,
                               content: str, logger):
        """Set a single macro db.

        Parameters
        ----------
        guild_id: str
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
            await self.pool.execute(sql, content, int(origin_id),
                                    int(quoted_id), int(guild_id), int(qid))
        except Exception as e:
            logger.warning(f'Error setting macro {e}')
            return False
        return True

    async def delete_single_macro(self, guild_id: str, name: str, logger):
        """Remove macro from DB.

        Parameters
        ----------
        guild_id: str
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
            await self.pool.execute(sql, int(guild_id), name)
        except Exception as e:
            logger.warning(f'Error removing macro: {e}')
            return False
        return True

    async def add_single_macro(self, guild_id: str, creator_id: str,
                               name: str, content: str, logger):
        """Add a single macro db.

        Parameters
        ----------
        guild_id: str
            guild id
        creator_id: str
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
            INSERT INTO {self.schema}.macros (guild_id, creator_id, name, content,
                hits, currtime) VALUES
                ($1,$2, $3, $4,0,DEFAULT);
        """
        try:
            await self.pool.execute(sql, int(guild_id), int(creator_id), name, content)
        except Exception as e:
            logger.warning(f'Error adding macro: {e}')
            return False
        return True

    async def rank_macros(self, guild_id: str, top: str, logger):
        """Rank X macros db.

        Parameters
        ----------
        guild_id: str
            guild id
        top: str
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
            return await self.pool.fetch(sql, int(guild_id), top)
        except Exception as e:
            logger.warning(f'Error removing macro: {e}')
            return False

    async def get_allmacrocreator(self, guild_id: str, logger):
        """Get all users that made macros.

        Parameters
        ----------
        guild_id: str
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
            return await set(self.pool.fetch(sql, int(guild_id), int(creator_id)))
        except Exception as e:
            logger.warning(f'Error getting macro: {e}')
            return False

    async def get_creator_macros(self, guild_id: str, creator_id: str, logger):
        """Get all macros from user.

        Parameters
        ----------
        guild_id: str
            guild id
        creator_id: str
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
            return await self.pool.fetch(sql, int(guild_id), int(creator_id))
        except Exception as e:
            logger.warning(f'Error getting macro: {e}')
            return False

    async def get_allguild_macro_names(self, guild_id: str, logger):
        """Get all quotes in a guild.

        Parameters
        ----------
        guild_id: str
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
            return await self.pool.fetch(sql, int(guild_id))
        except Exception as e:
            logger.warning(f'Error getting macros: {e}')
            return False

    async def get_alluser_macro_name(self, guild_id: str, creator_id: str, logger):
        """Get all macros made from a user.

        Parameters
        ----------
        guild_id: str
            guild id
        creator_id: str
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
            return await self.pool.fetch(sql, int(guild_id), int(creator_id))
        except Exception as e:
            logger.warning(f'Error getting macro: {e}')
            return False

    """
    REACTS
    """
    async def get_single_react(self, message_id: str,
                               react_id: str, logger):
        """Get a single react db.

        Parameters
        ----------
        guild_id: str
            guild id
        message_id: str
            message id that holds the react info
        react_id: str
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
            return await self.pool.fetch(sql, int(message_id), int(react_id))
        except Exception as e:
            logger.warning(f'Error retrieving react {e}')
            return False

    async def set_single_react(self, base_message_id: str, react_id: str,
                               target_id: str,  guild_id: str, react_role: bool,
                               react_channel: bool, react_category: bool,
                               info: str, logger):
        """Set a single react db.

        Parameters
        ----------
        base_message_id: str
            message id of the base message holding the info
        react_id: str
            react id 
        guild_id: str
            the id of the guild
        target_id: str
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
            status = await self.pool.execute(sql, int(target_id), react_role,
                                             react_channel,
                                             react_category, info,
                                             int(base_message_id),
                                             int(react_id), int(guild_id))
        except Exception as e:
            logger.warning(f'Error setting react {e}')
            status = False
        if status and react_role:
            await self.set_single_joininfo(int(target_id), info, logger)
            return True
        if status:
            return True
        return False

    async def delete_single_react(self, guild_id: str, base_message_id: str, react_id: str, logger):
        """Remove react from DB.

        Parameters
        ----------
        guild_id: str
            guild id
        base_message_id: str
            base message that holds react id
        react_id: str
            react id

        Returns
        -------
        bool
            success true false
        """
        rtype = await self.get_single_react(int(base_message_id), int(react_id))
        sql = f"""
            DELETE FROM {self.schema}.reacts
                WHERE guild_id = $1 AND base_message_id = $2 AND react_id = $3;
        """
        try:
            status = await self.pool.execute(sql, int(guild_id), int(base_message_id), int(react_id))
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

    async def add_single_react(self, guild_id: str, base_message_id: str,
                               target_id: str, react_id: str, 
                               react_role: bool, react_channel: bool, react_category: bool, 
                               info: str, logger):
        """Add a single react db.

        Parameters
        ----------
        guild_id: str
            guild id
        base_message_id: str
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
            INSERT INTO {self.schema}.reacts (
            guild_id,
            base_message_id,
            target_id,
            react_id,
            react_role,
            react_channel,
            react_category,
            info,
            currtime) VALUES
                ($1,
                $2,
                $3,
                $4,
                $5,
                $6,
                $7,
                $8,DEFAULT)
                ON CONFLICT (base_message_id, react_id) DO nothing;
        """
        try:
            await self.pool.execute(sql, int(guild_id), int(creator_id), name, content)
        except Exception as e:
            logger.warning(f'Error adding react: {e}')
            return False
        if react_role:
            await self.add_joinable_role(int(target_id))
            await self.add_single_joininfo(int(target_id), info)
            return True
        return True

    async def get_allguild_reacts(self, guild_id: str, logger):
        """Get all quotes in a guild.

        Parameters
        ----------
        guild_id: str
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
            return await self.pool.fetch(sql, int(guild_id))
        except Exception as e:
            logger.warning(f'Error getting reacts: {e}')
            return False

    async def get_single_record(self, guild_id, key, logger):
        """Get a single records in the guild.

        This is fine tuned and MUST match the exact specifications
        size of a record row for schema.guild. If it is unable to match
        it will not change that value and continue.

        Parameters
        ----------
        guild_id: str
            guild id
        key: str:
            the exact col name

        Returns
        -------
        bool:
            True or false for success
        """
        sql = f"""
            SELECT {key} FROM {self.schema}.guilds WHERE guild_id = $1;
        """
        try:
            current = await self.pool.fetchval(sql, int(guild_id))
        except Exception as e:
            logger.warning(f'Error getting current guild val: {e}')
            return False
        if isinstance(current, type(None)):
            logger.warning(f'Error getting current guild val: {e}')
            return False
        return current

    async def set_single_record(self, guild_id, key, value, logger):
        """Set a single records in the guild.

        This is fine tuned and MUST match the exact specifications
        size of a record row for schema.guild. If it is unable to match
        it will not change that value and continue.

        Parameters
        ----------
        guild_id: str
            guild id
        key: str:
            the exact col name
        value: str
            the value to input to 

        Returns
        -------
        bool:
            True or false for success
        """
        inv = {key: value}
        self.fix_key(inv, [], [])
        val = inv[key]
        sql = f"""
            UPDATE {self.schema}.guilds SET {key} = $1 WHERE guild_id = $2;
        """
        try:
            current = await self.pool.fetchval(sql, val, int(guild_id))
            return True
        except Exception as e:
            logger.warning(f'Error setting current guild val: {e}')
            return False
        return False

    async def set_multiple_records(self, guild_id, inv: dict, logger):
        """Set numerous records in the guild.

        This is fine tuned and MUST match the exact specifications
        size of a record row for schema.guild. If it is unable to match
        it will not change that value and continue.

        Parameters
        ----------
        guild_id: str
            guild id
        inv: dict
            input values in dictionary form. Key is the SAME as in schema. guild val must match the type too.

        Returns
        -------
        tuple[lists]
            a tuple of lists. tuple[0] keys that succeeded, tuple[1] keys that failed
        """
        passed = []
        failed = []
        self.fix_key(inv, passed, failed)
        p = []
        if len(passed) > 0:
            for x in passed:
                try:
                    success = await self.set_single_record(guild_id, x, inv[x], logger)
                    if success:
                        p.append(x)
                    else:
                        failed.append(x)
                except Exception as e:
                    logger.warning(f'Failed on {e}')
                    failed.append(x)
                    continue
        return p, failed

    def fix_key(self, inv, passed, failed):
        print(inv)
        for key in inv:
            val = inv[key]
            try:
                if ('channels' in key) or ('users' in key) or ('roles' in key):
                    if val == '-1':
                        val = []
                    if len(val) > 0:
                        val = list(map(int, val.split(',')))
                elif ('commands' in key) or ('subreddit' in key) or ('twitch' in key) or\
                     ('twitter' in key)  or ('github' in key):
                    if len(val) > 0:
                        val = list(map(str, val.split(',')))
                elif ('voice_enabled' in key) or ('invites_allowed' in key) or\
                     ('voice_logging' in key) or ('modlog_enabled' in key) or\
                     ('logging_enabled' in key) or ('pm_welcome' in key) or\
                     ('colour_enabled' in key) or ('pm_welcome' in key):
                     if val.lower() in ['false', 'no', 'stop', '-1']:
                        val = False
                     else:
                        val = True
                elif ('colour_template' in key):
                    val = int(val)
                elif 'prefix' in key:
                    val = str(val)[:2]
                passed.append(key)
                inv[key] = val
            except:
                failed.append(key)
                continue
        pass

# end of code

# end of file
