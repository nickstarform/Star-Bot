"""Database Creator."""

# internal modules
from typing import Optional
import datetime

# external modules
from asyncpg.pool import Pool

# relative modules

# global attributes
__all__ = ('make_tables', 'tables')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

tables = ('glob', 'glob_reports', 'guilds', 'moderation',
          'warnings', 'spamming', 'macros', 'quotes',
          'joinableroles', 'reacts', 'joinableinfo')


async def make_tables(pool: Pool, schema: str):
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
    str
        Either the yaml token if required or false.
    """
    await pool.execute('CREATE SCHEMA IF NOT EXISTS {};'.format(schema))

    glob = f"""
    CREATE TABLE IF NOT EXISTS {schema}.global (
        disallowed TEXT ARRAY,
        allowed TEXT ARRAY,
        guild_blacklist BIGINT ARRAY,
        user_blacklist BIGINT ARRAY,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY(currtime)
    );"""

    glob_reports = f"""
    CREATE TABLE IF NOT EXISTS {schema}.reports (
        user_id BIGINT,
        message TEXT,
        id INT NOT NULL AUTO_INCREMENT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY(id, user_id)
    );"""

    guilds = f"""
    CREATE TABLE IF NOT EXISTS {schema}.guilds (
        guild_id BIGINT,
        prefix varchar(2),
        voice_role_enabled BOOLEAN DEFAULT FALSE,
        voice_roles BIGINT ARRAY,
        invites_allowed BOOLEAN DEFAULT TRUE,
        voice_logging BOOLEAN DEFAULT FALSE,
        voice_channels BIGINT ARRAY,
        cleared_chanels BIGINT ARRAY,
        modlog_enabled BOOLEAN DEFAULT FALSE,
        modlog_channels BIGINT ARRAY,
        logging_enabled BOOLEAN DEFAULT FALSE,
        logging_channels BIGINT ARRAY,
        welcome_message TEXT,
        welcome_channels BIGINT ARRAY,
        pm_welcome BOOLEAN DEFAULT FALSE,
        send_welcome_channel BOOLEAN DEFAULT FALSE,
        report_channel BIGINT,
        rules_channel BIGINT,
        autoroles BIGINT ARRAY,
        joinable_roles BIGINT ARRAY,
        blacklist_channels BIGINT ARRAY,
        blacklist_users BIGINT ARRAY,
        ban_footer TEXT,
        kick_footer TEXT,
        faq TEXT,
        rules TEXT,
        misc TEXT,
        bots TEXT,
        channels TEXT,
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

    joinableinfo = f"""
    CREATE TABLE IF NOT EXISTS {schema}.joinableinfo (
        target_id BIGINT,
        info TEXT ARRAY,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (target_id)
    );"""

    reacts = f"""
    CREATE TABLE IF NOT EXISTS {schema}.reacts (
        guild_id BIGINT,
        base_message_id BIGINT,
        target_id BIGINT,
        react_id BIGINT,
        react_role BOOLEAN DEFAULT FALSE,
        react_channel BOOLEAN DEFAULT FALSE,
        react_category BOOLEAN DEFAULT FALSE,
        info TEXT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (base_message_id, react_id)
    );"""

    await pool.execute(glob)
    await pool.execute(glob_reports)
    await pool.execute(guilds)
    await pool.execute(moderation)
    await pool.execute(warnings)
    await pool.execute(spamming)
    await pool.execute(macros)
    await pool.execute(quotes)
    await pool.execute(joinableinfo)
    await pool.execute(reacts)

# end of code

# end of file
