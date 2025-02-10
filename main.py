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
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

data = {
    "content": "$p",
    "tts": False
}

def envoyer_message():
    response_send = requests.post(url_send_message, headers=headers, data=json.dumps(data))

    if response_send.status_code == 200:
        print("\033[92m[SUCCESS] Message envoyé avec succès !\033[0m")
        time.sleep(2)
        analyser_reponse()
    else:
        print(f"\033[91m[ERROR] {response_send.status_code}\033[0m")
        print(response_send.text)

def obtenir_dernier_message():
    response_get = requests.get(url_get_message, headers=headers)

    if response_get.status_code == 200:
        last_message = response_get.json()[0]
        contenu = last_message['content']
        sender_id = last_message['author']['id']
        return contenu, sender_id
    else:
        print(f"\033[91m[ERROR] {response_get.status_code}\033[0m")
        return None, None

def analyser_reponse():
    contenu, sender_id = obtenir_dernier_message()

    if not contenu or not sender_id:
        print("\033[91m[ERROR] Impossible de récupérer le dernier message.\033[0m")
        return

    print("--------------------")
    print(f"Contenu: {contenu}")
    print(f"Envoyeur : {sender_id}")

    if sender_id == "432610292342587392":
        if "Temps restant avant votre prochain $p" in contenu:
            temps_attente = extraire_temps(contenu)
            print(f"Temps restant avant le prochain message: {temps_attente} minutes")
            afficher_compte_a_rebours(temps_attente)
        else:
            print("\033[94m[INFO] Pokémon roll détecté, lancement du cycle de 2h.\033[0m")
            afficher_compte_a_rebours(120)
    else:
        print(f"\033[91m[ERROR] L'envoyeur n'est pas correct (ID: {sender_id}).\033[0m")

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
    print("\n\033[92m[INFO] Temps écoulé, envoi du message.\033[0m")
    envoyer_message()

def demarrer_bot():
    print("[INFO] Vérification du dernier message...")

    dernier_message, envoyeur = obtenir_dernier_message()

    if not dernier_message or not envoyeur:
        print("\033[91m[ERROR] Impossible de récupérer le dernier message. Envoi immédiat.\033[0m")
        envoyer_message()
        return

    if envoyeur != "432610292342587392":
        print(f"\033[91m[ERROR] L'envoyeur n'est pas correct (ID: {envoyeur}).\033[0m")
        return

    if "Temps restant avant votre prochain $p" in dernier_message:
        temps_attente = extraire_temps(dernier_message)
        print(f"[INFO] Mudae indique une attente de {temps_attente} minutes.")
        afficher_compte_a_rebours(temps_attente)
    else:
        print("[INFO] Aucun délai détecté, lancement du cycle de 2h.")
        afficher_compte_a_rebours(120)

demarrer_bot()
