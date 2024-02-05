from tinydb import TinyDB, Query
from datetime import datetime
from uuid import uuid4
import os

from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
sessiondb = TinyDB("./dbs/sessions.json")
userdb = TinyDB("./dbs/users.json")
SESSION_DURATION = 2630000  # ~1 month


def find_session(sessionid):
    # Given a session id, find the corresponding session, and return the user attached
    query = Query().sessionid == sessionid
    found = sessiondb.search(query)
    if len(found) == 0:
        return {"success": False, "message": "No session found."}
    if int(found[0]["expdate"]) < int(datetime.now().timestamp()):
        sessiondb.remove(query)
        return {"success": False, "message": "Expired session."}
    user = userdb.search(Query().username == found[0]["username"])[0]
    return {"success": True, "message": "Found session.", "user": user}


def verify_password(user, password):
    # Verify if the input password matches the hashed password of the username
    hashed = userdb.search(Query().username == user)[0]["password"].encode("utf-8")
    return bcrypt.check_password_hash(hashed, password.encode("utf-8"))


def new_session(username):
    # Create a new session with a sessionid, username and expdate
    sid = str(uuid4())
    session = {
        "sessionid": sid,
        "username": username,
        "expdate": datetime.now().timestamp() + SESSION_DURATION,
    }
    sessiondb.insert(session)
    return sid
