from tinydb import TinyDB, Query
from flask_bcrypt import Bcrypt
import os
import random
import string

from base64 import b64encode

userdb = TinyDB("dbs/users.json")

bcrypt = Bcrypt()

namechars = string.ascii_letters + string.digits
namelen = 20
pwdlen = 16


class User(dict):
    # Not entirely necessary, but nice to have
    def __init__(self, username, uid):
        self.username = username
        self.password = ""
        self.firstname = ""
        self.secondname = ""
        self.email = ""
        self.initialised = False
        self.uuid = uid

    def asdict(self):
        return {
            "username": self.username,
            "password": self.password,
            "firstname": self.firstname,
            "secondname": self.secondname,
            "email": self.email,
            "initialised": self.initialised,
            "uuid": self.uuid,
        }


def hash_password(password):
    # Hash the password, and return the hash
    hashed = bcrypt.generate_password_hash(password.encode("utf-8"))
    return hashed.decode("utf-8")


def user_is_initialised(username):
    # Check if a username is attached to an initialised (i.e. password+email)
    # account
    return userdb.search(Query().username == username)[0]["initialised"]


def add_data(username, email, password):
    # Add a password and email to a registered username
    id = userdb.update(
        {"email": email, "password": hash_password(password), "initialised": True},
        Query().username == username,
    )
    user = userdb.get(doc_id=id[0])
    return user 

def find_user(uid):
    # Given a uid, find the username that corresponds to this
    return userdb.search(Query().uuid == uid)[0]


def generate_user(uid):
    # Generate a username, no password or email, and put into database (uninitialised)
    search_user = userdb.search(Query().uuid == uid)
    if len(search_user)>0:
        return search_user[0]
    uname = "doorbell_" + "".join(random.choice(namechars) for _ in range(namelen))
    UserQuery = Query()
    while userdb.search(UserQuery.username == uname):
        uname = "doorbell_" + "".join(random.choice(namechars) for _ in range(namelen))
    user = User(uname, uid)
    userdb.insert(user.asdict())
    return user.asdict()


def update_name(username, firstname, secondname=""):
    # Update the first and/or second names for a given username
    userdb.update(
        {firstname: firstname, secondname: secondname}, Query().username == username
    )

def uuid_exists(uuid):
    # Check if a uuid exists in the db
    return len(userdb.search(Query().uuid == uuid)) > 0

def user_exists(username):
    # Check if a username exists in the db
    return len(userdb.search(Query().username == username)) > 0

def get_snapshots(uid):
    # Get a list of snapshot filenames for a uid
    snapshots = []
    folder = f"./user_data/{uid}/snapshot"
    for f in os.listdir(folder):
        with open(folder+"/"+f, "rb") as img:
            enc = b64encode(img.read())
            snapshots.append({"b64":enc, "name":f})
    return snapshots 

def get_recordings(uid):
    # Get a list of recording filenames for a uid
    recordings = []
    folder = f"./user_data/{uid}/recording"
    for f in os.listdir(folder):
        recordings.append({"name":f})
    return recordings 
