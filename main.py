import requests
import json
import re
import time
import sys
from datetime import datetime, timedelta

channel_id = "1084908479745114212"
url_send_message = f"https://discord.com/api/v9/channels/{channel_id}/messages"
url_get_message = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"

headers = {
    "accept": "*/*",
    "accept-language": "fr,fr-CH;q=0.9",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9181 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36"
}

data = {"content": "$p", "tts": False}

def envoyer_message():
    response_send = requests.post(url_send_message, headers=headers, data=json.dumps(data))
    
    if response_send.status_code == 200:
        print("\033[92m[SUCCESS] Message envoyé avec succès !\033[0m")
        return datetime.now()
    else:
        print(f"\033[91m[ERROR] {response_send.status_code}\033[0m")
        print(response_send.text)
        return None

def afficher_compte_a_rebours(minutes):
    while minutes > 0:
        sys.stdout.write(f"\r\033[92m[INFO] Temps restant : {minutes} min\033[0m")
        sys.stdout.flush()
        time.sleep(60)
        minutes -= 1
    print("\n\033[92m[INFO] Temps écoulé.\033[0m")

def boucle_principale():
    prochain_envoi = envoyer_message()
    if not prochain_envoi:
        return
    prochain_envoi += timedelta(hours=2)

    while True:
        heure_actuelle = datetime.now()
        
        if heure_actuelle.hour % 2 == 1 and heure_actuelle.minute == 0:
            envoyer_message()
        
        if heure_actuelle >= prochain_envoi:
            prochain_envoi = envoyer_message()
            if prochain_envoi:
                prochain_envoi += timedelta(hours=2)
        
        time.sleep(60)

boucle_principale()