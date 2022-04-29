import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

cluster = MongoClient(os.getenv("DATABASE"))
database = cluster["giveaways"]["giveaways"]

database.delete_many({})