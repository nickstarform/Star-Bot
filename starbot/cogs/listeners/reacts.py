
    async def on_raw_reaction_add(self, payload):
        """
        Called when an emoji is added
        """
        target_channel = await self.bot.postgres_controller.get_target_channel(payload.channel_id, payload.message_id)
        if not target_channel:
                return 
        user = self.bot.get_user(payload.user_id)
        channel = self.bot.get_channel(target_channel)
        reacts = await self.bot.postgres_controller.add_user_reaction(payload.user_id, payload.message_id)
        if int(reacts) in [10,20,100]:
                time = self.bot.timestamp()
                mod_info = self.bot.get_channel(259728514914189312)
                await mod_info.send(
                    f'**{time} | REACTION SPAM:** {user} has reacted {reacts} '\
                    f'times today on the permission message for #{channel}'
                )
        await self.add_perms(user, channel)

    async def on_raw_reaction_remove(self, payload):
        """
        Called when an emoji is removed
        """
        target_channel = await self.bot.postgres_controller.get_target_channel(payload.channel_id, payload.message_id)
        if not target_channel:
            return
        channel = self.bot.get_channel(target_channel)
        user = self.bot.get_user(payload.user_id)
        await self.remove_perms(user, channel)
    
    async def add_perms(self, user, channel):
        """
        Adds a user to channels perms
        """
        try:
            await channel.set_permissions(user, read_messages=True)
        except Exception as e:
            self.bot.logger.warning(f'{e}')  

    async def remove_perms(self, user, channel):
        """
        removes a users perms on a channel
        """
        try:
            await channel.set_permissions(user, read_messages=False)
        except Exception as e:
            self.bot.logger.warning(f'{e}')  
