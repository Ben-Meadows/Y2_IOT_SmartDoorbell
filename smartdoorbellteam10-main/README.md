# SmartDoorBellTeam10

## Description
A smart doorbell which records photos and video depending on the conditions it is presented
 - If the button is pressed a photo is taken
 - If someone approaches and leaves then a video is taken

## Required Python Libraries
For the Flask server:
 - `flask`
 - `flask-bcrypt`
 - `bottle`
 - `ffmpeg` (and a corresponding ffmpeg install)
 - `tinydb`

 For the Raspberry Pi & Arduino hardware:
 * `picamera`
 * `serial`
 * `requests`

## Function

### Server

The server is run via the `flask run` command, after sourcing the relevant virtual environment `source .venv/bin/activat`,
or installing dependencies. The server is run by default on port 8081, but this can be changed in `app.py`. User accounts
and sessions are stored in `dbs/users.json` and `dbs/sessions.json` respectively, and can be modified directly. User data,
i.e. videos and images, are stored in folders under the `user_data/<uid>` folder, according to their respective uid.

### Hardware

The Arduino script, `doorbell.ino`, can be compiled and uploaded to the Arduino. The name of the Arduino device is assumed to be
`ttyACM0`, but this can be modified in `doorbell.py`, along with other variables, at the top of the script. To run the application,
simply source the virtual environment as above, or install dependencies, and run `python3 doorbell.py`. The level of logging can be
modified in the top of the script, also. The application requires an environment variable `DOORBELL_ID` to be set to the UUID4 
corresponding to the device.
