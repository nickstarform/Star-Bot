"""Configuration Preparer.

Just import this file and call Config.X. This will
handle the required configuration parameters and
set them to immutable by use of enumerators.
"""

# internal modules
import yaml
import datetime
from enum import Enum
import os
import subprocess

# external modules

# relative modules

# global attributes
__all__ = ('Config',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

# general functions


def current_time():
    """
    Get Current time in botworld.

    Parameters
    ----------

    Returns
    -------
    str
        String format (Day Mon, DD YYYY HH:MM) of datetime in UTC
    """
    time = datetime.datetime.utcnow()
    return time.strftime('%A, %b %d %Y %H:%M')


def _construct(yml_c: dict, template_c: dict, token: str):
    """Configuration Constructor.

    Verify input configuration against a template.

    Parameters
    ----------
    yml_c : dict
        yaml dictionary to test
    template_c : dict
        template dictionary to test yaml against
    token : str
        The token to test

    Returns
    ----------
    str
        Either the yaml token if required or false.
    """
    class ConfigurationError(Exception):
        """Configuration Error.

        Custom Configuration Checker

        Parameters
        ----------
        token : string
            Token from the configuration template
        error : int
            Error Thrown

        Returns
        ----------
        """
        def __init__(self, token: str, error: int):

            # Call the base class constructor with the parameters it needs
            self.error = error
            self.token = token
            self.message = '\n'
            if self.error == 0:
                self.message += 'Configuration Mismatch!\n'
                self.message += f'The configuration parameter: {self.token} is not valid.'
            elif self.error == 1:
                self.message += 'Configuration Incomplete!\n'
                self.message += f'The configuration parameter: {self.token} cannot be blank.'
            elif self.error == 2:
                self.message += 'Configuration Invalid!\n'
                self.message += f'The configuration parameter: {self.token} was not found.'
            super().__init__(self.message)
        def __repr__(self):
            print(self.message)

    # function does general tests of the key and calls _raise
    def _test(yml_c: dict, token: str, test: bool) -> str:
        # first check if is null
        try:
            if isinstance(yml_c[token], type(None)):
                # throw blank
                return _raise(test, 1, token)
        except:
            # throw not found
            return _raise(test, 2, token)
        if len(str(yml_c[token])) <= 1:
            # throw invalid
            return _raise(test, 0, token)
        return str(yml_c[token])

    # handles raising errors if param required
    def _raise(test: bool, num: int, token: str) -> str:
        if test:
            raise ConfigurationError(token, num)
            exit()
        else:
            return ''

    # general caller
    return _test(yml_c, token, template_c[token])


class BaseConfig(Enum):
    """
    Super Config Class.

    This enumeration class extension will
    serve as the primary holder for the config.
    We shall expand this later and use as an enumerator.

    Parameters
    ----------

    Returns
    -------
    """

    Loaded = False
    pass

if str(os.getcwd())[-4:] != 'docs':
    # template configuration, key: required (True/False)
    template = {'token': True, 'owner_id': True, 'devel_id': True, 'avatar': False,
                'bot_key': False, 'bot_id': True, 'support_server': False,
                'psql_username': True, 'psql_passwd': False, 'psql_dbname': True,
                'psql_port': True, 'psql_host': True, 
                'maluser': False, 'malpass': False,
                'twitch_token': False,
                'battlenet_token': False,
                'imgur_token': False,
                'redditusername': False, 'redditpassword': False,
                'redditkey': False, 'redditsecret': False,
                'twitterappkey': False, 'twitterappsecret': False,
                'twittertokenkey': False, 'twittertokensecret': False, 'github': False}

    # load in the yaml configuration file for parsing
    with open(f"{__path__}/config.yml", 'r') as yml_config:
            y_c = yaml.load(yml_config)
    with open(f"{__path__}/../../.version", 'r') as v:
            version = v.read()

    __MAPPING__ = {'date': current_time()}
    for key in template.keys():
        __MAPPING__[key] = _construct(y_c, template, key)

    # static variables for discord
    BOT_INVITE = 'https://discordapp.com/oauth2/authorize?'\
        'client_id=$repl$&scope=bot&permissions=0'
    DISCORD = 'https://discordapp.com/invite/$repl$'

    # redefine custom mapping
    if __MAPPING__['support_server']:
        __MAPPING__['support_server'] = f"{DISCORD.replace('$repl$', __MAPPING__['support_server'])}"
    if __MAPPING__['bot_key']:
        __MAPPING__['bot_key'] = f"{BOT_INVITE.replace('$repl$', __MAPPING__['bot_key'])}"
    __MAPPING__['psql_cred'] = {}
    __MAPPING__['psql_cred']['user'] = __MAPPING__['psql_username']
    __MAPPING__['psql_cred']['password'] = __MAPPING__['psql_passwd']
    __MAPPING__['psql_cred']['database'] = __MAPPING__['psql_dbname']
    __MAPPING__['psql_cred']['port'] = __MAPPING__['psql_port']
    __MAPPING__['psql_cred']['host'] = __MAPPING__['psql_host']

    # versioning
    __MAPPING__['version'] = version
    try:
        label = subprocess.check_output(['git', 'describe', '--always']).strip().decode()
    except:
        label = ''
    __MAPPING__['githash'] = label
    __MAPPING__['Loaded'] = True

    # store into Config object for easy loading
    Config = Enum('BaseConfig', names=__MAPPING__)
else:
    __MAPPING__ = {'date': current_time()}
    Config = Enum('BaseConfig', names=__MAPPING__)

if __name__ == "__main__":
    print('Testing')
    print(Config.__members__)

# end of code

# end of file
