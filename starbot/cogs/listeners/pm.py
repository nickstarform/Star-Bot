
    async def on_message(self, message):
        if not isinstance(message.channel, discord.DMChannel):
            if message.channel.id != 429536153251741706:
                return
            if len(message.attachments) > 0:
                if random.randint(1, 10) > 8:
                    return
                await message.channel.send(
                    random.choice([
                        # doing it this way cause i don't want to actually implement probability
                        'Worst girl',
                        'Best girl',
                        'Worst girl',
                        'Best girl',
                        'Worst girl',
                        'Best girl',
                        'Worst girl',
                        'Best girl',
                        'Worst girl',
                        'Best girl',
                        'Worst girl',
                        'Best girl',
                        'Ew.',
                        'LMAO :joy: :joy:',
                        'Why is this even in the show'
                    ])
                )
            return
        if message.author.bot:
            return
        found_role = True
        if found_role:
            try:
                mod_info = self.bot.get_channel(259728514914189312)
                local_embed = discord.Embed(
                    title=f'DM report from {message.author.name}#{message.author.discriminator}:',
                    description=message.clean_content
                )
                if message.attachments:
                    desc = ''
                    for file in message.attachments:
                        desc += f'{file.url}\n'
                    local_embed.add_field(
                        name='Attachments',
                        value=f'{desc}',
                        inline=True
                    )
                await mod_info.send(embed=local_embed)
                await message.channel.send(':white_check_mark: You have submitted a report to the moderators. Abusing this function will get you kicked or banned. Thanks.')
                for user_id in self.bot.dm_forward:
                    user = await self.bot.get_user_info(user_id)
                    await user.create_dm()
                    await user.dm_channel.send(embed=local_embed)
            except Exception as e:
                self.bot.logger.warning(f'Issue forwarding dm: {e}')
