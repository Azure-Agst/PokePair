import sys
import random
import pymongo
from datetime import datetime
from discord.ext import commands

class DB_Conn():
    """
    Initializes the database connector for the bot
    """
    def __init__(self, uri):
        self.uri = uri
        self._dbcon = None
        self.data = None

    async def connect(self):
        """
        Connects the DB_Conn object to the database
        """
        try:
            self._dbcon = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self._dbcon.server_info()
            print('Connected to DB!') 
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print(err)
            sys.exit()
        self.data = self._dbcon['pokepair']['groups']

class DB_Plugin(commands.Cog):
    """
    Base class for plugins that interact with the database
    """
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db.data
        print(self.bot.db)
        print(f'Cog "{self.qualified_name}" loaded')

    async def db_create_group(self, ctx, name):
        """
        Creates an entry in the database for a group
        """
        id = self.db.insert_one({
            "name": name,
            "code": random.randrange(1000, 9999),
            "members": [
                { 
                    "name": ctx.author.display_name,
                    "id": ctx.author.id
                }
            ],
            "timestamp": datetime.now()
        }).inserted_id

        result = self.db.find_one({"_id": id})
        if not result:
            print("Error making group: {}".format(name))
            await ctx.author.send("Something went terribly wrong! Try again in a second!")
        return result
    