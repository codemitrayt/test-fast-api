from pymongo.mongo_client import MongoClient
import certifi # type: ignore
uri = "mongodb://rmmungse:sV0owwnKIdFXg0fc@ac-hno3pf8-shard-00-00.fmjxswa.mongodb.net:27017,ac-hno3pf8-shard-00-01.fmjxswa.mongodb.net:27017,ac-hno3pf8-shard-00-02.fmjxswa.mongodb.net:27017/?ssl=true&replicaSet=atlas-f0nbrf-shard-0&authSource=admin&retryWrites=true&w=majority&appName=fudo"

client = MongoClient(uri, ssl_ca_certs=certifi.where())

db = client.todo_db
collection_name = db['todo_collection']
user_collection = db['users']