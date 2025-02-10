import requests
import json
import re
import time
import sys
from datetime import datetime

channel_id = "1084908479745114212"
url_send_message = f"https://discord.com/api/v9/channels/{channel_id}/messages"
url_get_message = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"

headers = {
    "accept": "*/*",
    "accept-language": "fr,fr-CH;q=0.9",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9181 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36"
}

data = {
    "content": "$p",  
    "tts": False
}

def envoyer_message():
    response_send = requests.post(url_send_message, headers=headers, data=json.dumps(data))

    if response_send.status_code == 200:
        print("\033[92m[SUCCESS] Message envoyé avec succès !\033[0m")

        response_get = requests.get(url_get_message, headers=headers)

        time.sleep(1)
        
        if response_get.status_code == 200:
            last_message = response_get.json()[0]
            print("--------------------")
            print(f"Contenu: {last_message['content']}")
            sender_id = last_message['author']['id']
            print(f"Envoyeur : {sender_id}")
            
            if sender_id == "432610292342587392":
                temps_attente = extraire_temps(last_message['content'])
                
                print(f"Temps restant avant le prochain message: {temps_attente} minutes")

                if temps_attente > 0:
                    afficher_compte_a_rebours(temps_attente)
                
                boucle_principale()
            else:
                print(f"\033[91m[ERROR] L'envoyeur n'est pas correct (ID: {sender_id}).\033[0m")
        else:
            print(f"\033[91m[ERROR] {response_get.status_code}\033[0m")
    else:
        print(f"\033[91m[ERROR] {response_send.status_code}\033[0m")
        print(response_send.text)

def extraire_temps(message):
    match = re.search(r"(\d+)h(?: (\d+) min)?", message.replace("**", ""))
    minutes_match = re.search(r"(\d+) min", message.replace("**", ""))

    if match:
        heures = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return (heures * 60) + minutes
    elif minutes_match:
        return int(minutes_match.group(1))
    return 0

def afficher_compte_a_rebours(minutes):
    while minutes > 0:
        sys.stdout.write(f"\r\033[92m[INFO] Temps restant : {minutes} min\033[0m")
        sys.stdout.flush()
        time.sleep(60)
        minutes -= 1
    print("\n\033[92m[INFO] Temps écoulé.\033[0m")

def boucle_principale():
    while True:
        heure_actuelle = datetime.now()

        if heure_actuelle.hour % 2 == 1 and heure_actuelle.minute == 0:
            envoyer_message()

        print("Attente de 2 heures avant le prochain message...")
        afficher_compte_a_rebours(120)
        envoyer_message()  

envoyer_message()
