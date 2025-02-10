import requests
import json
import re
import time
import threading
import tkinter as tk
from tkinter import messagebox

running = False

def envoyer_message():
    global running
    headers = {
        "accept": "*/*",
        "authorization": token_entry.get(),
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    channel_id = channel_entry.get()
    url_send_message = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    url_get_message = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"

    data = {"content": "$p", "tts": False}

    response_send = requests.post(url_send_message, headers=headers, data=json.dumps(data))

    if response_send.status_code == 200:
        log_message("[SUCCESS] Message envoyé avec succès !")
        time.sleep(2)
        analyser_reponse(headers, url_get_message)
    else:
        log_message(f"[ERROR] {response_send.status_code}\n{response_send.text}")

def obtenir_dernier_message(headers, url_get_message):
    response_get = requests.get(url_get_message, headers=headers)

    if response_get.status_code == 200:
        last_message = response_get.json()[0]
        return last_message['content'], last_message['author']['id']
    else:
        log_message(f"[ERROR] {response_get.status_code}")
        return None, None

def analyser_reponse(headers, url_get_message):
    global running
    contenu, sender_id = obtenir_dernier_message(headers, url_get_message)

    if not contenu or not sender_id:
        log_message("[ERROR] Impossible de récupérer le dernier message.")
        return

    if sender_id == "432610292342587392":
        if "Temps restant avant votre prochain $p" in contenu:
            temps_attente = extraire_temps(contenu)
            log_message(f"Temps d'attente : {temps_attente} minutes")
            afficher_compte_a_rebours(temps_attente)
        else:
            log_message("[INFO] Pokémon roll détecté, lancement du cycle de 2h.")
            afficher_compte_a_rebours(120)

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
    global running
    while minutes > 0 and running:
        countdown_label.config(text=f"Temps restant : {minutes} min")
        root.update()
        time.sleep(60)
        minutes -= 1
    if running:
        log_message("[INFO] Temps écoulé, envoi du message.")
        envoyer_message()

def log_message(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

def demarrer_bot():
    global running
    if not token_entry.get() or not channel_entry.get():
        messagebox.showerror("Erreur", "Veuillez entrer un token et un Channel ID valide.")
        return
    running = True
    threading.Thread(target=envoyer_message, daemon=True).start()

def arreter_bot():
    global running
    running = False
    log_message("[INFO] Bot arrêté.")

root = tk.Tk()
root.title("Discord Pokémon Bot")
root.geometry("400x400")

tk.Label(root, text="Token Discord :").pack()
token_entry = tk.Entry(root, width=50, show="*")
token_entry.pack()

tk.Label(root, text="Channel ID :").pack()
channel_entry = tk.Entry(root, width=50)
channel_entry.pack()

start_button = tk.Button(root, text="Démarrer", command=demarrer_bot, bg="green", fg="white")
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Arrêter", command=arreter_bot, bg="red", fg="white")
stop_button.pack(pady=5)

countdown_label = tk.Label(root, text="Temps restant : -")
countdown_label.pack()

log_text = tk.Text(root, height=10, width=50)
log_text.pack()

root.mainloop()
