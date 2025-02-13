import requests
import json
import re
import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar  
import webbrowser
import os
import pygame

running = False
test_mode = False  

APPDATA_DIR = os.path.join(os.getenv("APPDATA"), "MudaeBot")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")
LOG_FILE = os.path.join(APPDATA_DIR, "log.txt")  
ICON_PATH = "mudae.ico"
SOUND_PATH = "music.mp3"

if not os.path.exists(APPDATA_DIR):
    os.makedirs(APPDATA_DIR)

pygame.mixer.init()

def sauvegarder_config():
    config = {
        "token": token_entry.get(),
        "channel_id": channel_entry.get(),
        "test_mode": test_mode  
    }
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)
    log_message("[INFO] Paramètres sauvegardés.")

def charger_config():
    global test_mode
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            token_entry.insert(0, config.get("token", ""))
            channel_entry.insert(0, config.get("channel_id", ""))
            test_mode = config.get("test_mode", False)  
        log_message("[INFO] Paramètres chargés.")
        test_mode_checkbox.select() if test_mode else test_mode_checkbox.deselect()

def envoyer_message():
    global running
    if test_mode:
        log_message("[TEST MODE] Le message n'est pas envoyé. Mode test activé.")
        return

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

    if test_mode:
        log_message("[TEST MODE] Simulation d'une réponse de Mudae.")
        temps_attente = 30
        afficher_compte_a_rebours(temps_attente)
        return

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
    countdown_label.config(text=f"Temps restant : {minutes} min")
    progress_bar["value"] = 0
    progress_bar["maximum"] = minutes

    def countdown():
        nonlocal minutes
        while minutes > 0 and running:
            countdown_label.config(text=f"Temps restant : {minutes} min")
            progress_bar["value"] = progress_bar["maximum"] - minutes
            root.update()
            time.sleep(60)
            minutes -= 1

        if running:
            log_message("[INFO] Temps écoulé, envoi du message.")
            envoyer_message()
            jouer_alerte_sonore() 

    threading.Thread(target=countdown, daemon=True).start()

def jouer_alerte_sonore():
    if os.path.exists(SOUND_PATH):
        pygame.mixer.music.load(SOUND_PATH)
        pygame.mixer.music.play()
        log_message("[INFO] Alerte sonore jouée.")
    else:
        log_message("[ERROR] Fichier sonore non trouvé.")

def log_message(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

    with open(LOG_FILE, "a") as log_file:
        log_file.write(message + "\n")

def toggle_bot():
    global running
    if running:
        running = False
        log_message("[INFO] Bot arrêté.")
        start_button.config(text="Démarrer", bg="green")
    else:
        if not token_entry.get() or not channel_entry.get():
            messagebox.showerror("Erreur", "Veuillez entrer un token et un Channel ID valide.")
            return
        running = True
        sauvegarder_config()
        log_message("[INFO] Bot démarré.")
        start_button.config(text="Arrêter", bg="red")
        threading.Thread(target=envoyer_message, daemon=True).start()

def ouvrir_lien(event):
    webbrowser.open("https://mediaboss.fr/trouver-token-discord/")  

def toggle_test_mode():
    global test_mode
    test_mode = not test_mode
    sauvegarder_config()  

root = tk.Tk()
root.title("Mudae Pokemon Automatiseur")
root.geometry("500x450")
root.minsize(400, 400)

if os.path.exists(ICON_PATH):
    root.iconbitmap(ICON_PATH)

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(5, weight=1)

tk.Label(root, text="Token Discord :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
token_entry = tk.Entry(root, width=50, show="*")
token_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

info_label = tk.Label(root, text="🔗", fg="blue", cursor="hand2")
info_label.grid(row=0, column=2, padx=5)
info_label.bind("<Button-1>", ouvrir_lien)

tk.Label(root, text="Channel ID :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
channel_entry = tk.Entry(root, width=50)
channel_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

button_frame = tk.Frame(root)
button_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)

start_button = tk.Button(button_frame, text="Démarrer", command=toggle_bot, bg="green", fg="white", width=12)
start_button.grid(row=0, column=0, padx=10, sticky="ew")

save_button = tk.Button(button_frame, text="Sauvegarder", command=sauvegarder_config, bg="blue", fg="white", width=12)
save_button.grid(row=0, column=1, padx=10, sticky="ew")

test_mode_checkbox = tk.Checkbutton(root, text="Mode Test", command=toggle_test_mode)
test_mode_checkbox.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

countdown_label = tk.Label(root, text="Temps restant : -")
countdown_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

progress_bar = Progressbar(root, length=300, mode='determinate')
progress_bar.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

log_text = tk.Text(root, height=10, width=55)
log_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

charger_config()

root.mainloop()
