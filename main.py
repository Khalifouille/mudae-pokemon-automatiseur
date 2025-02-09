import requests
import json
import re
import time
from datetime import datetime, timedelta

id_canal = "1084908479745114212"
url_envoi_message = f"https://discord.com/api/v9/channels/{id_canal}/messages"
url_recup_message = f"https://discord.com/api/v9/channels/{id_canal}/messages?limit=1"

entetes = {
    "accept": "*/*",
    "accept-language": "fr,fr-CH;q=0.9",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9181 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36"
}

donnees = {
    "content": "$p",  
    "tts": False
}

def envoyer_message():
    reponse_envoi = requests.post(url_envoi_message, headers=entetes, data=json.dumps(donnees))

    if reponse_envoi.status_code == 200:
        print("Message envoyé avec succès !")

        reponse_recup = requests.get(url_recup_message, headers=entetes)
        
        if reponse_recup.status_code == 200:
            dernier_message = reponse_recup.json()[0]
            print("--------------------")
            print(f"Contenu: {dernier_message['content']}")
            id_envoyeur = dernier_message['author']['id']
            print(f"Envoyeur : {id_envoyeur}")
            
            if id_envoyeur == "432610292342587392":
                correspondance = re.search(r"(\d+) min", dernier_message['content'].replace("**", ""))
                if correspondance:
                    temps_restant = int(correspondance.group(1))
                    print(f"Temps restant avant le prochain message: {temps_restant} minutes")
                    attendre_temps_restant(temps_restant)
                else:
                    print("Temps restant non trouvé dans le message.")
            else:
                print(f"L'envoyeur n'est pas correct (ID: {id_envoyeur}).")
        else:
            print(f"Erreur lors de la récupération du message : {reponse_recup.status_code}")
    else:
        print(f"Erreur lors de l'envoi du message : {reponse_envoi.status_code}")
        print(reponse_envoi.text)

def attendre_temps_restant(temps_restant):
    print(f"Attente pendant {temps_restant} minutes...")
    time.sleep(temps_restant * 60)
    print("Temps écoulé, envoi du message.")
    envoyer_message()

def envoyer_messages_reguliers():
    while True:
        heure_actuelle = datetime.now()

        if heure_actuelle.hour % 2 == 1 or heure_actuelle.minute == 0:
            envoyer_message()
        
        temps_attente = (60 - heure_actuelle.minute) * 60
        print(f"Attente jusqu'à la prochaine heure ({temps_attente} secondes)...")
        time.sleep(temps_attente)

envoyer_message()
envoyer_messages_reguliers()
