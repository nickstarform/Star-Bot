========
Star Bot
========

Welcome to `Star-Bot`, an open source Discord Bot. Originally based from Momo by Kagumi. However, the project completely diverged early and prompted a rewrite from Java to Python (yay). The bot focuses on moderation and additionally will handle many things: from sending Twitch.tv notifications, to temporarily muting troublemakers, `Star-Bot` can do a lot for your server.


Can I just add Star-Bot to my server?
=====================================
Current Star-Bot is self-hosted. However contact Nick\@1944 on discord to get an invite.


Features? Gimme some info!
==========================
* Reddit, Twitter, & Twitch.tv feeds - Get updates directly to your channel of choice with image/preview configuration
* Role management: Set roles as *joinable* and allow users to join/leave at their whim
* Reaction roles: Setup reactions roles
* Commands to ban, kick, and prune messages
* Log channel for user join/leaves, bans, kicks, and nickname changes
* Also check out the `Changelog <./changelog.rst>`_


Hosting Star-Bot for yourself
=============================

- If you want to host your own instance of the bot, feel free to take a look at the Releases tab and download the package. Fill out the configuration in the `config/config.yml`_ file, then run `docker-compose`. 
- To obtain a bot token from Discord, head on over to the `Discord Developers`_ page. From there, you can create an Application, then convert it to a Bot account. Then, click to show the bot token, which you can copy and paste into `config/config.yml`

.. _`Discord Developers`: https://discordapp.com/developers/applications/me

- Hosting Star-Bot for yourself nets you some benefits. You can change its username, avatar, and game status to whatever you see fit!

<> with <3 by Nick
