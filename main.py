import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import time
import requests
import json
import re
import webbrowser
import pygame
from ttkbootstrap import Style

pygame.mixer.init()

# Chemins des fichiers
APPDATA_DIR = os.path.join(os.getenv("APPDATA"), "MudaeBot")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")
LOG_FILE = os.path.join(APPDATA_DIR, "log.txt")
ICON_PATH = "mudae.ico"
SOUND_PATH = "music.mp3"

GITHUB_REPO = "Khalifouille/mudae-pokemon-automatiseur"
CURRENT_VERSION = "1.0.0"

running = False
test_mode = False

if not os.path.exists(APPDATA_DIR):
    os.makedirs(APPDATA_DIR)

def log_message(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(message + "\n")

def check_for_updates():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            latest_version = response.json()["tag_name"]
            if latest_version != CURRENT_VERSION:
                log_message(f"[UPDATE] Nouvelle version disponible : {latest_version} !")
                log_message("Télécharge-la ici : https://github.com/Khalifouille/mudae-pokemon-automatiseur/releases/latest")
                prompt_update()
            else:
                log_message("[INFO] Aucune mise à jour disponible.")
        else:
            log_message("[ERROR] Impossible de vérifier les mises à jour.")
    except Exception as e:
        log_message(f"[ERROR] Erreur lors de la vérification des mises à jour : {e}")

def prompt_update():
    result = messagebox.askyesno("Mise à jour disponible", "Une nouvelle version est disponible ! Veux-tu la télécharger maintenant ?")
    if result:
        webbrowser.open("https://github.com/Khalifouille/mudae-pokemon-automatiseur/releases/latest")

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
        test_mode_checkbox.state(["selected"]) if test_mode else test_mode_checkbox.state(["!selected"])

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
        temps_attente = 1
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
        stop_music_button.grid()
    else:
        log_message("[ERROR] Fichier sonore non trouvé.")

def stop_music():
    pygame.mixer.music.stop()
    log_message("[INFO] Musique arrêtée.")
    stop_music_button.grid_remove()

def toggle_bot():
    global running
    if running:
        running = False
        log_message("[INFO] Bot arrêté.")
        start_button.config(text="Démarrer", bootstyle="success")
    else:
        if not token_entry.get() or not channel_entry.get():
            messagebox.showerror("Erreur", "Veuillez entrer un token et un Channel ID valide.")
            return
        running = True
        sauvegarder_config()
        log_message("[INFO] Bot démarré.")
        start_button.config(text="Arrêter", bootstyle="danger")
        threading.Thread(target=envoyer_message, daemon=True).start()

def ouvrir_lien(event):
    webbrowser.open("https://mediaboss.fr/trouver-token-discord/")

def toggle_test_mode():
    global test_mode
    test_mode = not test_mode
    sauvegarder_config()

style = Style(theme="darkly")
root = style.master
root.title("Mudae Pokemon Automatiseur")
root.geometry("600x500")
root.minsize(500, 450)

if os.path.exists(ICON_PATH):
    root.iconbitmap(ICON_PATH)

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

header_frame = ttk.Frame(main_frame)
header_frame.pack(fill=tk.X, pady=5)

ttk.Label(header_frame, text="Mudae Pokemon Automatiseur", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)

input_frame = ttk.Frame(main_frame)
input_frame.pack(fill=tk.X, pady=10)

ttk.Label(input_frame, text="Token Discord :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
token_entry = ttk.Entry(input_frame, width=50, show="*")
token_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

info_label = ttk.Label(input_frame, text="🔗", foreground="blue", cursor="hand2")
info_label.grid(row=0, column=2, padx=5)
info_label.bind("<Button-1>", ouvrir_lien)

ttk.Label(input_frame, text="Channel ID :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
channel_entry = ttk.Entry(input_frame, width=50)
channel_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

button_frame = ttk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=10)

start_button = ttk.Button(button_frame, text="Démarrer", command=toggle_bot, bootstyle="success")
start_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

save_button = ttk.Button(button_frame, text="Sauvegarder", command=sauvegarder_config, bootstyle="info")
save_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

test_mode_checkbox = ttk.Checkbutton(main_frame, text="Mode Test", command=toggle_test_mode, bootstyle="round-toggle")
test_mode_checkbox.pack(pady=5)

countdown_label = ttk.Label(main_frame, text="Temps restant : -", font=("Segoe UI", 12))
countdown_label.pack(pady=5)

progress_bar = ttk.Progressbar(main_frame, length=300, mode='determinate')
progress_bar.pack(fill=tk.X, pady=10)

stop_music_button = ttk.Button(main_frame, text="Stop Music", command=stop_music, bootstyle="danger")
stop_music_button.pack(pady=5)
stop_music_button.pack_forget()

log_frame = ttk.Frame(main_frame)
log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

log_text = tk.Text(log_frame, height=10, width=55, wrap=tk.WORD)
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text.config(yscrollcommand=scrollbar.set)

charger_config()
check_for_updates()

root.mainloop()