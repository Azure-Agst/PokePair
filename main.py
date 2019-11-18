import os
import sys
import signal
import random
import discord
import pymongo
import configparser
from discord.ext import commands
from datetime import datetime
from aiohttp.client_exceptions import ClientConnectorError

# Load config.ini
config = configparser.ConfigParser()
config.read('config.ini')
bot = commands.Bot(command_prefix=config['Discord']['prefix'])

# plugins
plugins = [
    #"plugins.database",
    #"plugins.admin",
    "plugins.groups"
]

class PokePair(commands.Bot):
    """Main Bot Class"""
    def __init__(self, command_prefix, description):

        # init parent class
        super().__init__(command_prefix=command_prefix, description=description)

        # startup time
        self.startup = datetime.now()

        # for failed plugins
        self.failed_plugins = []
        self.exitcode = 0

        # channels
        self.channels = {
            'bot-test': None
        }

    def load_plugins(self):
        for plugin in plugins:
            try:
                self.load_extension(plugin)
            except BaseException as e:
                #print(f'{plugin} failed to load')
                self.failed_plugins.append([plugin, type(e).__name__, e])

    async def on_ready(self):
        # Check for only one server
        self.guild = self.get_guild(int(config['Discord']['serverid']))

        # get all channels specified in constructor
        for n in self.channels.keys():
            self.channels[n] = discord.utils.get(self.guild.channels, name=n)
            if not self.channels[n]:
                print(f'Failed to find channel {n}')

        # Set status
        game = discord.Game(config['Discord']['status'])
        await self.change_presence(status=discord.Status.online, activity=game)

        # start startup message
        startup_message = f'{self.user.name} has started! {self.guild} has {self.guild.member_count:,} members!'

        # check for failed plugins
        if len(self.failed_plugins) != 0:
            startup_message += "\n\nSome addons failed to load:"
            for f in self.failed_plugins:
                startup_message += "\n{}: `{}: {}`".format(*f)
            startup_message += "\n\n"

        # send startup message
        print(startup_message)
        await self.channels['bot-test'].send(startup_message)



def main():
    """Main function to run the bot"""
    bot = PokePair('!', description="Kurisu, the bot for Nintendo Homebrew!")
    print("Loading PokePair...")
    bot.load_plugins()

    try:
        bot.run(config['Discord']['token'])
    except ClientConnectorError as e:
        print("GetAddrInfo failed. Try launching again. :/")

    return bot.exitcode

#
# Wrapping things up...
#
def exit(signal, frame):
    print("Shutting down bot...")
    sys.exit()
if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit)
    exit(main())
    

# db.searchArrayDemo.find({EmployeeDetails:{$elemMatch:{EmployeePerformanceArea : "C++", Year : 1998}}}).pretty();