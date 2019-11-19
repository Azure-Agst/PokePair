import sys
import signal
import discord
import configparser
from discord.ext import commands
from datetime import datetime
from aiohttp.client_exceptions import ClientConnectorError
from plugins.db import DB_Conn

# Load config.ini
config = configparser.ConfigParser()
config.read('config.ini')
plugins = config['Discord']['plugins'].split(",")


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

        # for database
        self.db = None

        # channels
        self.channels = {
            'bot_test': None
        }

    def load_plugins(self):
        for plugin in plugins:
            try:
                self.load_extension(plugin)
            except BaseException as e:
                # print(f'{plugin} failed to load')
                self.failed_plugins.append([plugin, type(e).__name__, e])

    async def on_ready(self):
        # Check for only one server
        self.guild = self.get_guild(int(config['Discord']['serverid']))

        # get all channels specified in constructor
        for n in self.channels.keys():
            self.channels[n] = discord.utils.get(self.guild.channels, name=n)
            if not self.channels[n]:
                print(f'Failed to find channel {n}')

        # Initialize database
        self.db = DB_Conn(config['Mongo']['uri'])
        await self.db.connect()

        # load plugins
        self.load_plugins()

        # Set status
        game = discord.Game(config['Discord']['status'])
        await self.change_presence(status=discord.Status.online, activity=game)

        # start startup message
        startup_message = f'{self.user.name} has started! {self.guild} has {self.guild.member_count:,} members!'

        # check for failed plugins
        if len(self.failed_plugins) != 0:
            startup_message += "\n\nSome addons failed to load:"
            for f in self.failed_plugins:
                startup_message += "\n- *{}*: `{}: {}`".format(*f)
            startup_message += "\n"

        # send startup message
        print(startup_message)
        await self.channels['bot_test'].send(startup_message)


def main():
    """Main function to run the bot"""
    bot = PokePair('!', description="PokePair, the bot for the Pokemon SwSh LFG server!")
    print("Loading PokePair...")

    try:
        bot.run(config['Discord']['token'])
    except ClientConnectorError:
        print("GetAddrInfo failed. Try launching again. :/")
        sys.exit()

    return bot.exitcode


def exit_bot(signal, frame):
    print("Shutting down bot...")
    sys.exit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_bot)
    exit(main())

# db.searchArrayDemo.find({EmployeeDetails:{$elemMatch:{EmployeePerformanceArea : "C++", Year : 1998}}}).pretty();
