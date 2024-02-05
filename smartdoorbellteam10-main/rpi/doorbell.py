import serial
import time
import logging as log
import os
from picamera import PiCamera, Color
from datetime import datetime as dt
import threading

from util import timestamp, upload_file

log.basicConfig(level=log.WARNING, format="[%(asctime)s] %(levelname)s : %(message)s ", datefmt="%H:%M:%S")

# Base settings
LOOP_DELAY = 0.1
CLOSE_DISTANCE = 300
DEVICE_NAME = "ttyACM0"
TIME_INACTIVE = 5
MAX_LENGTH = 90

# Live feed settings
HIGH_FRAMERATE = 5
LOW_FRAMERATE = 0.5
LIVE_QUALITY = 5
delay = 1/LOW_FRAMERATE


def liveview_capture(cam):
    # The live feed capture loop
    # This runs on a separate thread
    while True:
        time.sleep(delay)
        filename=f"live/live_{timestamp()}.jpg"
        cam.capture(filename, use_video_port = True, quality=LIVE_QUALITY)
        log.debug("Live feed captured snapshot.")
        upload_file(filename)

def loop(conn, cam):
    global delay
    last_frame_with_activity = 0 # Initialise last active frame to 0
    filename = "" # Hold file name
    snapshotter = threading.Thread(target=liveview_capture, args=(cam,)) # Start live feed thread
    snapshotter.start()
    while True:
        # Annotate the date/time to video
        cam.annotate_text = dt.now().strftime("%H:%M:%S %D")
        if cam.recording:
            # Check if recording duration is above maximum 
            record_dur = cam.frame.index / int(cam.framerate)
            if record_dur > MAX_LENGTH:
                log.info(f"Hit maximum single-file recording duration, stopping.")
                cam.stop_recording()
                continue
            log.debug(f"Recorded {record_dur:.2f}s of video so far")
            cam.wait_recording(LOOP_DELAY)
        else:
            # Camera isn't recording, so just loop
            time.sleep(LOOP_DELAY)
        raw_data = conn.readline() # Raw bytes read from serial
        decoded_data = bytes.decode(raw_data) # Decoded bytes (utf-8)
        conn.flushInput() # Flush connection
        data = "".join(ch for ch in decoded_data if ch.isdigit()) # Filter non-numbers from data
        if len(data) != 4: # Invalid packet
            log.error(f"Received an invalid serial line of length {len(data)}, skipping. (Raw bytes: {raw_data}).")
            continue # Skip to next loop
        dist = int(data[0:3])  # First 3 bytes are the distance
        btnState = int(data[3]) == 0 # Last byte is the button state (default high)
        log.debug(f"Distance:{dist} BtnState:{btnState}")
        if dist < CLOSE_DISTANCE:
            # Object is detected within distance range
            # Restart the snapshotting thread, with a higher framerate
            delay = 1/HIGH_FRAMERATE
            if not cam.recording:
                # Start recording
                filename = f"recordings/recording_{timestamp()}.h264"
                log.info(f"Close object detected, starting recording to {filename}.")
                cam.start_recording(filename)
            elif btnState:
                # The button has been pressed, while we are recording, and
                # an object is still close
                # Stop recording, discard video, take a snapshot, and notify
                record_dur = cam.frame.index / int(cam.framerate)
                log.info(f"Button pressed while recording, deleting {record_dur:.2f}s of video. Saving snapshot.")
                cam.stop_recording()
                snapname=f"snapshots/snapshot_{timestamp()}.jpg"
                cam.capture(snapname,resize=(640,480) , quality=50)
                os.remove(filename)
                upload_file(snapname)
            else:
                # Currently recording, update last active frame
                last_frame_with_activity = cam.frame.index
        else:
            # No object detected within range
            # Adjust snapshotting rate
            delay = 1/LOW_FRAMERATE
            if cam.recording:
                # Currently recording, so check how long we've been recording, and stop if necessary
                record_dur = cam.frame.index / int(cam.framerate)
                time_since_active = (cam.frame.index - last_frame_with_activity)/int(cam.framerate)
                if time_since_active >= TIME_INACTIVE:
                    # We've recorded for the correct length of time
                    log.info(
                            f"Reached max recording duration without seeing an object, stopping recording."
                            )
                    cam.stop_recording()
                    upload_file(filename)
                elif btnState:
                    log.info(f"Button pressed while recording, deleting {record_dur:.2f}s of video. Saving snapshot.")
                    cam.stop_recording()
                    snapname = "snapshots/snapshot_{timestamp()}.jpg"
                    cam.capture(snapname, quality=50)
                    upload_file(snapname)
                    os.remove(filename)

def main():
    camera = PiCamera(resolution=(640,480))
    camera.annotate_background = Color("black")
    try:
        log.info(f"Attempting to connect to serial interface on '/dev/{DEVICE_NAME}'..")
        # Open serial connection
        serial_connection = serial.Serial("/dev/" + DEVICE_NAME)
        log.info(f"Connected to serial interface.")
        log.debug(f"Opening loop thread.")
        loopthread = threading.Thread(target=loop, args=(serial_connection, camera))
        loopthread.start()
    except serial.SerialException as err:
        log.critical(f"Failed to connect to Serial Port : {err}")
        exit()


if __name__ == "__main__":
    main()
