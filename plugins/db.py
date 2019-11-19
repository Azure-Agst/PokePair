import sys
import pymongo
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
        print(f'Plugin "{self.qualified_name}" loaded')

    async def db_create_group(self, ctx, name, ts, g_id, code, tc_id, vc_id, em_id):
        """
        Creates an entry in the database for a group
        """
        id = self.db.insert_one({
            "name": name,
            "group-id": g_id,
            "code": code,
            "members": [
                ctx.author.id
            ],
            "text": tc_id,
            "voice": vc_id,
            "embed-id": em_id,
            "timestamp": ts
        }).inserted_id

        result = self.db.find_one({"_id": id})
        if not result:
            print("Error making group: {}".format(name))
            await ctx.author.send("Something went terribly wrong! Try again in a second!")
        return result

    async def db_find_group_by_chat(self, tc_id):
        """
        Creates an entry in the database for a group
        """
        return self.db.find_one({"text": tc_id})

    async def db_delete_group(self, g_id):
        """
        Deletes an entry in the database for a group
        """
        return self.db.delete_one({"group-id": g_id})
