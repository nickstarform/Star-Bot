"""."""

# internal modules

# external modules

# relative modules

# global attributes
__all__ = ('test', 'main', 'Default')
__filename__ = __file__.split('/')[-1].strip('.py')
__path__ = __file__.strip('.py').strip(__filename__)


    async def on_voice_state_update(self, member, before, after):
        vc_logging = await self.bot.pg_utils.get_voice_logging(
            member.guild.id)
        if not vc_logging:
            return
        vc_channels = await self.bot.pg_utils.get_voice_channels(
            member.guild.id
        )
        if before.channel is None and after.channel:
            local_embed = embeds.VoiceChannelStateEmbed(
                member, after.channel, 'joined'
            )
            for channel in vc_channels:
                channel = self.bot.get_channel(channel)
                await channel.send(embed=local_embed)
        elif after.channel is None and before.channel:
            local_embed = embeds.VoiceChannelStateEmbed(
                member, before.channel, 'left'
            )
            for channel in vc_channels:
                channel = self.bot.get_channel(channel)
                await channel.send(embed=local_embed)
        elif before.channel != after.channel:
            local_embed = embeds.VoiceChannelMoveEmbed(
                member, before.channel, after.channel
            )
            for channel in vc_channels:
                channel = self.bot.get_channel(channel)
                await channel.send(embed=local_embed)


    async def on_voice_state_update(self, member, before, after):
        """
        Checks if a user has recently joined or left a voice channel and adds
        role if necessary
        """
        if not await checks.is_channel_blacklisted(self, ctx):
            return
        vc_enabled = await self.bot.pg_utils.get_voice_enabled(
            member.guild.id)
        if not vc_enabled:
            return
        users_roles = member.roles.copy()
        if before.channel is None and after.channel:
            vc_roles = await self.bot.pg_utils.get_channel_roles(
                member.guild.id, after.channel.id
            )
            for vc_role in vc_roles:
                found_role = None
                for role in member.guild.roles:
                    if role.id == vc_role:
                        found_role = role
                if not found_role:
                    self.logger.warning(
                        f'Couldn\'t find {vc_role} in guild {member.guild.id}')
                    continue
                users_roles.append(found_role)
            await member.edit(roles=set(users_roles))
        elif after.channel is None and before.channel:
            vc_roles = await self.bot.pg_utils.get_channel_roles(
                member.guild.id, before.channel.id
            )
            for vc_role in vc_roles:
                for role in users_roles:
                    if role.id == vc_role:
                        try:
                            users_roles.remove(role)
                        except ValueError as e:
                            self.logger.warning(
                                f'{vc_role} not found in {users_roles}')
            await member.edit(roles=set(users_roles))
        else:
            vc_roles = await self.bot.pg_utils.get_server_roles(
                member.guild.id
            )
            for vc_role in vc_roles:
                for role in users_roles:
                    if role.id == vc_role:
                        try:
                            users_roles.remove(role)
                        except ValueError as e:
                            self.logger.warning(
                                f'{vc_role} not found in {users_roles}')
            vc_roles = await self.bot.pg_utils.get_channel_roles(
                member.guild.id, after.channel.id
            )
            for vc_role in vc_roles:
                found_role = None
                for role in member.guild.roles:
                    if role.id == vc_role:
                        found_role = role
                if not found_role:
                    self.logger.warning(
                        f'Couldn\'t find {vc_role} in guild {member.guild.id}')
                    continue
                users_roles.append(found_role)
            await member.edit(roles=set(users_roles))


if __name__ == "__main__":
    """Directly Called."""

    print('Testing module')
    test()
    print('Test Passed')

# end of code

# end of file
