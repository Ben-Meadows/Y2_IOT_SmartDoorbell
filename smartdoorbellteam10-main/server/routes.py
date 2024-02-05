from bottle import (
    route,
    get,
    post,
    static_file,
    request,
    template,
    response,
    TEMPLATE_PATH,
    redirect,
)
import db
from datetime import datetime
from os import path, listdir, remove, makedirs
import auth
from base64 import b64encode
import os
import emailsender
import ffmpeg
TEMPLATE_PATH.insert(0, "templates")

dirname = path.abspath(path.dirname(__file__))


@route("/static/<filename>")
def serve_static(filename):
    # Serve static files from the static directory
    return static_file(filename, root=f"{dirname}/static")

@route("/assets/<filename>")
def serve_asset(filename):
    return static_file(filename, root=f"{dirname}/static/assets")

@route("/")  # homepage route
def home():
    session = auth.find_session(request.get_cookie("sessionid")) # Verify the session cookie
    if session["success"]: # User has a valid session
        return template("templates/loggedin.tpl", user=session["user"], snapshots=db.get_snapshots(session["user"]["uuid"]), recordings=db.get_recordings(session["user"]["uuid"]))
    else: # User doesn't have a valid session, or isn't logged in
        return template("templates/login.tpl")


@get("/api/livefeed/latest") # api endpoint for latest livefeed 
def latest():
    session = auth.find_session(request.get_cookie("sessionid")) # Verify session
    if not session["success"]:
        return {"success":False, "message": "Tried to get livefeed without a verified session"}
    uid = session["user"]["uuid"]
    folder = f"./user_data/{uid}/live/" # The local folder where live feed is stored
    liveframes = listdir(folder) # List the frames
    dtformat = "%H%M%S%d%m%y.jpg" # The datetime format string
    if len(liveframes)==0: # There are no frames
        return {"success":False, "message": "No images found for this user"} 
    latest_frame = sorted( # Find the most recent frames by sorting by the timestamp
        liveframes,
        key=lambda frame: datetime.strptime("".join(frame.split("_")[1:]), dtformat),
    )[-1]
    with open(folder + latest_frame, "rb") as image_file:
        encoded_image = b64encode(image_file.read()) # Encode the file as b64
    remove(folder+latest_frame) # Remove the file
    return {"success": True, "message":"Found latest frame for this user", "image": str(encoded_image, "utf-8"),"name":latest_frame}


@get("/logout") # Logout path, remove session cookie and redirect
def logout():
    response.set_cookie("sessionid", "", expires=0)
    return redirect("/")


@post("/newuser") # New user path, for new UUIDs
def new_user():
    uid = request.forms.get("uid", "")
    if uid == "":
        response.status = 400
        return {"success": False, "message": "No id attached to new user request"}
    if db.uuid_exists(uid):
        user = db.find_user(uid)
        return {"success":False,
                "message": "User with this id already exists",
                "username": user.get("username","")
                }
    user = db.generate_user(uid)
    return {
        "success": True,
        "message": "New user registered",
        "username": user.get("username",""),
    }


@post("/login") # Login path for registered users
def login():
    rf = request.forms
    user = rf.get("username", "")
    pwd = rf.get("password", "")
    if not db.user_is_initialised(user):
        response.status = 400
        return {"success": False, "message": "Attempted to login as uninitialised user"}
    elif auth.verify_password(user, pwd):
        response.set_cookie("sessionid", f"{auth.new_session(user)}") 
        return {"success": True, "message": "Logged in"}
    else:
        response.status = 401
        return {"success": False, "message": "Wrong password"}


@post("/username_check") # Checks if the username is attached to an account
def username_check():
    rf = request.forms
    user = rf.get("username", "")
    if user == "":
        # No username in form
        return {"success": False, "message": "Empty username."}
    if db.user_exists(user):
        # The username in the form exists in the database
        if db.user_is_initialised(user):
            # The username is attached to an initialised account
            return {
                "success": True,
                "message": "User already initialised.",
                "initialised": True,
            }
        else:
            # The username is attached to an uninitialised account
            return {
                "success": True,
                "message": "User not initialised.",
                "initialised": False,
            }
    else:
        # The username doesn't exist in the database
        response.status = 404
        return {"success": False, "message": "No user found with this username."}


@post("/initialise_user") # Add a password and email to the user
def init_user():
    rf = request.forms
    username = rf.get("username", "")
    if db.user_is_initialised(username):
        response.status = 409
        return {"success": False, "message": "User already initialised"}
    password = rf.get("password", "")
    email = rf.get("email", "")
    if username == "" or password == "" or email == "":
        return {"success": False, "message": "Empty field."}
    user = db.add_data(username, email, password)
    [ # Add local storage directories for uploads by this user
        makedirs(f"./user_data/{user.get('uuid')}/{_type}", exist_ok=True)
        for _type in ["snapshot", "live", "recording"]
    ]
    return {"success": True, "message": "Initialised user data."}

@get("/api/download/<uid>/<filename>") # Download route
def download_recording(uid, filename):
    session = auth.find_session(request.get_cookie("sessionid")) 
    if not session["success"] or not session["user"]["uuid"]==uid: # Check if the user has a valid session, and that the uuid corresponds to this route
        response.status = 401
        return {"success": False, "message": "Unauthorised attempt to download file"}
    folder = f"{uid}/{filename.split('_')[0]}/"
    filepath = folder+filename
    return static_file(filepath, root="user_data", download=filepath) # Download file

#
# Following three routes are for uploading files, and function the same.
# The user attaches a file, which is uploaded to the relevant directory corresponding
# to the file type and uid of the user. For the snapshot, this is also emailed to the 
# email address. (Not implemented currently due to email sending restrictions).

@post("/api/new_snapshot")
def new_image():
    if not auth.find_session(request.get_cookie("sessionid")):
        response.status = 401
        return {"success": False, "message": "Need to be authorised."}
    uid = request.forms.get("uid", "")
    if uid == "":
        response.status = 409
        return {"success": False, "message": "No uid attached to request."}
    if request.files.get("file", "") == "":
        return {"success": False, "message": "No image attached"}
    request.files.get("file").save(f"./user_data/{uid}/snapshot", overwrite=True)
    dtformat = "%H%M%S%d%m%y.jpg"
    while (len(os.listdir(f"./user_data/{uid}/snapshot")))>20:
        oldest_snap = sorted(
            os.listdir(f"./user_data/{uid}/snapshot"),
            key=lambda snap: datetime.strptime("".join(snap.split("_")[1:]), dtformat),
        )[0]
        #os.remove(f"./user_data{uid}/snapshot/{oldest_snap}")
    emailsender.send_email_image(request.files.get("file").file.read())


@post("/api/new_recording")
def new_recording():
    if not auth.find_session(request.get_cookie("sessionid")):
        response.status = 401
        return {"success": False, "message": "Need to be authorised."}
    uid = request.forms.get("uid", "")
    if uid == "":
        response.status = 409
        return {"success": False, "message": "No uid attached to request."}
    if request.files.get("file", "") == "":
        return {"success": False, "message": "No image attached"}
    dtformat = "%H%M%S%d%m%y.jpg" # The datetime format string
    while (len(os.listdir(f"./user_data/{uid}/recording")))>20:
        oldest_recording = sorted(
            os.listdir(f"./user_data/{uid}/recording"),
            key=lambda recording: datetime.strptime("".join(recording.split("_")[1:]), dtformat),
        )[0]
        os.remove(f"./user_data/{uid}/recording/{oldest_recording}")
    request.files.get("file").save(f"./user_data/{uid}/recording", overwrite=True)
    filename = request.files.get("file").raw_filename
    ffmpeg.input(f"./user_data/{uid}/recording/{filename}").output(f"./user_data/{uid}/recording/{filename[0:-5]}.mp4").run()
    os.remove(f"./user_data/{uid}/recording/{filename}")
    emailsender.send_email_recording(f"http://35.246.105.232/api/download/{uid}/{filename[0:-5]}.mp4")


@post("/api/new_livefeed")
def feed_update():
    if not auth.find_session(request.get_cookie("sessionid")):
        response.status = 401
        return {"success": False, "message": "Need to be authorised."}
    uid = request.forms.get("uid", "")
    if uid == "":
        response.status = 409
        return {"success": False, "message": "No uid attached to request."}
    if request.files.get("file", "") == "":
        return {"success": False, "message": "No image attached"}
    dtformat = "%H%M%S%d%m%y.jpg" # The datetime format string
    while len(os.listdir(f"./user_data/{uid}/live"))>15:
        oldest_frame = sorted(
            os.listdir(f"./user_data/{uid}/live"),
            key=lambda live: datetime.strptime("".join(live.split("_")[1:]), dtformat),
        )[0]
        #os.remove(f"./user_data/{uid}/live/{oldest_frame}")
    request.files.get("file").save(f"./user_data/{uid}/live", overwrite=True)
