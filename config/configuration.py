import os
import dotenv
from pymongo import MongoClient

dotenv.load_dotenv()

DBURL = os.getenv("URL")

if not(DBURL):
    raise ValueError("Por favor, especifica una URL")

client = MongoClient(DBURL)
db = client.get_database()
messages_coll = db["messages"]
char_coll = db["characters"]
group_coll = db["chats"]

