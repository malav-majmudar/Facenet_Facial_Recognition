import re
import os
from firebase_admin import initialize_app, credentials, firestore
regex_pattern = r"https:\/\/(.*?)\.com"
tunnel_url = ""


with open('output.txt', 'r') as f:
    lines = f.readlines()

    for line in lines:
        match = re.search(regex_pattern, line)

        if match:
            tunnel_url = match.group()
            break


f.close()


initialize_app(credentials.Certificate("key.json"))
db = firestore.client()

db.collection('stream').document('stream_link').set({'value': tunnel_url})
os.environ["CLOUDFLARE_URL"] = tunnel_url

print(tunnel_url)