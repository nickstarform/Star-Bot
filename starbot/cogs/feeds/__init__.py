"""Main Feed Management Hub."""

# internal modules

# external modules

# relative modules
from cogs.feeds.github import Github
from cogs.feeds.reddit import Reddit
from cogs.feeds.twitch import Twitch
from cogs.feeds.twitter import Twitter

# global attributes
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)

_load = (Github, Reddit, Twitter,
         Twitch)


def setup(bot):
    for mod in _load:
        bot.add_cog(mod(bot))
        print(f'Loaded {mod.__name__}')

# end of code

# end of file
