import sys
import signal
import random
import discord
import pymongo
import configparser
from discord.ext import commands
from datetime import datetime

#
# Init...
#
print("Starting bot...")
config = configparser.ConfigParser()
config.read('config.ini')
bot = commands.Bot(command_prefix=config['Discord']['prefix'])

#
# Database stuff
#
try:
    client = pymongo.MongoClient(config['Mongo']['uri'], serverSelectionTimeoutMS=5000)
    client.server_info()
    print('Connected to DB!')
except pymongo.errors.ServerSelectionTimeoutError as err:
    print(err)
    sys.exit()

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
# Groups
#
@bot.command()
async def group(ctx, cmd, *, arg):    
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

async def create_group(ctx, arg):
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
# db.searchArrayDemo.find({EmployeeDetails:{$elemMatch:{EmployeePerformanceArea : "C++", Year : 1998}}}).pretty();