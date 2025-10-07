import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import os

# === Carica storico ===
storico_file = "storico_frecce.csv"
if not os.path.exists(storico_file):
    raise FileNotFoundError("⚠️ Il file storico_frecce.csv non è stato trovato.")

df = pd.read_csv(storico_file)
df['datetime'] = pd.to_datetime(df['datetime'])

# 🔧 Converti distanza in stringa per uniformare il confronto
df['distanza'] = df['distanza'].astype(str).str.strip()

intervalli = ["Ultimi 7 giorni", "Ultimi 15 giorni", "Ultimo mese", "Ultimi 3 mesi", "Ultimo anno", "Tutto"]
sessioni = sorted(df['session_id'].unique())
distanze_disponibili = sorted(df['distanza'].unique())

# === Funzioni ===
def filtra_dati(tipo, valore, distanza):
    df_filtrato = df[df['distanza'] == distanza]
    oggi = datetime.now()
    if tipo == "Per intervallo di tempo":
        if valore == "Ultimi 7 giorni": start = oggi - timedelta(days=7)
        elif valore == "Ultimi 15 giorni": start = oggi - timedelta(days=15)
        elif valore == "Ultimo mese": start = oggi - timedelta(days=30)
        elif valore == "Ultimi 3 mesi": start = oggi - timedelta(days=90)
        elif valore == "Ultimo anno": start = oggi - timedelta(days=365)
        elif valore == "Tutto": start = df['datetime'].min() - timedelta(days=1)
        else: return pd.DataFrame()
        return df_filtrato[df_filtrato['datetime'] >= start]
    elif tipo == "Per sessione":
        return df_filtrato[df_filtrato['session_id'] == valore]
    return pd.DataFrame()

def aggiorna_secondo_menu(*args):
    tipo = tipo_var.get()
    distanza = distanza_var.get()
    menu = valore_option["menu"]
    menu.delete(0, "end")

    if tipo == "Per intervallo di tempo":
        options = intervalli
    else:
        # mostra solo le sessioni della distanza selezionata
        sessioni_filtrate = df[df['distanza'] == distanza]['session_id'].unique()
        options = sorted(sessioni_filtrate)

    if options:
        for val in options:
            menu.add_command(label=val, command=lambda v=val: valore_var.set(v))
        valore_var.set(options[0])
    else:
        valore_var.set("")

    aggiorna_dashboard()

def aggiorna_dashboard(*args):
    tipo = tipo_var.get()
    valore = valore_var.get()
    distanza = distanza_var.get()
    if not tipo or not valore or not distanza:
        return
    df_filtrato = filtra_dati(tipo, valore, distanza)
    disegna_bersaglio(df_filtrato)
    aggiorna_statistiche(df_filtrato)

def disegna_bersaglio(dataframe):
    global ax
    ax.clear()

    colori = ['white', 'black', 'blue', 'red', 'yellow']
    r = 10
    for i in range(5):
        for _ in range(2):
            ax.add_patch(patches.Circle((0, 0), r, color=colori[i], ec='black'))
            r -= 1

    if not dataframe.empty:
        for _, row in dataframe.iterrows():
            ax.plot(row['x'], row['y'], marker='x', color='limegreen', markersize=6, linewidth=1.5)

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    fig_canvas.draw_idle()

def aggiorna_statistiche(df_filtrato):
    if df_filtrato.empty:
        stats_label.config(text="Nessuna freccia trovata.")
        return

    media_punteggio = df_filtrato['punteggio'].mean()
    centro_x = df_filtrato['x'].mean()
    centro_y = df_filtrato['y'].mean()
    distanza_media = (df_filtrato['x']**2 + df_filtrato['y']**2).pow(0.5).mean()
    dev_standard = (df_filtrato['x']**2 + df_filtrato['y']**2).pow(0.5).std()

    testo = (
        f"🎯 Frecce: {len(df_filtrato)}\n"
        f"📊 Totale: {df_filtrato['punteggio'].sum()}  |  Medio: {media_punteggio:.2f}\n"
        f"📍 Centro medio: ({centro_x:.2f}, {centro_y:.2f})\n"
        f"📏 Distanza media: {distanza_media:.2f}\n"
        f"📉 Dev. standard: {dev_standard:.2f}"
    )
    stats_label.config(text=testo)

# === GUI ===
root = tk.Tk()
root.title("🎯 Dashboard storico frecce")

font_grande = ("Segoe UI", 20)

# Frame Selezione
frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

# === DISTANZA ===
tk.Label(frame, text="Distanza:", font=font_grande).grid(row=0, column=0, sticky="w", pady=10)
distanza_var = tk.StringVar(value=distanze_disponibili[0])
distanza_option = tk.OptionMenu(frame, distanza_var, *distanze_disponibili)
distanza_option.config(font=font_grande, width=25)
distanza_option["menu"].config(font=font_grande)
distanza_option.grid(row=0, column=1, pady=5)

# === FILTRI ===
tk.Label(frame, text="Filtro:", font=font_grande).grid(row=1, column=0, sticky="w", pady=10)
tk.Label(frame, text="Valore:", font=font_grande).grid(row=2, column=0, sticky="w", pady=10)

tipo_var = tk.StringVar(value="Per intervallo di tempo")
valore_var = tk.StringVar(value=intervalli[0])

# Filtro tipo
tipo_option = tk.OptionMenu(frame, tipo_var, *["Per intervallo di tempo", "Per sessione"])
tipo_option.config(font=font_grande, width=25)
tipo_option["menu"].config(font=font_grande)
tipo_option.grid(row=1, column=1, pady=5)

# Filtro valore
valore_option = tk.OptionMenu(frame, valore_var, *intervalli)
valore_option.config(font=font_grande, width=25)
valore_option["menu"].config(font=font_grande)
valore_option.grid(row=2, column=1, pady=5)

# Callback
tipo_var.trace_add("write", aggiorna_secondo_menu)
valore_var.trace_add("write", aggiorna_dashboard)
distanza_var.trace_add("write", aggiorna_secondo_menu)

# Bersaglio
fig, ax = plt.subplots(figsize=(12, 12))
fig_canvas = FigureCanvasTkAgg(fig, master=root)
fig_canvas.get_tk_widget().pack(pady=20)

# Statistiche
stats_label = tk.Label(root, text="Statistiche", font=font_grande, justify="left", pady=15)
stats_label.pack()

# Avvio iniziale
aggiorna_dashboard()
root.mainloop()
