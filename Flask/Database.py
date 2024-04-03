import pymongo
from werkzeug.security import generate_password_hash
from pymongo.errors import DuplicateKeyError
import User
import importlib
import pickle
importlib.reload(User)
from User import User
from cryptography.hazmat.primitives.asymmetric import rsa
from EncryptionService import get_public_key

flask_server_ip = "127.0.0.1"

myclient = pymongo.MongoClient("mongodb://localhost:27017")

database = myclient["ChatAppDatabase"]

users = database.get_collection("users")
invites = database.get_collection("invites")

#TODO: code a killswitch function that overwrites all the data in the database with 0's 

def write_user(username, password, browser_fingerprint, current_room=None):
    password_hash = generate_password_hash(password)
   
    try:
        users.insert_one({'_id': username,
                        'password': password_hash,
                        'browser_fingerprint': browser_fingerprint,
                        'current_room': current_room,
                        })
    except DuplicateKeyError:
        print(f"Error: user with username '{username}' already exists")

def write_invite(username, invite_id):
    try:
        invites.insert_one({'_id': username, 
                        'invite_id': invite_id,
                        })
    except DuplicateKeyError:
        print(f"Error: user with username '{username}' already exists")

'''def get_room(username):
    user = users.find_one({'_id': username})
    #user_object = User(user)if user is not None else None
    room = user['current_room']
    return room'''

def set_room(username, room):
    # Update the current_room field for the user
    users.update_one({'_id': username}, {'$set': {'current_room': room}})

def get_user(username):
    user = users.find_one({'_id': username})
    user_object = User(user)if user is not None else None
    return user_object

def get_invite(username):
    invite = invites.find_one({'_id': username})
    return invite

def invite_exists(username):
    invite = invites.find_one({'_id': username})
    return invite if invite else None

def remove_invite(username):
    result = invites.delete_one({'_id': username}) #TODO: make this overwrite the entry with 0's first before deleting it?
    return (True if result.deleted_count == 1 else False)  


def get_user_ids(user):
    all_users = users.find()
    user_ids = []
    for current_user in all_users:
        current_id = current_user['_id']
        if current_id != user.get_id():
            user_ids.append(current_id)
    return user_ids

