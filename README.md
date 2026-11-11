# Video Searcher

App desktop per indicizzare e cercare i file video presenti in una o più cartelle (anche su SSD/HDD esterni) e aprirli con il lettore predefinito.

È nata come script Tkinter di poche righe per ritrovare i video sparsi su un disco esterno. Ogni volta che mi serviva qualcosa in più l'ho aggiunto, fino a riscriverla in **PyQt6**: lo storico dei commit contiene tutte le versioni, dalla prima all'ultima.

## Funzionalità

- Cartelle da scansionare scelte dall'app e ricordate tra un avvio e l'altro, senza doppioni (una sottocartella di una già presente viene ignorata)
- Scansione ricorsiva alla ricerca di file `.mp4`, `.mkv`, `.avi`, `.mov`; se un disco esterno è scollegato lo segnala e prosegue con le altre cartelle
- Scansione in un **thread separato** (`QThread`), così l'interfaccia non si blocca
- **Cache JSON** dei risultati: all'avvio non serve riscansionare
- Ricerca istantanea per nome, anche con più parole (es. `mare 2023`)
- Ordinamento per percorso, data di modifica e dimensione
- **Ricerche salvate** con il numero di file trovati per ognuna
- Doppio click per aprire il video
- Tema scuro con fogli di stile Qt (QSS)

## Come è cresciuta

| Versione | Novità |
|----------|--------|
| prima versione | Tkinter: scansione dei dischi, ricerca per parole, doppio click per aprire |
| + ordinamento | Ordinamento per data e per dimensione, con freccia ↑/↓ |
| + contatore | Numero di video trovati e dimensione di ogni file |
| + tema scuro | Interfaccia scura |
| Mark 1 | Cache JSON della scansione, indice delle parole più frequenti nei nomi |
| Mark 2 | Parole da escludere dall'indice, salvate nella cache |
| Mark 3 | Ricerche salvate al posto dell'indice delle parole |
| Mark 4 | Riscrittura in PyQt6 con tabella, barra laterale e scansione in background |
| Mark 5 | Gestione degli errori: dischi non disponibili, cache danneggiata, file spostati |
| attuale | Codice riordinato e cartelle da scansionare scelte dall'utente |

Per vedere una versione precisa basta aprire il commit corrispondente nella cronologia.

## Avvio

```
pip install -r requirements.txt
python searcher.py
```

Al primo avvio premi **Aggiungi cartella** (o direttamente **Scansiona**) e scegli dove cercare i video. Le cartelle e i risultati vengono salvati in `video_cache.json`, accanto allo script.

## Tecnologie

Python 3 · PyQt6 · Tkinter (versioni precedenti) · JSON · threading con QThread
