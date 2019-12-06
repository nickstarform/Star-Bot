class Observations(metaclass=utils.MetaCog, thumbnail='https://i.imgur.com/oA6lvQq.png'):
    """Commands which help you understand this cruel world and its surrounds better.
    Maybe..."""

    def __init__(self, bot):
        self.bot = bot

    @property
    def weather_key(self):
        return self.bot._config.get('WEATHER', '_token')

    @property
    def nasa_key(self):
        return self.bot._config.get('NASA', '_token')

    @commands.command(name='weather', cls=utils.EvieeCommand)
    async def get_weather(self, ctx, *, location: str=None):
        """Retrieve weather information for a location.
        Parameters
        ------------
        location: [Required]
            The location to retrieve weather information for.
        Examples
        ----------
        <prefix>weather <location>
            {ctx.prefix}weather Sydney
        """
        if not location:
            return await ctx.send('Please provide a valid location.')

        try:
            resp, cont = await self.bot.aio('get', url=f'http://api.apixu.com/v1/current.json?'
                                                       f'key={self.weather_key}&'
                                                       f'q={location}', return_attr='json')
        except Exception as e:
            self.bot.dispatch('command_error', ctx, e)
            return await ctx.send(f'There was an error retrieving weather information:\n```css\n{e}\n```')

        loc = cont['location']
        current = cont['current']
        condition = current['condition']

        if current['is_day'] == 1:
            colour = 0xFDB813
        else:
            colour = 0x546bab

        embed = discord.Embed(title=f'Weather for {loc["name"]}, {loc["region"]} {loc["country"]}',
                              description=f'{condition["text"]}', colour=colour)
        embed.set_thumbnail(url=f'http:{condition["icon"]}')

        embed.add_field(name='Temp', value=f'{current["temp_c"]}℃ | {current["temp_f"]}℉')
        embed.add_field(name='Feels Like', value=f'{current["feelslike_c"]}℃ | {current["feelslike_f"]}℉')
        embed.add_field(name='Humidity', value=f'{current["humidity"]}%')
        embed.add_field(name='Cloud Coverage', value=f'{current["cloud"]}%')
        embed.add_field(name='Wind Speed', value=f'{current["wind_kph"]}kph | {current["wind_mph"]}mph')
        embed.add_field(name='Wind Direction', value=f'{current["wind_dir"]} - {current["wind_degree"]}°')
        embed.add_field(name='Precipitation', value=f'{current["precip_mm"]}mm | {current["precip_in"]}in')
        embed.add_field(name='Visibility', value=f'{current["vis_km"]}km | {current["vis_miles"]}miles')
        embed.set_footer(text=f'Local Time: {loc["localtime"]}')

        await ctx.send(embed=embed)

    @commands.command(name='apod', aliases=['iotd'], cls=utils.EvieeCommand)
    async def nasa_apod(self, ctx):
        """Returns NASA's Astronomy Picture of the day.
        Examples
        ----------
        <prefix>apod
            {ctx.prefix}apod
        """
        url = f'https://api.nasa.gov/planetary/apod?api_key={self.nasa_key}'

        try:
            resp, cont = await self.bot.aio(method='get', url=url, return_attr='json')
        except Exception as e:
            return await ctx.send(f'There was an error processing APOD.\n```css\n[{e}]\n```')

        embed = discord.Embed(title='Astronomy Picture of the Day', description=f'**{cont["title"]}** | {cont["date"]}'
                                                                                f'\n{cont["explanation"]}')

        img = cont["url"]
        if not img.endswith(('gif', 'png', 'jpg')):
            embed.add_field(name='Watch', value=f"[Click Me](http:{cont['url']})")
        else:
            embed.set_image(url=cont['url'])

        try:
            embed.add_field(name='HD Download', value=f'[Click here!]({cont["hdurl"]})')
        except KeyError:
            pass

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text='Generated ')

        await ctx.send(embed=embed)

    @commands.command(name='epic', aliases=['EPIC'], cls=utils.EvieeCommand)
    async def nasa_epic(self, ctx):
        """Returns NASA's most recent EPIC image.
        Examples
        ---------
        <prefix>epic
            {ctx.prefix}epic
        """
        # todo Add the ability to select a date.
        base = f'https://api.nasa.gov/EPIC/api/natural?api_key={self.nasa_key}'
        img_base = 'https://epic.gsfc.nasa.gov/archive/natural/{}/png/{}.png'

        try:
            rep, cont = await self.bot.aio(method='get', url=base, return_attr='json')
        except Exception as e:
            return await ctx.send(f'There was an error processing your EPIC request.\n```css\n[{e}]\n```')

        img = random.choice(cont)
        coords = img['centroid_coordinates']

        embed = discord.Embed(title='NASA EPIC', description=f'{img["caption"]}', colour=0x1d2951)
        embed.set_image(url=img_base.format(img['date'].split(' ')[0].replace('-', '/'), img['image']))
        embed.add_field(name='Centroid Coordinates',
                        value=f'Lat: {coords["lat"]} | Lon: {coords["lon"]}')
        embed.add_field(name='Download',
                        value=f"[Click Me]({img_base.format(img['date'].split(' ')[0].replace('-', '/'), img['image'])})")

        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text='Generated on ')

await ctx.send(embed=embed)