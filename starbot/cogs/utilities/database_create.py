"""Database Creator."""

# internal modules
from typing import Optional
import datetime

# external modules
from asyncpg.pool import Pool

# relative modules

# global attributes
__all__ = ('make_tables', )
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


async def make_tables(pool: Pool, schema: str):
    await pool.execute('CREATE SCHEMA IF NOT EXISTS {};'.format(schema))
    tables = define_tables(schema)
    for t in tables:
        await pool.execute(t)


def define_tables(schema: str):
    """Configuration Constructor.

    Verify input configuration against a template.

    Parameters
    ----------
    pool : Pool
        The connection pool
    schema : str
        The schema to use

    Returns
    ----------
    tuple[str]
        sql statements to generate the sql db
    """

    globalmacros = f"""
    CREATE TABLE IF NOT EXISTS {schema}.globalmacros (
        name TEXT,
        content TEXT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (name)
    );"""

    globcl = f"""
    CREATE TABLE IF NOT EXISTS {schema}.globalcmdbl (
        disallowed_command TEXT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY(disallowed_command)
    );"""

    globul = f"""
    CREATE TABLE IF NOT EXISTS {schema}.globaluserbl (
        user_id BIGINT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY(user_id)
    );"""

    globgl = f"""
    CREATE TABLE IF NOT EXISTS {schema}.globalguildbl (
        guild_id BIGINT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY(guild_id) 
    );"""

    glob_reports = f"""
    CREATE TABLE IF NOT EXISTS {schema}.reports (
        user_id BIGINT,
        message TEXT,
        id SERIAL,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY(id, user_id)
    );"""

    guilds = f"""
    CREATE TABLE IF NOT EXISTS {schema}.guilds (
        guild_id BIGINT,
        prefix varchar(2),
        voice_enabled BOOLEAN DEFAULT FALSE,
        voice_roles BIGINT ARRAY,
        invites_allowed BOOLEAN DEFAULT TRUE,
        voice_logging BOOLEAN DEFAULT FALSE,
        voice_channels BIGINT ARRAY,
        cleared_channels BIGINT ARRAY,
        modlog_enabled BOOLEAN DEFAULT FALSE,
        modlog_channels BIGINT ARRAY,
        logging_enabled BOOLEAN DEFAULT FALSE,
        logging_channels BIGINT ARRAY,
        welcome_message TEXT,
        welcome_channels BIGINT ARRAY,
        pm_welcome BOOLEAN DEFAULT FALSE,
        report_channel BIGINT,
        colour_enabled BOOLEAN DEFAULT FALSE,
        colour_template BIGINT,
        autoroles BIGINT ARRAY,
        joinable_roles BIGINT ARRAY,
        blacklist_channels BIGINT ARRAY,
        blacklist_users BIGINT ARRAY,
        disallowed_commands TEXT ARRAY,
        subreddit TEXT ARRAY,
        twitch TEXT ARRAY,
        twitter TEXT ARRAY,
        github TEXT ARRAY,
        ban_footer TEXT,
        kick_footer TEXT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id)
    );"""

    moderation = f"""
    CREATE TABLE IF NOT EXISTS {schema}.moderation (
        guild_id BIGINT,
        mod_id BIGINT,
        user_id BIGINT,
        index_id INT,
        type INT,
        reason TEXT,
        forgiven BOOLEAN DEFAULT FALSE,
        logtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id, user_id, index_id)
    );"""

    warnings = f"""
    CREATE TABLE IF NOT EXISTS {schema}.warnings (
        guild_id BIGINT,
        mod_id BIGINT,
        user_id BIGINT,
        index_id INT,
        reason TEXT,
        major BOOLEAN DEFAULT FALSE,
        forgiven BOOLEAN DEFAULT FALSE,
        logtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id, user_id, index_id)
    );"""

    macros = f"""
    CREATE TABLE IF NOT EXISTS {schema}.macros (
        guild_id BIGINT,
        creator_id BIGINT,
        name TEXT,
        content TEXT,
        hits INT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id, name)
    );"""

    quotes = f"""
    CREATE TABLE IF NOT EXISTS {schema}.quotes (
        guild_id BIGINT,
        origin_id BIGINT,
        quoted_id BIGINT,
        creator_id BIGINT,
        content TEXT,
        id INT,
        hits INT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id, id)
    );"""

    remindme = f"""
    CREATE TABLE IF NOT EXISTS {schema}.reminder (
        user_id BIGINT,
        content TEXT,
        id SERIAL,
        notify_in BIGINT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (id)
    );"""

    giveaway = f"""
    CREATE TABLE IF NOT EXISTS {schema}.giveaway (
        status BOOLEAN DEFAULT FALSE,
        guild_id BIGINT DEFAULT 0,
        channel_id BIGINT DEFAULT 0,
        num_winners INT DEFAULT 0,
        countdown_message_id BIGINT  DEFAULT 0,
        winner_message_id BIGINT DEFAULT 0,
        winners_id BIGINT ARRAY,
        gifter_id BIGINT DEFAULT 0,
        content TEXT,
        endtime TIMESTAMP,
        starttime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (countdown_message_id)
    );"""

    joinableinfo = f"""
    CREATE TABLE IF NOT EXISTS {schema}.joinableinfo (
        guild_id BIGINT,
        target_id BIGINT,
        info TEXT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (target_id)
    );"""

    reacts = f"""
    CREATE TABLE IF NOT EXISTS {schema}.reacts (
        guild_id BIGINT,
        base_message_id BIGINT,
        base_channel_id BIGINT,
        target_id BIGINT,
        react_id INT,
        react_type INT,
        group_id INT,
        group_name TEXT,
        user_ids BIGINT ARRAY,
        url TEXT,
        name TEXT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (base_message_id, react_id)
    );"""

    return (globalmacros, globcl, globul, globgl, glob_reports,
            guilds, moderation, warnings, macros, quotes,
            remindme, joinableinfo, reacts, giveaway)

# end of code

# end of file
