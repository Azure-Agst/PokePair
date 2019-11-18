import pymongo

class DB_Conn():
    def __init__(self):
        self.dbcon = None

    def connect(self):
        try:
            self.dbcon = pymongo.MongoClient(config['Mongo']['uri'], serverSelectionTimeoutMS=5000)
            self.dbcon.server_info()
            print('Connected to DB!')
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print(err)
            sys.exit()

def setup(bot):
    bot.add_cog(Groups(bot))