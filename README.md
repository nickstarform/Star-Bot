# Welcome to Star-Bot, an open source Discord Bot, based off of [JDA](https://github.com/DV8FromTheWorld/JDA), adapted from Momo by Kagumi. Very robust and will handle many things: from sending Twitch.tv notifications to playing music, to temporarily muting troublemakers, Star-Bot can do a lot for your server.


## Can I just add Star-Bot to my server?
Current Star-Bot is self-hosted for the server [Erect Eggplants] and [OU SRT]. However this code is provide as an effort to further Kagumi's legacy and to provide additional functionalities to the original Momo.

### Features? Gimme some info!
* Reddit, Twitter, & Twitch.tv feeds - Get updates directly to your channel of choice with image/preview configuration
* Play music in a music channel. Can play off direct Youtube searches, too!
* Role management: Set roles as *joinable* and allow users to join/leave at their whim
* Bring up character for various video games: FFXIV, WoW, osu! *(LoL & Overwatch coming soon!)*
* Commands to ban, kick, and prune messages
* Create a strawpoll from discord & directly link it to your users
* Log channel for user join/leaves, bans, kicks, and nickname changes
* **Upcoming** A profile for separating roles and groups in order to better organize servers and an RPG game to play on the server.


---

## Hosting Star-Bot for yourself
`you need java 8 to run this bot`

* If you want to host your own instance of the bot, feel free to take a look at the Releases tab and download the package. Fill out the configuration in the `resources/Bot.properties` file, then run `java -jar Star-Bot-x.x.x.jar` where `x.x.x` is the current version. 
* To obtain a bot token from Discord, head on over to the [Discord Developers](https://discordapp.com/developers/applications/me) page. From there, you can create an Application, then convert it to a Bot account. Then, click to show the bot token, which you can copy and paste into `Bot.properties`
* Hosting Star-Bot for yourself nets you some benefits. Music functionality, though dependent on your internet speeds, will be better for single servers than a larger cluster. You can also change its username, avatar, and game status to whatever you see fit!

---

## Pulling from the source & building
Star-Bot uses [Apache Maven](https://maven.apache.org/) for project management. As such, it's extremely simple managing Java dependencies, so building any edits and changes you want into your own bot is easy.

#### Installing Maven
Linux: `apt-get install maven`

Windows & macOS: [download the package](http://maven.apache.org/download.cgi) and follow the instructions in the previously linked install page

**Windows & macOS alternative**

Windows & macOS users can install [Chocolatey](https://chocolatey.org/) & [Homebrew](http://brew.sh/) respectively to get `apt-get` functionality

chocolatey: `choco install maven`

homebrew: `brew install maven`

#### Building
Run `mvn install` on the root directory. This will create two builds: a `.jar` of the bot's source & a `.jar` with all the dependencies shaded (all packaged into a single file). This is the file you want - `Star-Bot-x.x.x.jar`. On subsequent builds, if you do not run the command with the `clean` parameter, then all `.jar` will be the correct bot.

**NOTE**: `mvn install` *does not* copy the resources folder to the `target/` directory. As a side effect, it *will not* overwrite pre-existing resources, so you are free to copy over `resources/` to `target/`.

**NOTE 2**: If you decide to run `mvn clean install`, *all folders and files in* `target/` *will be deleted*. Just a forewarning before you lose all of your server's data

#### Running
Once you have built the jar, simply run `java -jar Star-Bot-x.x.x.jar` where `x.x.x` is the current version numbering. 

### Creating a command
Probably the #1 reason people will run their own bot, and probably the easiest thing to implement with Star-Bot. This example also shows how permissions are setup, so if you want to change the permission level of commands... You're in the right place.

1. Create a new class file. Must be in the `io.ph.bot.commands` package.

2. Let's say you call your command `Echo`, and it echoes whatever the user says. Make sure to have your file extend `io.ph.bot.commands.Command` and to override `run(Message msg)`

3. The meat of your command goes in the aformentioned `run` method. For brevity, our command ignore package and imports.
```java
public class Say extends Command {
    @Override
    public void run(Message msg) {
        msg.getChannel().sendMessage(Util.getCommandContents(msg)).queue();
    }
}
```
To then have the command register through the command handler, annotate the class with `io.ph.commands.CommandData`
```java
@CommandData (
		defaultSyntax = "echo",
		aliases = {"repeat", "ech0"},
		permission = Permission.NONE,
		description = "Have the bot repeat after you",
		example = "This will be echoed!"
		)
public class Say extends Command {
    @Override
    public void run(Message msg) {
		msg.getChannel().sendMessage(Util.getCommandContents(msg)).queue();
    }
}
```
It's as easy as that~ 

note: commands with permission `Permission.NONE` are disableable by admins by using the `disable` command

If you're going to delve deeper into developing with JDA, check out the documentation [here](http://home.dv8tion.net:8080/job/JDA/Promoted%20Build/javadoc/) and join up at the [Discord API server](https://discordapp.com/invite/0SBTUU1wZTWPnGdJ).




# root

* The pom.xml file is the xml representation of the Maven Project. POM stands for "Project Object Model".
This contains the dependencies and licenses for the entire maven project.

* The OPcide Reference.md Lists the opcodes for the client handshakes that are initiated to the discord api

# resource
* avatar

** holds the pictures that Star-Bot can use for her avatar

* config

** DefaultGlobalSettings.properties houses the defaukt

* database houses the first sqlite database that the rest of the databases are based off of

* guilds

** Will normally house the guilds here + the template information for the guilds

* Bot properties is an important file that acts as the configuration file for your server. Fill out the necessary fields (bot token and bot owner) and you can begin. The file should be self explainatory


# src/io/ph
* bot

** bot.java

*** Singleton instance of the entire bot. Includes configuration and the main JDA singleton

** launder.java

*** Main entry point and setup directories

** state.java

*** Various helper methods to change the state of the bot

** audio

*** houses all audio events

** commands

*** Command.java

**** sets up the command modules to be run, is dynamic and checks permissions

*** CommandCategories

**** Defines the command categories to be used and callable by anyone

*** COmmandData

**** defines the syntax for the command files

*** CommandHandler

****  A centralized class that manages all commands available across servers

*** administration

**** admin commands to modify server

*** fun

**** fun commands that anyone can run and have no lasting affects on server

*** games

**** will look up characters in each of the games, based from the RESTWrapper repo

*** general

**** everyone can use these commands but these can have more lasting affects as they can range from all  users to light mod commands

*** japanese

**** scripts for looking up anime, jap words, or theme songs

*** moderation

**** These are mod/admin/owner only commands. These have the potential to spam the server or drastically change the way they function

*** music

**** These commands are only available to those with the dj role

*** owner

**** commands only available to the bot owner and will change globally the commands of the bot. use with caution

** events

*** defines separate events for when people are muted/unmuted

** exceptions

*** Lists of exceptions that are described and throwable in the code

** feed

*** The different feeds that the bot has, reddit, twitch, twitter

** jobs

*** command files for the scheduled or frequent jobs

** listeners

*** very important to the chaning of events in the guild like people entering, leaving, joining, etc

** model

*** provides the model layout for generic objects or frequently used objects

** procedural

*** defines command that come in a sequence like yes no commands etc

** scheduler

*** periodically checks for changes in feeds or event updates

** ws

*** handles incoming and outgoing connections. Check the opcode reference in root directory

* db

** setup files for the handling of sqlite databases

* rest

** initialize cache size

* util

** sends message to channels/users and handles receiving of messages




When you add a command, make sure you place command in the io.ph.bot.commands directory

