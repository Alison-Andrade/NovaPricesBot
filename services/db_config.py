import pymongo
import os
from dotenv import load_dotenv

load_dotenv('.env')
MONGODB_URL = os.getenv('MONGODB_URL')

client = pymongo.MongoClient(MONGODB_URL)
db = client.get_database()
