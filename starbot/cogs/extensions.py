
class Extension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.command()
    @permissions.is_master()
    async def extension(self, ctx, action, toy_extension):
        print(ctx.message.content + " - " + ctx.author.name + "#" + ctx.author.discriminator + " - " + ctx.guild.name)
        print(self.bot.extensions.items())
        # Loading Extension
        if action == "load":
            try:
                self.bot.load_extension(toy_extension)
                print("Loaded extension {}.".format(toy_extension))
                self.bot.ext_config['loaded_extensions'].append(toy_extension)
                await ctx.send("Loaded extension {} successfully!".format(toy_extension))
            except Exception as errorload:
                print("Failed to load extension {}. [{}]".format(toy_extension, errorload))
                await ctx.send("Failed to load extension {}.".format(toy_extension))
        # Unload Extension
        elif action == "unload":
            try:
                self.bot.unload_extension(toy_extension)
                await ctx.send("Unloaded extension {} successfully!".format(toy_extension))
                self.bot.ext_config['loaded_extensions'].remove(toy_extension)
                print("Unloaded extension {}.".format(toy_extension))
            except Exception as errorunload:
                print("Failed to unload extension {}. [{}]".format(toy_extension, errorunload))
                await ctx.send("Failed to unload extension {}.".format(toy_extension))
        # Reload ALL Loaded Extensions
        elif action == "reload" and toy_extension == "*":
            try:
                for reextension in loaded_extensions:
                    self.bot.unload_extension(reextension)
                    self.bot.ext_config['loaded_extensions'].remove(reextension)
                    self.bot.load_extension(reextension)
                    self.bot.ext_config['loaded_extensions'].append(reextension)
                    print("Reloaded extension {}!".format(reextension))

                print("Successfully reloaded all extensions!")
                await ctx.send("Successfully reloaded all extensions!")
            except Exception as err2:
                print("Failed to reload all extensions! [{}]".format(err2))
                await ctx.send("Failed to reload all extensions!")
        # Reload Extension
        elif action == "reload":
            try:
                self.bot.unload_extension(toy_extension)
                self.bot.ext_config['loaded_extensions'].remove(toy_extension)
                self.bot.load_extension(toy_extension)
                self.bot.ext_config['loaded_extensions'].append(toy_extension)
                print("Reloaded extension {} successfully!".format(toy_extension))
                await ctx.send("Reloaded extension {}!".format(toy_extension))
            except Exception as errorreload:
                print("Failed to reload extension {}. [{}]".format(toy_extension, errorreload))
                await ctx.send("Failed to reload extension {}.".format(toy_extension))
        else:
            await ctx.send("Unknown action!")
