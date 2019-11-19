from discord.ext import commands


class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    @commands.command()
    async def ping(self, ctx, *, arg):
        # self - the class object
        # ctx - the context surrounding why this function was called
        # arg - everything after the "!ping"
        ctx.send("Pong!")
