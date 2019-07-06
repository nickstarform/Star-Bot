"""Database Creator."""

# internal modules

# external modules
from asyncpg.pool import Pool

# relative modules

# global attributes
__all__ = ('make_tables', )
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


async def make_tables(pool: Pool, schema: str):
    await pool.execute('CREATE SCHEMA IF NOT EXISTS {};'.format(schema))
    for t in define_tables:
        await pool.execute(define_tables[t].replace('schema', schema))


define_tables = {
    'globalmacros': f"""
    CREATE TABLE IF NOT EXISTS schema.globalmacros (
        name TEXT,
        content TEXT,
        PRIMARY KEY (name)
    );""",

    'globcl': f"""
    CREATE TABLE IF NOT EXISTS schema.globalcmdbl (
        disallowed_command TEXT,
        PRIMARY KEY(disallowed_command)
    );""",

    'globul': f"""
    CREATE TABLE IF NOT EXISTS schema.globaluserbl (
        user_id BIGINT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY(user_id)
    );""",

    'globgl': f"""
    CREATE TABLE IF NOT EXISTS schema.globalguildbl (
        guild_id BIGINT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY(guild_id) 
    );""",

    'glob_reports': f"""
    CREATE TABLE IF NOT EXISTS schema.reports (
        user_id BIGINT,
        guild_id BIGINT,
        message TEXT,
        id SERIAL,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY(id, user_id)
    );""",

    'guilds': f"""
    CREATE TABLE IF NOT EXISTS schema.guilds (
        guild_id BIGINT,
        prefix varchar(2),
        voice_enabled BOOLEAN DEFAULT FALSE,
        invites_allowed BOOLEAN DEFAULT TRUE,
        voice_logging BOOLEAN DEFAULT FALSE,
        modlog_enabled BOOLEAN DEFAULT FALSE,
        logging_enabled BOOLEAN DEFAULT FALSE,
        welcome_message TEXT,
        pm_welcome BOOLEAN DEFAULT FALSE,
        report_channel BIGINT,
        colour_enabled BOOLEAN DEFAULT FALSE,
        colour_template BIGINT,
        singlejoinablerole BOOLEAN DEFAULT TRUE,
        ban_footer TEXT,
        kick_footer TEXT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id)
    );""",

    'vrole': f"""
    CREATE TABLE IF NOT EXISTS schema.voice_roles (
        vrole_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (vrole_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'vchan': f"""
    CREATE TABLE IF NOT EXISTS schema.voicelog_channels (
        vchan_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (vchan_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'modlog': f"""
    CREATE TABLE IF NOT EXISTS schema.modlog_channels (
        modlog_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (modlog_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'clear': f"""
    CREATE TABLE IF NOT EXISTS schema.cleared_channels (
        clear_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (clear_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'log': f"""
    CREATE TABLE IF NOT EXISTS schema.logging_channels (
        log_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (log_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'welcome': f"""
    CREATE TABLE IF NOT EXISTS schema.welcome_channels (
        welcome_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (welcome_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    # React PSQL Table
    # react_type 0=role, 1=channel,2=category
    'joinableinfo': f"""
    CREATE TABLE IF NOT EXISTS schema.joinableinfo (
        guild_id BIGINT,
        target_id BIGINT,
        info TEXT,
        join_type INT,
        url TEXT,
        name TEXT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (target_id),
        CHECK (join_type in (0, 1, 2)),
        UNIQUE (target_id, join_type),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'autorole': f"""
    CREATE TABLE IF NOT EXISTS schema.autoroles (
        autorole_id BIGINT,
        guild_id BIGINT,
        react_type INT DEFAULT 0,
        PRIMARY KEY (autorole_id, guild_id),
        CHECK (react_type = 0),
        FOREIGN KEY (joinrole_id, react_type) REFERENCES schema.joinableinfo (target_id, join_type)  ON DELETE CASCADE,
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'joinrole': f"""
    CREATE TABLE IF NOT EXISTS schema.joinable_roles (
        joinrole_id BIGINT,
        guild_id BIGINT,
        react_type INT DEFAULT 0,
        PRIMARY KEY (joinrole_id, guild_id),
        CHECK (react_type = 0),
        FOREIGN KEY (joinrole_id, react_type) REFERENCES schema.joinableinfo (target_id, join_type)  ON DELETE CASCADE,
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'joinable_users': f"""
    CREATE TABLE IF NOT EXISTS schema.joinable_users (
        user_id BIGINT,
        guild_id BIGINT,
        target_id BIGINT
        react_type INT DEFAULT 0,
        PRIMARY KEY (user_id, target_id),
        FOREIGN KEY (joinrole_id, react_type) REFERENCES schema.joinableinfo (target_id, join_type)  ON DELETE CASCADE,
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'reacts': f"""
    CREATE TABLE IF NOT EXISTS schema.reacts (
        guild_id BIGINT,
        base_message_id BIGINT,
        base_channel_id BIGINT,
        target_id BIGINT,
        react_id INT,
        react_type INT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (base_message_id, react_id),
        CHECK (react_type in (0, 1, 2)),
        FOREIGN KEY (joinrole_id, react_type) REFERENCES schema.joinableinfo (target_id, react_type) ON DELETE CASCADE,
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'reacts_users': f"""
    CREATE TABLE IF NOT EXISTS schema.reacts_users (
        react_id INT,
        user_id BIGINT,
        base_message_id BIGINT,
        PRIMARY KEY (user_id, base_message_id, react_id),
        FOREIGN KEY (base_message_id, react_id) REFERENCES schema.reacts (base_message_id, react_id) ON DELETE CASCADE
    );""",

    'blchannel': f"""
    CREATE TABLE IF NOT EXISTS schema.blacklist_channels (
        blchannel_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (blchannel_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'bluser': f"""
    CREATE TABLE IF NOT EXISTS schema.blacklist_users (
        bluser_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (bluser_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'blcmd': f"""
    CREATE TABLE IF NOT EXISTS schema.disallowed_commands (
        blcmd TEXT,
        guild_id BIGINT,
        PRIMARY KEY (blcmd, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'subreddit': f"""
    CREATE TABLE IF NOT EXISTS schema.subreddit (
        subreddit TEXT,
        pingrole_id BIGINT,
        guild_id BIGINT,
        type INT DEFAULT 0,
        CHECK (type = 0),
        FOREIGN KEY (pingrole_id, type) REFERENCES schema.joinableinfo (target_id, react_type) ON DELETE CASCADE,
        PRIMARY KEY (subreddit, guild_id),
        UNIQUE (subreddit, type),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'twitch': f"""
    CREATE TABLE IF NOT EXISTS schema.twitch (
        twitch TEXT,
        guild_id BIGINT,
        pingrole_id BIGINT,
        type INT DEFAULT 0,
        CHECK (type = 0),
        FOREIGN KEY (pingrole_id, type) REFERENCES schema.joinableinfo (target_id, react_type) ON DELETE CASCADE,
        UNIQUE (twitch, type),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE,
        PRIMARY KEY (twitch, guild_id)
    );""",

    'twitter': f"""
    CREATE TABLE IF NOT EXISTS schema.twitter (
        twitter TEXT,
        guild_id BIGINT,
        pingrole_id BIGINT,
        type INT DEFAULT 0,
        CHECK (type = 0),
        FOREIGN KEY (pingrole_id, type) REFERENCES schema.joinableinfo (target_id, react_type) ON DELETE CASCADE,
        PRIMARY KEY (twitter, guild_id),
        UNIQUE (twitter, type),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'github': f"""
    CREATE TABLE IF NOT EXISTS schema.github (
        github TEXT,
        guild_id BIGINT,
        pingrole_id BIGINT,
        type INT DEFAULT 0,
        CHECK (type = 0),
        FOREIGN KEY (pingrole_id, type) REFERENCES schema.joinableinfo (target_id, react_type) ON DELETE CASCADE,
        PRIMARY KEY (github, guild_id),
        UNIQUE (github, type),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'subreddit_chan': f"""
    CREATE TABLE IF NOT EXISTS schema.subreddit_chan (
        subreddit_chan_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (subreddit_chan_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'twitch_chan': f"""
    CREATE TABLE IF NOT EXISTS schema.twitch_chan (
        twitch_chan_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (twitch_chan_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'twitter_chan': f"""
    CREATE TABLE IF NOT EXISTS schema.twitter_chan (
        twitter_chan_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (twitter_chan_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'github_chan': f"""
    CREATE TABLE IF NOT EXISTS schema.github_chan (
        github_chan_id BIGINT,
        guild_id BIGINT,
        PRIMARY KEY (github_chan_id, guild_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'moderation': f"""
    CREATE TABLE IF NOT EXISTS schema.moderation (
        guild_id BIGINT,
        mod_id BIGINT,
        user_id BIGINT,
        index_id INT,
        type INT,
        reason TEXT,
        forgiven BOOLEAN DEFAULT FALSE,
        logtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id, user_id, index_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'warnings': f"""
    CREATE TABLE IF NOT EXISTS schema.warnings (
        guild_id BIGINT,
        mod_id BIGINT,
        user_id BIGINT,
        index_id INT,
        reason TEXT,
        major BOOLEAN DEFAULT FALSE,
        forgiven BOOLEAN DEFAULT FALSE,
        logtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id, user_id, index_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'macros': f"""
    CREATE TABLE IF NOT EXISTS schema.macros (
        guild_id BIGINT,
        creator_id BIGINT,
        name TEXT,
        content TEXT,
        hits INT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id, name),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'quotes': f"""
    CREATE TABLE IF NOT EXISTS schema.quotes (
        guild_id BIGINT,
        origin_id BIGINT,
        quoted_id BIGINT,
        creator_id BIGINT,
        content TEXT,
        id INT,
        hits INT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (guild_id, id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'remindme': f"""
    CREATE TABLE IF NOT EXISTS schema.reminder (
        user_id BIGINT,
        content TEXT,
        id SERIAL,
        notify_in BIGINT,
        currtime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (id)
    );""",

    'giveaway': f"""
    CREATE TABLE IF NOT EXISTS schema.giveaway (
        status BOOLEAN DEFAULT FALSE,
        guild_id BIGINT DEFAULT 0,
        channel_id BIGINT DEFAULT 0,
        num_winners INT DEFAULT 0,
        countdown_message_id BIGINT DEFAULT 0,
        winner_message_id BIGINT DEFAULT 0,
        gifter_id BIGINT DEFAULT 0,
        content TEXT,
        endtime TIMESTAMP,
        starttime TIMESTAMP DEFAULT current_timestamp,
        PRIMARY KEY (countdown_message_id),
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

    'giveaway_winners': f"""
    CREATE TABLE IF NOT EXISTS schema.giveaway_winners (
        countdown_message_id BIGINT DEFAULT 0,
        guild_id BIGINT DEFAULT 0,
        winner_id BIGINT,
        PRIMARY KEY (winner_id, countdown_message_id),
        FOREIGN KEY (countdown_message_id) REFERENCES schema.giveaway (countdown_message_id) ON DELETE CASCADE,
        FOREIGN KEY (guild_id) REFERENCES schema.guilds (guild_id) ON DELETE CASCADE
    );""",

}

# end of code

# end of file
