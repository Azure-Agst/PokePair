import random
import discord
from discord.ext import commands
from datetime import datetime

class Groups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(f'Cog "{self.qualified_name}" loaded')

    @commands.command()
    async def group(self, ctx, cmd, *, arg):    
        if isinstance(ctx.channel, discord.DMChannel):
                await ctx.send("We currently don't support making groups in DMs. Hop into a server and try again!")
        else:

            # handle raid creation
            if cmd == "create":
                await ctx.send("Creating raid group \"{}\"! Check your DMs for more info!".format(arg))
                await create_group(ctx, arg)

            elif cmd == "wow":
                await ctx.send("Amazing!")

            else:
                await ctx.send("Command {} not found! Check your syntax and try again!".format(cmd))

    @group.error
    async def group_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Seems a few arguments are missing! Check your syntax and try again!')

    #
    # Main Create Group Function
    #
    async def create_group(self, ctx, arg):
        # make entry in database for group
        raids_db = client['pokepair']['groups']
        id = raids_db.insert_one({
            "name": arg,
            "code": random.randrange(1000, 9999),
            "members": [
                { 
                    "name": ctx.author.display_name,
                    "id": ctx.author.id
                }
            ],
            "timestamp": datetime.now()
        }).inserted_id
        result = raids_db.find_one({"_id": id})
        if not result:
            print("Error making group: {}".format(arg))
            await ctx.author.send("Something went terribly wrong! Try again in a second!")

        # make embed
        embed = discord.Embed(
            title = "PokePair - {}".format(result['name']),
            description = "Made at: {}".format(result['timestamp']),
            color = discord.Color.blue()
        )
        embed.set_footer(text="PokePair", icon_url="https://cdn.discordapp.com/avatars/645769421486424103/77b0befead90b9ec147304f312514f21.png?size=256")
        embed.add_field(name="Code:", value=result['code'])
        embed.add_field(name="Members:", value="• {}\n• {}\n• {}\n• {}".format(result['members'][0]['name'],"N/A","N/A","N/A"))
        await ctx.author.send(embed=embed)
        await ctx.author.send("We made a channel for you in {} for you to pair up with other people!".format(ctx.guild))

def setup(bot):
    bot.add_cog(Groups(bot))