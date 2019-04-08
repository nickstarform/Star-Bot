"""."""

# internal modules
import urllib
import aiohttp
import re
import urllib.parse
import random
import math

# external modules
from discord.ext import commands
import requests
import discord

# relative modules
from cogs.utilities import Colours, permissions
from cogs.utilities.functions import current_time
from cogs.utilities.message_general import generic_message
from cogs.utilities.embed_general import generic_embed, MAX_LEN
from cogs.utilities.embed_dialog import respond

# global attributes
__all__ = ('Fun',)
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


def setup(bot):
    bot.add_cog(Fun(bot))
    print('Loaded Fun')


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball'])
    @commands.guild_only()
    async def eightball(self, ctx: commands.Context, *, _: str):
        """Classic 8ball.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        question: str
            question to ask

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'eightball'):
            return
        answers = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes, definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy, try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful"
        ]
        answer = random.choice(answers)
        await generic_message(ctx, [ctx.channel], f'🔮{answer}🔮', -1)
        pass

    @commands.command(aliases=['judge', 'match'])
    @commands.guild_only()
    async def rate(self, ctx: commands.Context, *, user: str=None):
        """Rate someone.

        Either rate another user or see how the bot rates you.
        Are you sure you want to know...

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        user: str
            some normal format of a user

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'rate'):
            return
        if isinstance(user, type(None)):
            text = ctx.author
        else:
            text = get_member(ctx, user)
        if not isinstance(text, type(None)):
            text = text.id
        else:
            await respond(ctx, False)
            return

        rated = (int(text) + int(ctx.author.id)) % 10
        if isinstance(user, type(None)):
            await generic_message(ctx, [ctx.channel], f'I rate you {rated + 1}/10', -1)
        else:
            await generic_message(ctx, [ctx.channel], f'I rate them {rated + 1}/10', -1)
        pass

    @commands.command(aliases=['sample', 'num'])
    @commands.guild_only()
    async def number(self, ctx: commands.Context, minimum: int=0, maximum: int=100):
        """Uniform sample between two values.

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        minimum: int
            minimum number
        maximum: int
            max number

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'number'):
            return
        val = minimum + (maximum - minimum) * random.random()
        await generic_message(ctx, [ctx.channel], f'Random number: {val}', -1)
        pass

    @commands.command(aliases=['chose', 'choice', 'pick', 'which'])
    @commands.guild_only()
    async def choose(self, ctx: commands.Context, *, text:str):
        """Pick from a list.

        Must be delimited by `,` or `;` or `|` or `or` or ` ` in that order

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        text: str
            string of choices

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'choose'):
            return
        delimiters = (',', ';', '|', 'or', ' ')
        choices = [text]
        i = 0
        while len(choices) == 1:
            choices = choices[0].split(delimiters[i])
            i += 1
            if (i >= len(delimiters)) and (len(choices) == 1):
                await generic_message(ctx, [ctx.channel], f'Something wrong with your input: {text}', 10)
                await respond(ctx, False)
        choice = random.choice(choices)
        await generic_message(ctx, [ctx.channel], f'I pick "{choice}"', -1)
        pass

    @commands.command(aliases=['dice', 'd20'])
    @commands.guild_only()
    async def roll(self, ctx: commands.Context, *, text: str='d20', explicit: bool=True):
        """Classic dice roller.

        Dice roller that tries to be intelligent:
        d20
        d8+2
        d2-1
        4d9+4

        Parameters
        ----------
        ctx: :func: commands.Context
            the context command object
        text: str
            The possible dice combo
        explicit: bool
            List the full roll sequence.

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'roll'):
            return
        text = text.lower()
        explicit = False if 'false' in text else True
        text = text.replace(' ', '')
        text = text.replace(str(explicit).lower(), '')
        regex = f'([0-9]*)(d)([0-9]*)(\-?\+?)([0-9]*)'
        match = re.findall(regex, text)[0]
        if match[2] == '0':
            await generic_message(ctx, [ctx.channel], 'Rolled with a d0 dummy', 5)
            return
        if int(match[0]) > 100:
            await generic_message(ctx, [ctx.channel], 'Please roll with something less than 100dice', 5)
            return
        numdice = int(match[0], base=10) if match[0] else 1
        sides = int(match[2], base=10) if match[2] else 20
        mod = int(''.join(match[3:]), base=10) if match[3] else 0
        rolls = [random.randint(1, sides) for x in range(numdice)]
        title = f'Rolling: **{"".join(match)}**'
        if explicit:
            contructor = f'{title}\n```  ROLLS  |  TOTAL  |  TOTAL + MOD  \n'\
                           f'-----------------------------------\n'
        else:
            contructor = title
        total = 0
        tracker = 0
        for i, roll in enumerate(rolls):
            total += roll
            if explicit: 
                tmp = f'{roll:>9}|{total:>9}|{(total + mod * (i + 1)):>15}\n'
                contructor += f'{tmp}'
        if explicit:
            contructor += f'-----------------------------------\n'
        contructor += f'AVG: {float(total / numdice) + mod}  EXPECTED: {(math.ceil(sides / 2) + 1 + mod)}  TOTAL: {total + numdice * mod}```'
        await generic_message(ctx, [ctx.channel], contructor, -1, splitwith='```')
        return

    @commands.command(aliases=['sleep', 'night'])
    @commands.guild_only()
    async def kaga(self, ctx):
        """Grab kaga image.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'kaga'):
            return
        try:
            url = 'https://api.imgur.com/3/album/WtrQ0/images'
            headers = {'Authorization': 'Client-ID ' + self.bot.config.imgur_token.value}
            r = requests.get(url, headers=headers)
            if int(r.status_code) > 399:
                raise RuntimeError
        except Exception as e:
            await generic_message(ctx, [ctx.channel], f'{e}', -1)
            await respond(ctx, False)
            return
        responce = r.json()['data']
        chose = random.choice(responce)
        await generic_message(ctx, [ctx.channel], f'{chose["link"]}', -1)
        pass

    @commands.command(aliases=['words', 'japanese', 'translate'])
    @commands.guild_only()
    async def jisho(self, ctx: commands.Context, word: str):
        """Translates using jisho.

        Japanese to English, and English to Japanese
        Works with Romaji, Hiragana, Kanji, and Katakana.

        Parameters
        ----------
        word: str
            translate this single word

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'jisho'):
            return
        self.connector = aiohttp.TCPConnector(force_close=True)
        self.session = aiohttp.ClientSession(connector=self.connector)
        search_args = await self.dict_search_args_parse(ctx, word.lower())
        if not search_args:
            await self.session.close()
            return
        limit, query = search_args
        message = urllib.parse.quote(query, encoding='utf-8')
        url = "http://jisho.org/api/v1/search/words?keyword=" + message
        async with self.session.get(url) as response:
            data = await response.json()
        try:
            messages = [self.parse_data(result) for result in data["data"][:limit]]
        except KeyError:
            await respond(ctx, False)
            await self.session.close()
            return await ctx.send("I was unable to retrieve any data", delete_after=5)
        try:
            await ctx.send('\n'.join(messages))
        except discord.HTTPException:
            await respond(ctx, False)
            await ctx.send("No data for that word.")
        await self.session.close()
        pass

    def parse_data(self, result):
        japanese = result["japanese"]
        output = self.display_word(japanese[0], "**{reading}**",
                                   "**{word}** {reading}") + "\n"
        new_line = ""
        if result["is_common"]:
            new_line += "Common word. "
        if result["tags"]:
            new_line += "Wanikani level " + ", ".join(
                [tag[8:] for tag in result["tags"]]) + ". "
        if new_line:
            output += new_line + "\n"
        senses = result["senses"]
        for index, sense in enumerate(senses, 1):
            parts = [x for x in sense["parts_of_speech"] if x is not None]
            if parts == ["Wikipedia definition"]:
                continue
            if parts:
                output += "*{}*\n".format(", ".join(parts))
            output += "{}. {}".format(index, "; ".join(sense["english_definitions"]))
            for attr in ["tags", "info"]:
                if sense[attr]:
                    output += ". *{}*.".format("".join(sense[attr]))
            if sense["see_also"]:
                output += ". *See also: {}*".format(", ".join(sense["see_also"]))
            output += "\n"
        if len(japanese) > 1:
            output += "Other forms: {}\n".format(", ".join(
                [self.display_word(x, "{reading}", "{word} ({reading})") for x in
                 japanese[1:]]))
        return output

    def display_word(self, obj, *formats):
        return formats[len(obj) - 1].format(**obj)

    async def dict_search_args_parse(self, ctx: commands.Context, message):
        if not message:
            return await ctx.send("Error in arg parse")
        limit = 1
        query = message
        result = re.match(r"^([0-9]+)\s+(.*)$", message)
        if result:
            limit, query = [result.group(x) for x in (1, 2)]
        return int(limit), query

    @commands.command(aliases=['kitsu'])
    @commands.guild_only()
    async def anime(self, ctx: commands.Context, *, term: str=None):
        """Search for an anime from Kitsu.io.

        Will search for the keyword anime or manga and use that to
        further search on kitsu. If neither is found it will default
        to searching for anime.

        Parameters
        ----------

        Returns
        -------
        """
        if await permissions.is_cmd_blacklisted(self.bot, ctx.guild.id, 'anime'):
            return
        if not term:
            return
        term = term.lower()
        search = '/'
        if 'manga' in term:
            search += 'manga'
        else:
            search += 'anime'
        term = term.replace(search, '')
        search = f'{search}?filter[text]='
        search += urllib.parse.quote_plus(term)

        try:
            url = 'https://kitsu.io/api/edge' + search
            headers = {
                'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json',
            }
            r = requests.get(url, headers=headers)
            if int(r.status_code) > 399:
                raise RuntimeError
        except Exception as e:
            e = e if e != '' else 'None defined'
            await generic_message(ctx, [ctx.channel], f'{e},{url}', -1)
            await respond(ctx, False)
            return

        def gather(di: dict, fields: list):
            ret = []
            for f in fields:
                try:
                    ret.append(di[f])
                except:
                    ret.append('')
            return ret
        def no(li):
            for f in li:
                if not isinstance(f, type(None)) and f != '' and f.lower() != 'none':
                    return f

        responce = r.json()['data'][0]
        link = gather(responce['links'], ['self'])[0]
        attr = gather(responce['attributes'], ['synopsis',
                                               'createdAt',
                                               'titles',
                                               'averageRating',
                                               'startDate',
                                               'endDate',
                                               'coverImage',
                                               'status',
                                               'episodeCount'])
        syn, create, titles, rating, start, stop, image, status, ep = attr
        image = no(gather(image, ['original', 'large', 'tiny']))
        fields = []
        if 'en' in titles.keys():
            fields.append(['English', titles['en']])
        if 'en_jp' in titles.keys():
            fields.append(['Romaji', titles['en_jp']])
        if 'ja_jp' in titles.keys():
            fields.append(['Japanese', titles['ja_jp']])
        fields.append(['Type', responce['type']])
        fields.append(['Start Date', start])
        fields.append(['End Date', stop])
        fields.append(['Rating', rating + '/100'])
        fields.append(['Episodes', ep])
        fields.append(['Kitsu Creation', create])
        embeds = generic_embed(title=responce['attributes']['canonicalTitle'],
                               desc=syn,
                               fields=fields,
                               footer=f'[Info from Kitsu.io] ' + current_time(),
                               colours=Colours.COMMANDS,
                               image=image,
                               url=link
                              )
        for embed in embeds:
            await ctx.send(embed=embed)

if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    test()
    print('Test Passed')

# end of code

# end of file
