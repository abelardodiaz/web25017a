import requests, os, json
r = requests.post(
    "https://developers.syscom.mx/oauth/token",
    headers={'Content-Type': 'application/json'},
    json={
        "client_id": "ciDckpXpicKUAmwwBSEwCz1GTffdRGdV",
        "client_secret": "TeeJrGgqujzkBvlXsZOPRXWr9VKSk8OSl14AF0qY",
        "grant_type": "client_credentials",
    },
    timeout=15
)
print(r.status_code, r.text[:1200])