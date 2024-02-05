import os
import requests
API_KEY = os.environ.get("MAILGUN_API_KEY", "")

def send_email_recording(url):
    domain = "sandboxa5985b8dd80d41b785cea7ea950308a6.mailgun.org"
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", API_KEY),
        data={"from": f"Team 10 Solutions mailgun@{domain}",
        "to": ["thet10solutions@gmail.com"],
        "subject": "Alert: Someone approached your doorbell!",
        "html": f"Your doorbell recorded someone approaching it. <video src='{url}' controls ></video>"
        })

def send_email_image(image):
    domain = "sandboxa5985b8dd80d41b785cea7ea950308a6.mailgun.org"
    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", API_KEY),
        files=[('inline[0]', ('image.png', image))],
        data={"from": f"Team 10 Solutions mailgun@{domain}",
        "to": ["thet10solutions@gmail.com"],
        "subject": "Alert: Someone pushed your smart doorbell buzzer!",
        "html": f"Your doorbell has been rung by this individual<img src='cid:image.png'/>",
        })
