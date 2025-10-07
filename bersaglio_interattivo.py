import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from datetime import datetime
import os
import sys

# === Ottieni la directory dove si trova il file .py ===
base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# === Parametri iniziali ===
distanza = input("Inserisci la distanza di tiro (es. 18m, 30m): ")

while True:
    try:
        frecce_per_volee = int(input("Quante frecce per volee? (3 o 6): "))
        if frecce_per_volee in [3, 6]:
            break
    except:
        continue

# === Identificativo sessione ===
now = datetime.now()
session_id = now.strftime('%Y-%m-%d_%H-%M')
timestamp = now.strftime('%Y-%m-%d %H:%M')
storico_file = os.path.join(base_dir, "storico_frecce.csv")

tiri_totali = []
volee_corrente = []
volee_numero = 1

# === Funzioni di supporto ===
def calcola_punteggio(x, y):
    distanza = np.sqrt(x**2 + y**2)
    if distanza <= 1: return 10
    elif distanza <= 2: return 9
    elif distanza <= 3: return 8
    elif distanza <= 4: return 7
    elif distanza <= 5: return 6
    elif distanza <= 6: return 5
    elif distanza <= 7: return 4
    elif distanza <= 8: return 3
    elif distanza <= 9: return 2
    elif distanza <= 10: return 1
    else: return 0

def disegna_bersaglio(ax):
    colori = ['white', 'black', 'blue', 'red', 'yellow']
    r = 10
    for i in range(5):
        for j in range(2):
            c = patches.Circle((0, 0), r, color=colori[i], ec='black')
            ax.add_patch(c)
            r -= 1
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_aspect('equal')
    ax.axis('off')

def onclick(event):
    global volee_corrente, tiri_totali, fig, ax, volee_numero

    if event.inaxes is not ax:
        return

    x, y = event.xdata, event.ydata
    p = calcola_punteggio(x, y)
    volee_corrente.append((x, y, p))
    tiri_totali.append((x, y, p, volee_numero))
    ax.plot(x, y, marker='x', color='limegreen', markersize=6, linewidth=1.5)
    fig.canvas.draw()

    print(f"  Freccia {len(volee_corrente)}: ({x:.2f}, {y:.2f}) → {p} punti")

    if len(volee_corrente) >= frecce_per_volee:
        print(f"\n✅ Volee {volee_numero} completata.")
        volee_numero += 1
        volee_corrente = []
        plt.close()

# === Loop per inserire volee ===
while True:
    fig, ax = plt.subplots(figsize=(6, 6))
    disegna_bersaglio(ax)
    ax.set_title(f"Clicca sul bersaglio – Volee {volee_numero}")
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    cont = input("Vuoi continuare con un'altra volee? (s/n): ").lower()
    if cont != 's':
        break

# === Analisi finale ===
df = pd.DataFrame(tiri_totali, columns=['x', 'y', 'punteggio', 'volee'])
df['distanza'] = distanza
df['session_id'] = session_id
df['datetime'] = timestamp
df['freccia'] = df.groupby('volee').cumcount() + 1

print("\n📊 STATISTICHE FINE ALLENAMENTO")
print(f"Frecce totali: {len(df)}")
print(f"Punteggio totale: {df['punteggio'].sum()}")
print(f"Punteggio medio: {df['punteggio'].mean():.2f}")
media_x, media_y = df['x'].mean(), df['y'].mean()
print(f"Centro medio: ({media_x:.2f}, {media_y:.2f})")
distanze = np.sqrt(df['x']**2 + df['y']**2)
print(f"Distanza media dal centro: {distanze.mean():.2f}")
print(f"Deviazione standard: {distanze.std():.2f}")

# === Salva bersaglio finale ===
fig, ax = plt.subplots(figsize=(6, 6))
disegna_bersaglio(ax)
for x, y, _, _ in tiri_totali:
    ax.plot(x, y, marker='x', color='limegreen', markersize=6, linewidth=1.5)
ax.set_title(f"Tutti i colpi – Sessione {session_id}")



# === Salva sessione nella cronologia ===
columns_order = ['datetime', 'session_id', 'volee', 'freccia', 'x', 'y', 'punteggio', 'distanza']
df_finale = df[columns_order]

if os.path.exists(storico_file):
    df_old = pd.read_csv(storico_file)
    df_aggiornato = pd.concat([df_old, df_finale], ignore_index=True)
else:
    df_aggiornato = df_finale

df_aggiornato.to_csv(storico_file, index=False)
print(f"✅ Risultati salvati in: {storico_file}")
print(f"✅ Immagine bersaglio salvata in: {img_path}")
