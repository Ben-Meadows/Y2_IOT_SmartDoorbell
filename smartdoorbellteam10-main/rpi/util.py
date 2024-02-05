from datetime import datetime as dt

import logging as log
import requests
import urllib
import os

log.getLogger("requests").setLevel(log.WARNING)
def timestamp():
    # Simple timestamp, returning the hour minute second followed by day month year
    return dt.now().strftime("%H%M%S_%d%m%y")

def upload_file(filepath):
    # Given a filepath and url (subpath) to upload to, upload the file to the
    # base url + subpath, using the local identifier
    base_url = "http://35.246.105.232/api/"
    filename = os.path.basename(filepath)
    _id = os.environ.get("DOORBELL_ID", "")
    if "snapshot" in filename:
        # We are uploading a snapshot
        url_ext = "new_snapshot"
    elif "live" in filename:
        # We are uploading a live feed capture
        url_ext = "new_livefeed"
    elif "recording" in filename:
        # We are uploading a video recording
        url_ext = "new_recording"
    else:
        log.error(f"Couldn't parse an update type out of {filename}. Skipping.")
        return
    url_full = urllib.parse.urljoin(base_url, url_ext)
    log.debug(f"Attempting to upload '{filepath}' to '{url_full}'. Using private ID {_id}.")
    try:
        res = requests.post(url_full, data={"uid":_id}, files={"file": open(filepath, 'rb')})
        if res.status_code == 200:
            # Succesful upload, remove file
            log.debug(f"Successfully uploaded file. Deleting file.")
            os.remove(filepath)
        else:
            # Failed to upload, don't remove file
            log.warn(f"Failed to upload file.")
    except requests.exceptions.RequestException:
        # An exception during requests POST request, rather than an HTTP code error
        log.error(f"Encountered error while trying to upload.")



