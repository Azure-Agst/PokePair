import sys
import signal
import discord
import configparser
from discord.ext import commands
from pymongo import MongoClient

#
# Init...
#
print("Starting bot...")
config = configparser.ConfigParser()
config.read('config.ini')
bot = commands.Bot(command_prefix='p!')
client = MongoClient(config['Mongo']['uri'])

#
# Ready event
#
@bot.event
async def on_ready():
    game = discord.Game(config['Discord']['status'])
    await bot.change_presence(status=discord.Status.online, activity=game)
    print("Bot started!")

#
# Ping!
#
@bot.command()
async def ping(ctx):
    await ctx.send('pong')


#
# Raids
#
@bot.command()
async def group(ctx, cmd, *, arg):
    raids = client['pokepair']['raids']
    
    # handle raid creation
    if cmd == "create":
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Creating raid group \"{}\"!".format(arg))
        elif isinstance(ctx.channel, discord.GroupChannel):
            await ctx.send("Creating raid group \"{}\"! Check your DMs for more info!".format(arg))
        await create_group(ctx.author, arg)

    elif cmd == "wow":
        await ctx.send("Amazing!")

    else:
        await ctx.send("Command {} not found! Check your syntax and try again!".format(cmd))

async def create_group(user, arg):
    # make embed
    embed = discord.Embed(
        title = "PokePair - {}".format(arg),
        color = discord.Color.blue()
    )
    embed.set_footer(text="PokePair", icon_url="https://cdn.discordapp.com/avatars/645769421486424103/77b0befead90b9ec147304f312514f21.png?size=256")
    embed.add_field(name="Members:", value="• {}\n• {}\n• {}\n• {}".format(user.display_name,"N/A","N/A","N/A"))
    await user.send(embed=embed)
    await user.send("We made a channel for you in azure's server for you to pair up with other people!")

@group.error
async def group_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Seems a few arguments are missing! Check your syntax and try again!')

#
# Wrapping things up...
#
def exit(signal, frame):
    print("Shutting down server...")
    sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit)
    bot.run(config['Discord']['token'])

# https://discordapp.com/api/oauth2/authorize?client_id=645769421486424103&permissions=1547037905&scope=bot