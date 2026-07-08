# Report di Progetto: Quoridor

## 1. Introduzione
Il presente documento descrive l'architettura, le scelte di progettazione e lo stato di avanzamento del progetto **Quoridor**. Il software è un'implementazione digitale del gioco da tavolo omonimo, sviluppata in Python con interfaccia a riga di comando (CLI). L'obiettivo primario è garantire un'esperienza utente chiara e la completa portabilità del software tramite containerizzazione.

---

## 2. Modello di Dominio

Il modello di dominio identifica le astrazioni del mondo reale necessarie per comprendere e descrivere il problema. In ottemperanza alla prospettiva concettuale, questa descrizione è totalmente indipendente dalle scelte di implementazione software, dalle tecnologie o dall'architettura dell'applicazione.

Facendo riferimento esclusivo alle regole ufficiali e agli elementi fisici del gioco da tavolo *Quoridor*, il dominio mappa i seguenti concetti fondamentali e le loro proprietà intrinseche:

* **Partita:** Rappresenta la sessione di gioco nella sua interezza. Regola l'avvicendamento dei turni tra i partecipanti (2 o 4) e determina la fine del gioco al verificarsi della condizione di vittoria (il raggiungimento del lato opposto della scacchiera) o per eliminazione progressiva dei giocatori. Può opzionalmente svolgersi in modalità a tempo, nel qual caso è associata a un orologio di partita. La partita può essere avviata tramite interfaccia a riga di comando (CLI) oppure tramite un'interfaccia grafica avanzata (GUI), selezionabile al lancio dell'applicazione.
* **Scacchiera:** Il tabellone fisico su cui si svolge il gioco. È costituita da una plancia che include un reticolo di caselle quadrate e le relative intercapedini destinate all'inserimento dei muri.
* **Casella:** Ciascuno degli 81 spazi fisici (disposti in una griglia 9x9) che compongono la scacchiera. Ogni casella può ospitare, al massimo, un pedone alla volta.
* **Giocatore:** Ciascuno dei partecipanti (da 2 a 4) che competono nella partita. Ogni giocatore è caratterizzato da un obiettivo di vittoria, possiede una scorta limitata di muri (10 in modalità 2 giocatori, 5 in modalità 4 giocatori), controlla un singolo pedone e può trovarsi nello stato *attivo* oppure *eliminato*. In una partita a 4 giocatori un giocatore può essere eliminato per abbandono volontario o per esaurimento del tempo, lasciando proseguire la partita tra i rimanenti.
* **Pedone:** La pedina che rappresenta fisicamente il giocatore sulla scacchiera. Inizia la partita al centro della propria riga di partenza e si sposta ortogonalmente tra le caselle con lo scopo di raggiungere una qualsiasi casella della riga di traguardo (la riga di partenza dell'avversario).
* **Muro:** Un ostacolo avente una lunghezza pari a due caselle adiacenti. Può assumere un orientamento orizzontale o verticale e viene posizionato in modo permanente nelle intercapedini della scacchiera per deviare o allungare il percorso del pedone avversario. Sottostà alla regola fisica per cui non può mai bloccare completamente l'accesso al traguardo a un pedone.
* **OrologioPartita:** L'orologio stile scacchi associato opzionalmente a una partita in modalità a tempo. Gestisce un conto alla rovescia indipendente per ciascun giocatore attivo (fino a 4): il tempo di un giocatore scorre esclusivamente durante il proprio turno e si blocca non appena la mossa viene confermata. L'esaurimento del tempo di un giocatore ne determina l'eliminazione immediata; in una partita a 4 giocatori la partita prosegue tra i rimanenti finché non resta un solo giocatore o uno raggiunge il traguardo.
* **CronologiaMosse:** Il registro ordinato di tutte le mosse effettuate nel corso della partita. Ogni partita possiede una e una sola cronologia, che raccoglie in sequenza le mosse prodotte dai giocatori. Può essere consultata in qualsiasi momento durante la sessione e viene mostrata automaticamente al termine.
* **Mossa:** La singola azione registrata nella cronologia. È caratterizzata dal tipo (spostamento del pedone, piazzamento di un muro, abbandono o timeout), dal numero di turno in cui è stata effettuata e dal comando che la rappresenta. Ogni mossa è associata al giocatore che l'ha eseguita.
* **Replay:** La riproduzione sequenziale della partita appena conclusa. È associata alla cronologia mosse della partita e consente al giocatore di navigare liberamente tra le posizioni della scacchiera mossa per mossa, avanzando o tornando indietro, fino a rivivere l'intera sessione dalla posizione iniziale fino all'ultima mossa registrata.
* **InterfacciaUtente:** La modalità con cui il giocatore interagisce con la partita. Può assumere la forma di un'**interfaccia testuale (CLI)**, accessibile dal terminale tramite comandi digitati, oppure di un'**interfaccia grafica (GUI)**, avviabile con il flag `--gui`, che offre una rappresentazione visiva della scacchiera con interazione tramite mouse e una schermata di configurazione iniziale dedicata.

![Diagramma delle Classi – Modello di Dominio](https://www.plantuml.com/plantuml/png/ZLJRZjem47tFLrWyhW1jLtreLssrMogjaBegsii7c6GAepgUo7QGWFBlFKv2Rakhle0pS-RCcOkTtFcWNIXpa_XVR0ljTAvIexs_3y7nkWoqJCK-yu7KTG_YmzuGVXsdLV2MCrAK5s6lSWfRoNoIL3Hg1NeEMXqJfNB9jC772v2YRjLN4KFQmcFB_84brK4Smx6qWJRaajEPvJdLQRfbSZLHnZbPpsAf0wlFwcCNiD2UZAdHZZUwHwfKAaQiZRR5LlUod2LG5GPDv6GGA6kc47WNhSyetcvWH0T3D1nrvPegCfopXV4KQouTVsDVYEKrcul5hIYBbSISXNW-nBgUnffRp-8luXzBY8qSQ27PeD6XMXQ-3mU1nT1KxGZZI76CsanfDriw7FIWYpSTvm-7P1kM_X137DwANDUi2oKjdDWgL3-Azx6sJYSC3HDNMt14StoZTnhxXL-zNckBhk0OC6ifmwcTo4lfh8pccKTqDvGssHCLHk_xwMEK-ubjOlqQa986KXRVbrFryBeyNGo0jq8t-UvtE-wIedEJOe_TjohNREV5VdAH1Ep_9fdDDYLNiUUsJzvDrDLiLlrtD-6j-sO-Vp_fjlXY_6Wo0un4pFLyZkDeyWDOm_IsaxTAeneDMC0ZmR1yIPBUrMrrV8X2wXiwy2FtLGEfZt6fawHRjNubzRKPETiIhkjWQFAfE4Y2bF5MjcnDihYP5q5TNvg5kiMZKZZ9980vgyZhlUxrftz1o1E6scB7z-eSDHeW0l7u1e1D5VQsuvz-8soueV-1mWecTsIp-7B_0G==)
---

## 3. Requisiti Specifici

### 3.1 Requisiti Funzionali
I requisiti funzionali definiscono i servizi e le funzionalità che il sistema deve offrire all'utente.

### US 1 -  Visualizzazione della scacchiera
Come giocatore, voglio visualizzare la griglia di gioco in formato testuale in modo dinamico, affinché io possa avere sempre sotto controllo lo stato della partita ad ogni interazione.

**Criteri di Accettazione:**
* Il sistema mostra la griglia di gioco testuale (9x9).
* La visualizzazione include l'esatta posizione attuale dei pedoni dei giocatori.
* La visualizzazione mostra il numero di muri residui a disposizione di ciascun giocatore.
* Viene indicato chiaramente di chi è il turno corrente.
* L'aggiornamento avviene dinamicamente a ogni interazione valida.

---

### US 2 - Muovere il pedone
Come giocatore, voglio poter spostare il mio pedone digitando la coordinata della casella di destinazione (es. `e2`), affinché io possa avanzare verso l'obiettivo.

**Criteri di Accettazione:**
* Il movimento è consentito solo verso caselle adiacenti libere (verticali o orizzontali).
* È consentito il "salto" sopra il pedone avversario se i due si trovano faccia a faccia.
* Il movimento viene impedito se la destinazione è fuori dai bordi (griglia 9x9).
* Il movimento viene impedito se c'è un muro che blocca fisicamente il passaggio.
* Il movimento viene impedito se la casella di destinazione è già occupata.
* In caso di comando non valido/mossa illegale, il sistema mostra un messaggio di errore esplicito e richiede un nuovo inserimento **senza** consumare il turno.
* Dopo un movimento valido, le coordinate vengono aggiornate, la scacchiera ristampata e il turno passa all'avversario.

---

### US 3 - Piazzare un muro orizzontale
Come giocatore, voglio piazzare un muro orizzontale digitando `h` seguito dalla coordinata in basso a sinistra (es. `he3`), affinché io possa bloccare il passaggio verticale al mio avversario.

**Criteri di Accettazione:**
* Il muro viene posizionato sopra la riga indicata e si estende verso destra per 2 colonne, bloccando il passaggio verticale.
* Il piazzamento è consentito solo se il giocatore ha ancora muri nella propria scorta (la scorta diminuisce di 1 a ogni utilizzo valido).
* Il piazzamento viene impedito se il muro supera i confini destri o superiori della scacchiera.
* Il piazzamento viene impedito se si sovrappone, anche parzialmente, a un altro muro orizzontale.
* Il piazzamento viene impedito se incrocia a croce un muro verticale esistente.
* In caso di errore/mossa illegale, mostrare messaggio esplicito senza consumare il turno.
* Dopo un piazzamento valido, aggiornare la scorta muri, ristampare la scacchiera e passare il turno.

---

### US 4 - Piazzare un muro verticale
Come giocatore, voglio piazzare un muro verticale digitando `v` seguito dalla coordinata in alto a destra (es. `vc2`), affinché io possa bloccare il passaggio orizzontale al mio avversario.

**Criteri di Accettazione:**
* Il muro viene posizionato a sinistra della colonna indicata e si estende verso il basso per 2 righe, bloccando il passaggio orizzontale.
* Il piazzamento è consentito solo se il giocatore ha ancora muri disponibili (la scorta diminuisce di 1).
* Il piazzamento viene impedito se il muro supera i confini inferiori o sinistri della scacchiera.
* Il piazzamento viene impedito se si sovrappone, anche parzialmente, a un altro muro verticale.
* Il piazzamento viene impedito se incrocia a croce un muro orizzontale esistente.
* In caso di errore/mossa illegale, mostrare messaggio esplicito senza consumare il turno.
* Dopo un piazzamento valido, aggiornare la scorta muri, ristampare la scacchiera e passare il turno.

---

### US 5 - Verifica della condizione di vittoria
Come sistema, voglio verificare la condizione di vittoria dopo ogni mossa valida, affinché io possa terminare la partita ed eleggere un vincitore non appena l'obiettivo viene raggiunto.

**Criteri di Accettazione:**
* Il Giocatore 1 (P1), che inizia dalla riga 1, vince se il suo pedone raggiunge qualsiasi casella della riga 9.
* Il Giocatore 2 (P2), che inizia dalla riga 9, vince se il suo pedone raggiunge qualsiasi casella della riga 1.
* Quando la condizione è soddisfatta, stampare per l'ultima volta la scacchiera aggiornata.
* Mostrare un messaggio di vittoria esplicito per il giocatore vincente.
* Presentare due opzioni all'utente: iniziare nuova partita (comando `n`) o uscire definitivamente (comando `q`).

---

### US 6 - Abbandono della partita

Come giocatore di turno, voglio poter abbandonare la partita digitando il comando `exit` al posto della mossa, affinché io possa ritirarmi volontariamente concedendo la vittoria.

**Criteri di Accettazione:**
* Il comando `exit` inserito durante il turno interrompe immediatamente la partita.
* Il sistema dichiara vincitore l'avversario (es. "Il Giocatore 1 ha abbandonato. Il Giocatore 2 vince la partita!").
* Dopo l'annuncio, presentare le opzioni di fine partita: nuova partita (`n`) o uscita (`q`).
* Se il comando `exit` viene digitato male, gestirlo come normale mossa non valida (errore, nessun consumo turno).

---

### US 7 - Visualizzazione del messaggio di aiuto
Come giocatore, voglio poter visualizzare una guida ai comandi digitando `help`, affinché io possa rinfrescare la memoria sulle regole e i controlli senza penalità.

**Criteri di Accettazione:**
* Il comando `help` stampa un elenco testuale leggibile con le istruzioni di movimento, piazzamento muri e utility (es. `exit`).
* L'utilizzo del comando non consuma il turno del giocatore.
* Dopo la lettura della guida, il sistema ristampa la scacchiera e attende nuovamente l'input del giocatore di turno.

---

### US 8 - Uscita immediata dal gioco
Come utente, voglio poter chiudere l'applicazione in qualsiasi momento digitando `quit`, affinché l'esecuzione venga terminata in modo sicuro e pulito.

**Criteri di Accettazione:**
* Il comando `quit` è riconosciuto ogni volta che il sistema attende un input.
* All'inserimento, stampare un breve messaggio di chiusura (es. "Uscita dal gioco in corso... Arrivederci!").
* Arrestare il processo con codice di uscita `0`.
* Assicurarsi che l'applicazione e il container Docker associato si arrestino correttamente, senza crash o errori, ritornando al prompt del terminale nativo.

---

### US 9 - Modalità a tempo (orologio stile scacchi)
Come giocatore, voglio poter scegliere se giocare con un orologio a tempo stile scacchi, in modo da rendere la partita più dinamica e competitiva gestendo strategicamente il proprio tempo residuo.

**Criteri di Accettazione:**
* All'avvio della partita, il sistema chiede al giocatore se vuole attivare la modalità a tempo (es. "Vuoi giocare con un limite di tempo? [s/n]").
* Se la modalità è attivata, il giocatore inserisce il tempo totale a disposizione per ciascun giocatore espresso in minuti (es. 5, 10, 20 minuti), come negli scacchi.
* Ogni giocatore ha il proprio timer personale indipendente dagli altri.
* Il timer di un giocatore inizia a scalare i secondi all'inizio del suo turno e si ferma non appena il giocatore conferma la propria mossa.
* Al ritorno del turno di quel giocatore, il timer riprende dal tempo residuo precedentemente salvato.
* Il tempo residuo di ciascun giocatore è sempre visibile sul terminale durante la partita.
* Se il tempo di un giocatore si esaurisce, quel giocatore perde la partita e viene mostrato un messaggio di notifica (es. "Il Giocatore 1 ha esaurito il tempo. Ha perso!").
* Il comando `help` viene aggiornato per includere la descrizione della modalità a tempo e del suo funzionamento.

---

### US 10 - Visualizzazione della cronologia mosse

Come giocatore, voglio poter visualizzare la trascrizione completa delle mosse effettuate durante la partita, in modo da analizzare l'andamento del gioco a fine sessione o in qualsiasi momento durante il gioco.

**Criteri di Accettazione:**
* Al termine di ogni partita, il sistema mostra automaticamente la lista ordinata di tutte le mosse effettuate da ciascun giocatore, con il numero di turno, il giocatore e il tipo di mossa (spostamento o muro).
* La trascrizione è formattata in modo leggibile sul terminale (tabella con colonne: Turno, Giocatore, Tipo, Comando).
* Il giocatore può richiedere la trascrizione durante la partita digitando il comando `history`.
* L'utilizzo del comando `history` non consuma il turno del giocatore corrente.
* Il comando `help` viene aggiornato per includere il comando `history` e la sua descrizione.
* Se non è ancora stata effettuata alcuna mossa, il sistema mostra un messaggio informativo appropriato al posto della tabella.

---

### US 11 - Replay della partita
Come giocatore, voglio poter rivedere la partita appena conclusa mossa per mossa, affinché io possa rivivere le fasi salienti della sessione e analizzare le scelte effettuate.

**Criteri di Accettazione:**
* Al termine di una partita, il sistema offre l'opzione di avviarne il replay (es. "Vuoi rivedere la partita? [s/n]").
* Il replay ripercorre le mosse aggiornando la visualizzazione della board sul terminale a ogni passo, mostrando il numero della mossa corrente sul totale (es. "Mossa 3 / 24").
* Il giocatore può navigare liberamente tra le mosse digitando `next` (o premendo Invio) per andare avanti e `prev` per tornare indietro.
* Il giocatore può uscire dal replay in qualsiasi momento digitando `quit`, senza essere obbligato a visualizzare tutte le mosse.
* Durante il replay non è possibile inserire mosse di gioco; il sistema mostra un messaggio esplicativo se il giocatore tenta di farlo.
* Il comando `help` viene aggiornato per descrivere la funzionalità di replay e i comandi disponibili (`next`, `prev`, `quit`).

---

### US 12 - Modalità 2 o 4 giocatori
Come giocatore, voglio poter avviare una partita a 2 o a 4 giocatori, in modo da avere una modalità di gioco più variegata rispetto al classico 1v1, sapendo che se un giocatore abbandona durante una partita a 4 la partita può proseguire in 3.

**Criteri di Accettazione:**
* All'avvio, il sistema chiede quanti giocatori parteciperanno: le uniche opzioni valide sono `2` o `4`.
* In una partita a 2 giocatori, ogni giocatore dispone di 10 muri come da regole standard.
* In una partita a 4 giocatori, ogni giocatore dispone di 5 muri e i giocatori partono dai quattro lati della board: Nord (P1), Sud (P2), Ovest (P3), Est (P4).
* Se durante una partita a 4 giocatori uno dei giocatori abbandona (tramite il comando `exit`) o esaurisce il tempo, viene eliminato e la partita prosegue regolarmente tra i 3 giocatori rimanenti.
* Il sistema notifica gli altri giocatori quando uno di essi abbandona (es. "Il Giocatore 3 ha abbandonato la partita. Si continua in 3.").
* La condizione di vittoria rimane invariata: il primo giocatore a raggiungere il lato opposto della board vince.
* Il comando `help` viene aggiornato per descrivere le due modalità disponibili (2 o 4 giocatori) e le relative regole.

---

### US 13 - Avviare il gioco con un'interfaccia avanzata in alternativa alla CLI

Come giocatore, voglio poter avviare il gioco con un'interfaccia grafica avanzata passando l'argomento `--gui` da riga di comando, in modo da avere un'esperienza di gioco più visiva rispetto alla CLI standard.

**Criteri di Accettazione:**
* Il gioco si avvia in modalità CLI di default; passando `--gui` alla riga di comando, viene avviata l'interfaccia grafica.
* All'avvio della GUI viene mostrata una schermata di configurazione iniziale che consente di scegliere il numero di giocatori (2 o 4) e di attivare la modalità a tempo con il relativo numero di minuti.
* La GUI mostra la board di gioco aggiornata in tempo reale, con i giocatori e i muri chiaramente distinguibili tramite colori dedicati.
* Tutte le funzionalità disponibili in CLI (movimenti, piazzamento muri, abbandono, cronologia mosse, aiuto, replay, modalità a tempo) sono accessibili anche tramite GUI attraverso pulsanti e interazione con il mouse.
* Il piazzamento di muri mostra un'anteprima visiva colorata (ambra se valida, rossa se non valida) prima della conferma.
* Al termine della partita vengono proposte le stesse opzioni della CLI: replay, nuova partita o uscita.

---

### FIX - Ristampa dinamica della scacchiera

Come utente, voglio che il terminale venga pulito prima della stampa di una nuova scacchiera valida, affinché io possa avere la sensazione di un aggiornamento in tempo reale senza accumulare cronologia illeggibile.

**Criteri di Accettazione:**
* Il sistema effettua la pulizia del terminale *solo* immediatamente prima della ristampa di una mossa valida.
* La pulizia utilizza comandi cross-platform: `cls` su Windows e `clear` su Unix/Linux/macOS.
* Il meccanismo di pulizia deve essere pienamente compatibile con l'ambiente Docker.
* Dopo la pulizia, informazioni accessorie (muri rimanenti, turno corrente) devono essere ancora visibili assieme alla griglia.
* Il terminale **non** deve essere pulito in caso di: comandi non validi, comando di aiuto (`help`), o qualsiasi situazione in cui non venga effettuata una mossa valida (per permettere la lettura dell'errore).


---

### 3.2 Requisiti Non Funzionali
L'app deve essere eseguita in un container docker. I terminali supportati sono:
1. Terminal di Linux
2. Terminal di MacOS
3. Powershell di Windows
4. Git Bash di Windows
Notazione testuale compatta: le caselle della griglia 9×9 si identificano con una lettera di colonna (a–i) e un numero di riga (1–9), e le due azioni di gioco si distinguono per la forma del comando.
 
**Movimento del pedone:** si digita solo la casella di destinazione
```
e2
```
 
**Piazzamento di un muro:** si digita la posizione dell'intersezione seguita dall'orientamento, h per orizzontale o v per verticale.
```
he3
vd5
```
 
---

## 4. System Design

### Decisioni Architetturali e Principi di Progettazione

Le decisioni in fase di design sono state prese per supportare attivamente i requisiti non funzionali e garantire la manutenibilità del codice:

1. **Architettura a Livelli (Layered Architecture)**
   Il sistema adotta una netta separazione delle responsabilità (*Separation of Concerns*) dividendosi in quattro strati comunicanti:
   * **Livello di Controllo CLI (`main.py`)**: Funge da controller MVC per la modalità testuale. Non contiene né logica di dominio né logica di presentazione. Coordina il flusso di gioco: configura la partita (con o senza timer tramite le funzioni `setup_timer()` e `new_game()`), interpreta i comandi speciali (`quit`, `help`, `exit`) e, dopo ogni mossa valida, verifica la condizione di vittoria tramite `WinHandler.check_win()` e gestisce la fine partita tramite `handle_post_game()`. Pulisce il terminale (`clear_screen()`) unicamente prima di una ristampa valida della scacchiera.
   * **Livello di Presentazione CLI (`view.py`)**: Interamente racchiuso nella classe `QuoridorView`, è l'unico punto del sistema responsabile di tutto l'output verso l'utente e di tutti i prompt di input nella modalità testuale. Espone metodi dedicati per ogni evento di gioco (`show_winner()`, `show_timeout_loss()`, `show_exit()`, `show_error()`, `show_help()`, ecc.) e per il rendering della scacchiera (`display_board()`), incluso il pannello dei timer (`_display_timers()`). Nessun altro modulo produce output nella modalità CLI.
   * **Livello di Presentazione GUI (`src/gui/`)**: Implementato con il framework **Textual**, costituisce l'interfaccia grafica alternativa alla CLI, avviabile con il flag `--gui`. È composto da `QuoridorApp` (l'applicazione Textual radice), `SetupScreen` (schermata di configurazione iniziale), `GameScreen` (schermata principale di gioco), `BoardWidget` (widget grafico della scacchiera 9×9 con interazione mouse), `PlayerCard` (widget card per stato e timer di ciascun giocatore) e `overlays.py` (schermate modali per aiuto, cronologia, vittoria, replay e notifiche). Tutta la logica di presentazione GUI è incapsulata in questo livello, senza alcuna dipendenza dal livello di presentazione CLI.
   * **Livello di Dominio (`board.py`, `movement.py`, `wall.py`, `win_handler.py`, `timer.py`, `history.py`, `replay.py`)**: Contiene lo stato puro della partita e tutta la logica di business, senza alcuna dipendenza dall'interfaccia utente (né CLI né GUI). `QuoridorBoard` gestisce lo stato della scacchiera, supportando modalità a 2 o 4 giocatori (con posizionamenti iniziali e dotazioni di muri distinti), e delega le mosse a `MovementHandler` e i piazzamenti muri a `WallHandler` tramite il metodo `process_move()`. Espone i metodi `eliminate_player()` e `advance_turn()` per gestire l'uscita di un giocatore e l'avvicendamento dei turni tra i giocatori rimanenti. `WinHandler` incapsula la verifica della condizione di vittoria per entrambe le modalità (riga opposta per P1/P2, colonna opposta per P3/P4, e ultimo rimasto in caso di eliminazioni progressive). `GameTimer` gestisce l'orologio stile scacchi con countdown indipendenti per i giocatori attivi, esponendo i metodi `start_turn()`, `stop_turn()`, `get_remaining()`, `is_expired()` e `remove_player()`. `MoveHistory` registra in forma strutturata ogni mossa valida tramite `record_move()` e ne espone la lista ordinata tramite `get_all_moves()`; viene interrogata sia dal controller CLI sia dalla `GameScreen` GUI. `ReplayHandler` ricostruisce la sequenza degli snapshot della scacchiera a partire dalla cronologia mosse tramite `_build_snapshots()`, esponendo i metodi `get_snapshot()`, `get_move_info()` e `total_moves()` per consentire la navigazione passo per passo della partita conclusa; è condiviso tra la modalità CLI e quella GUI.

2. **Information Hiding e Incapsulamento**
   Ogni classe espone esclusivamente l'interfaccia minima necessaria. `QuoridorView` nasconde la gestione dei colori ANSI tramite Rich e l'attributo `accent_color` inizializzato nel costruttore. `GameTimer` incapsula il timestamp di avvio del turno e il dizionario dei tempi residui, esponendo solo metodi ad alto livello. `QuoridorBoard` nasconde i dettagli delle strutture dati (`h_walls`, `v_walls` come `set`) delegando la validazione ai relativi handler, rendendo il controller indipendente dai dettagli implementativi. Il layer GUI incapsula completamente la gestione degli eventi Textual (click mouse, hover, messaggi widget) senza esporre questi dettagli al livello di dominio.

3. **Portabilità e Containerizzazione (Docker)**
   Per soddisfare il requisito non funzionale di **Portabilità**, il progetto adotta la containerizzazione tramite **Docker** (evidenziata dalla presenza del `Dockerfile` nella radice del repository). La pulizia del terminale (`clear_screen()`) utilizza comandi cross-platform (`cls` su Windows, `clear` su Unix/Linux/macOS) pienamente compatibili con l'ambiente container.

---

### Diagramma dei Package

![Diagramma dei Package](https://www.plantuml.com/plantuml/png/ZPJFIyCm5CVl-Il2lEYb9myYeqm5puB78IMcZowO9k4bModY_sxQTJL9ks0EWtxpUT--7tibE-iOkcChYVqIoZ1aBRMkb-1_KV3anZ3-nHfu7m44xfXg90J04wBkNhJKI6_knnDSlfsZdpNMW1FqC1v29cUwOSPiw3SXbCwIHJv9iLWqHx6Xs-shDuUoz0WTpzvx5AR_k3nQS4TJMOu0AjG_DSEwwaJTW0jr8raFM75_6yhw1EXlR6GzTC8MZbjxrdwMQTBRMhTCgBlLNCSaGilMlwS55MNKCIcZPw6g0rEr10nb9zfOE0ZhDFQXX32KDokh-N8frfCz2UY2q2byFrGtok7K75XdboxxGQ_cYC72cymMj2ZAUO3qqOUBrcXqPPaobrooqDpTB1MqASlzzIwBpMF8KiaCOvRCBSYM4K7NguYmQzb5K3Qv6BtQb6K5mQxbs6J_ScYuapak_GIatOvy_fFmCk1Q7qWmlH4C5pnnJSZBsgU6qGhb_o4hQ7QsEr3ryCt_1G==)

---

### Diagramma dei Componenti

![Diagramma dei Componenti](https://www.plantuml.com/plantuml/png/ZPHDJyCm38Rl_HKHNE001yGP0KK2910V0tO0D8KsWeZcGqwsQI3-EtRIf5ar97fOyhv-vZYkrUhOUGv-hhhAVKfjEN35d5zr0dz1DgD8OvGrMcW_2GW63uhe2O1PrgOpmBOFmrDLbZUV_5smhIkv45rdM2jPRRG7WsABVLUCFIikzRvTlUZwwZ871RmoxjWrnj2kVZQdkWNXi1p-9R4iXc2VycvkGBO6dgHOlkYT1Ivumcv8ITx_yfq_ZlETM8lfkBKv6p9e4ZCHVcud3GYXaN6aPYx830U4s7EkH4RNqkK0OQU6GpkLxRlmoBsHcYs3p7-82C6t7Ly9g54YQuEODQWoMYVoPY40umuvqsypb69_TUZCAAcb6VKbL95ANA-Di6iyHc5VBxXkySqYg7edimaXVCgxRa2Ng396eO18NH1IppwY6a2fKwCVf0gOfpK3mKt5NKZd3U08xdp4NSRw287tWhew70j1PpA6gM_zqBAzlQCuRQKHcr8wL6gfOsMbaueelVwuAWvWiE9u5KOnJSDsg68wTkjDPfw8JId69jrbPCNhZCnqevIylDAQrnTQXJKuUL86Aqp5iT0jVQv-0G)
---

## 5. OO Design

Questa sezione documenta le decisioni di progettazione orientate agli oggetti adottate durante lo Sprint 2, con riferimento ai principi di OO design e ai design pattern applicati. Per ciascuna user story significativa vengono presentati i diagrammi delle classi e di sequenza realizzati in PlantUML, corredati di commento sulle scelte architetturali.

### 5.1 Principi di OO Design applicati

Il progetto Quoridor applica sistematicamente i seguenti principi di OO design:

**Presentazione Separata.** La logica di presentazione (CLI e GUI) è completamente separata dalla logica di dominio. Le classi `QuoridorView` (CLI) e il package `src/gui/` (GUI) non contengono regole di gioco, mentre le classi di dominio (`board.py`, `movement.py`, `wall.py`, ecc.) non producono output verso l'utente. Questa separazione permette di scrivere casi di test automatici con asserzioni testuali sulle classi di dominio senza dipendenze dall'interfaccia grafica.

**Information Hiding.** Ogni classe custodisce i propri dati interni: gli attributi di istanza sono privati (`h_walls`, `v_walls` come `set` in `QuoridorBoard`; `_start_time` e `_time_left` in `GameTimer`). Le classi esternano solo le operazioni strettamente necessarie (es. `process_move()`, `check_win()`, `get_remaining()`).

**Alta Coesione.** Ogni classe ha una responsabilità ben definita: `MovementHandler` gestisce esclusivamente la validazione e l'esecuzione dei movimenti dei pedoni; `WallHandler` si occupa unicamente del piazzamento e della validazione dei muri; `WinHandler` verifica solo la condizione di vittoria; `MoveHistory` registra e recupera la cronologia delle mosse.

**Basso Accoppiamento.** Le classi comunicano attraverso interfacce ben definite. Il controller `main.py` non conosce i dettagli implementativi di `QuoridorBoard` né di `QuoridorView`: interagisce con entrambi esclusivamente tramite i loro metodi pubblici, rendendo possibile modificare l'una senza impattare l'altra.

**DRY (Do Not Repeat Yourself).** La logica di validazione dei muri è centralizzata in `WallHandler`; la logica di verifica del percorso libero è incapsulata in `_is_wall_between()`. Non esistono sequenze di istruzioni duplicate tra la modalità CLI e quella GUI per quanto riguarda la logica di dominio.

**Principi SOLID applicati:**
- *Single Responsibility*: ogni classe di dominio ha una sola ragione per essere modificata.
- *Open/Closed*: l'aggiunta di nuove modalità di presentazione (es. GUI Textual) non ha richiesto modifiche alle classi di dominio.
- *Liskov Substitution*: non applicato tramite ereditarietà, ma tramite composizione e interfacce implicite.
- *Dependency Inversion*: il controller dipende dalle astrazioni (metodi pubblici) delle classi di dominio, non dai loro dettagli implementativi.

---

### 5.2 Design Pattern applicati

**Strategy** — Il metodo `process_move()` di `QuoridorBoard` smista ogni mossa ricevuta verso l'handler appropriato (`MovementHandler` o `WallHandler`) a seconda del formato del comando. Questo realizza il principio GoF "programma rispetto a un'interfaccia anziché rispetto a un'implementazione": il controller non conosce quale handler verrà invocato.

**Facade** — La classe `QuoridorBoard` funge da Facade per il livello di dominio: espone un'interfaccia unificata e semplice (`process_move()`, `eliminate_player()`, `advance_turn()`) nascondendo la complessità dei sottosistemi interni (movimento, muri, turni, stato della scacchiera).

**Observer (implicito)** — Il controller CLI e la `GameScreen` GUI interrogano `MoveHistory` e `GameTimer` dopo ogni mossa per aggiornare la visualizzazione, realizzando un pattern pull-based di notifica dello stato.

**Memento** — `ReplayHandler` cattura gli snapshot successivi della scacchiera durante la ricostruzione della partita, permettendo la navigazione avanti/indietro tra gli stati salvati senza violare l'incapsulamento di `QuoridorBoard`.

---

### 5.3 Diagrammi delle Classi

#### 5.3.1 Diagramma delle classi — Livello di Dominio (user story principali)

Il diagramma seguente mostra le classi che collaborano nella realizzazione delle user story di gioco (US 2, US 3, US 4, US 5), con le loro relazioni e responsabilità principali.

![Diagramma delle Classi – Livello di Dominio](https://www.plantuml.com/plantuml/png/jLN1Rjim3BtdAuIUd3KfrXvp6BeEsBh33bi7x2We4kiGaKL3afram_vzb9muTfAsfnq2n-GZzKW-olSXAX-Roax26bsjlAg4jYg4Zp5wN3OHlcfoJ_WRnFjJo6ToyIdkB8W7icRWNIgzBZqrpdmYIrviLXXXCib1udj37Wtv1rBUY3yJ8UQYfe0HoGMn40PrpCQDiZP82yznQ5t9R6TJWCxIdbcKZjY2hAtQWKyEYw7pnCOxYSx0bgteEgDhgW6sirwBsfE646H5BHITUoOqLPLoPigu9P7DGB1OeLFnSE0Ud30jeSaOPLhbDCXqVZ7ob12bRhm75m_nqpsBluUMVMCA5GCU-MWBVj-qPMxWOjpGZj4MD4_kLTOIWsoLHJCkq428qjDc_q-JFOjAtPPBY1i0L_XRJiy_VyVFknxRK__5uFz3cr4wTwNWFFnGIK1C974_ewqzXG0TzpVmH-heXiolXLw1NiiDkYBNS75CZwmqyhjzhQcr0_rT2m-Q_4dBqukCknhwYcTPfsSoINtF6RD2Six-x2-gWfzOzLsMaL_EbaUEDcEm0Z9V0pc8hS-MLCTtRqwglQ1gBhL-GT8UAeKENJc8EwRb8SAsHWzcuEwdnR7KlhHDVSK_87d6sfB1gJgiA8wMNfwD8J4yG8jy7KoFRUhScGAwPxhWZnJLS1Hz5vSDMdCaKQmwDSn4BvX33UDRyEhsIhoRp_FpTDdvNB1GggGJJ0vw9NYuRiV0nkD9pCtDXw6-5w89wWrE1sKlU3ub__U94I_LXSn7CIvOqYnulXwpf74odbe2ZtCpuH84hwlZBqU9waB0-3ocWvgOJeD1Gn8iD-WUdE5lsZy0)

#### 5.3.2 Diagramma delle classi — Presentazione separata (US 1, US 13)

Il diagramma mostra come la presentazione CLI e quella GUI dipendano dal dominio senza accoppiamento reciproco, applicando il principio di presentazione separata.

![Diagramma delle Classi – Presentazione Separata](https://www.plantuml.com/plantuml/png/XLN1Rjim3BtxAuIUN2m1TivXQ9S1NO4Dw9PkEngAp3f2956Wf6Jfa7yVxRYfAZZR9Gd49ptoFPAv2L5IJDPKOQkTboIjK4Q6S1iZwNMASA_GhVGpYFSPP2tLjYDChbsYGHBxZOwGnJt7PGUhU30W25IKhZDGLUEvkFg4LZkDL-9F9Kw4ubj2qYtIHvJK3kT2l1EUK448ZSKTrDx80z1CABHMklPQBCGQqOpG3cAZ4X6us9oGTO_GBZBWUERvoYzzrY4Y7Sui_LLfpC0IXbk64M-ktKaBZze2lRb4O2KNuhenj_xgaq4PHumE3Vpscg3D06FEn-gOAV9043Xp-QpHWLX-kP_IvgU6_SW_5rAflbGrEB0G8T98skhGapNhNibw-EnfTwZR4H4sk6_ssZdMw3Ml4W14IBKDtLHm0yRNHO3DiZxcNbrdYSr5yv9Px8KCzV2LlP6PnAekqKL2OpB9ARcIqy6-wTYRydp33MAWyHZYH7mk0iJaJuaCeRE__t7cxiUaCxVUdxD4nn8a5-l9qdgYbI80bryON3ef1pjcAwhXHdlYD3PDqjEl3bFpIxVSb4KU0Iu_omXbjDfE1bcX2otqIlimkBpC9pRvLaPeUB54gBd_Oo8t4tiUhp0Jvtafk7Xesz68xyDFkJRmUF3mXctLUrPe9rLaNvgGrbONYhE9HH_Dvn-AFRCGASX_mOQHkuZAbmal3UWwc8AzBey5Bo-aLZjPLNdllA36wXR2SkEIhBAp7fBRt3_beWO79IfpvJ9eIeS2CbLT0Pcix8OjvF-Klm00)

---

### 5.4 Diagrammi di Sequenza

#### 5.4.1 US 2 — Muovere il pedone (scenario principale)

Il diagramma mostra l'interazione tra gli oggetti durante l'esecuzione di un movimento valido del pedone in modalità CLI.

![Diagramma di Sequenza – US 2 Muovere il Pedone](https://www.plantuml.com/plantuml/png/bLJDYjim4BxxAOHF3cnBwN4FPN6WzIMmXM8VIZ6pqf0CiJLX9CVTj-_8JhA9cptiJVRtEoFZfn11uj1tMTYJFu10Rrx0xhV2WtThxbZCkAE86TYev_m7iGKzOMuWcETC9P4i7S17apzkWFoQVHJkEfI9ibalE3y75d8iDU4uCUft22M3k8bHBcFuY3twM85tbvngGMh8N-FD4ayc5GMTvNKYL5dsR3vzqyBcqP0FA1Gi6ikzkh0fC7msENxDLsaLT8I8QJPbgwPKoK7OOWXjhxx5eODNb8UbeCpAAQ9IFlv5EyHtgJgFqixaba9xX8xShRt345lXyNIotAb35qtF8O2P190PCnkbah3T4ei7S-10aTY7txFNdmijnGbQbaLM7bGJ8UsTyxdkWuc3-DL9Uehu9GFg6uVNenXJNYgu8tYBRP8Mgnavh_r_RPdCfnqtgPZTeTst8_dY9NqTINwXDYccgTxSljnQJVZiDS6sGv0sM46SYynOhP2ZaCPkfv0xKRK-r6z1HoPtcrLds0KytODdVtiNfqry1-NSNzNP-Gwbl6aQTZosAC9Iv9j5MlxXpjvbrsNMsPE-qh_3Fm00)

#### 5.4.2 US 3/4 — Piazzare un muro (scenario principale)

Il diagramma mostra il flusso per il piazzamento di un muro orizzontale o verticale.

![Diagramma di Sequenza – US 3/4 Piazzare un Muro](https://www.plantuml.com/plantuml/png/bPD1Qzj048Nl-XM3JZ8uWT9Re2N8qFfYIA78XrB4P7TQBrdjcDcLrEJNToHPhkKaXrw4TlTxRzwCLlSneQIsyLbySk68WWqyeddwBTm6ks7F0lt19ShG97tFlpesg6-K0qPuo5IId75730doknswiE6GXBqd6P7Tvehvrh8uor8vwaUYUWSe6SMEH7b5xD7xBGOxrzXlhtDmHriNDUVp26opx05kFciOk0CN8ecBXi1meouC1SLRo0_qCLyDVReE4mt15LTHgPgZiA4OwqQDYwF7PvBrAqMPbGE_twg0_f1fq_kiHbPkfciNwmwzixNoXXeAgSWF-Hg4-xN6zAi5ROHZf5ZtEeTh3ds2eyEN5nnS64PRpW0cWw6PmoYCjsXjKPoLgmKp4hMdN-d7rC9FkFa47yxCa4F8iDYhcJIjS7xgTmsfbJ0Rdvo_IqkwO-bo5W3bN1bjXy5GFKYBrNGoVxhNsbANqsSQ0UC9fOv6Y2RnT5RfaNLn25a_3jUg69y3S7QgT57zAzMniyjILKO-qcAuWSDomASUlg2IRpSv-x-1b8kyyS1zJI8iHRxJeLuKo_yxUB3PnOPUxNlTqj_-Bm00)

#### 5.4.3 US 9 — Gestione del timer a scacchi (turno con timeout)

Il diagramma illustra il flusso di un turno con la modalità a tempo attiva, incluso il caso di esaurimento del tempo.

![Diagramma di Sequenza – US 9 Timer a Scacchi](https://www.plantuml.com/plantuml/png/bLF1RY8n3BtFLrWzjTBs1pYiAZYK2uUL41n78N718eb7ZWFjtzSpG66dTAKzZ1JvFJ-_vsHUYZhHcc9JzfGx9ox1nldzLhZcCEF80iSTAJQ6ANdgN5Puc2mSvHbd5OuHvG5SWSLin7br2PUKpl3hSWJ_gImKM5Q4nu6n-e4mPITXO4n7Z3NbkSlXuc0zRvh539v_sp2Om12jrIhvqLSHpDfsqNsWF3NEAnsSOc_wwsmEcyZS0MypWISV6GA1hQLg0t2ZJAN5zuu4mpTbw1dFHZJw13RCqKekAYYcZg5u5wgorVuIBChToUdJ00MyTNKbJusBaH9bWyupxrYuq5Uzz8wFhTerSDKsSYd_uA_drk1twFVjaVBZfb_y2JVaAvH16SNA60kUSsNETxBrymELVb0xYDrAPhPqGjkT0hzPm-Gi9LWeL8O35TfGn95U9vmwRHCVy6wIrTMevsIlWqVxCm6FfTnJ-7LfEKbDhr9BgVY_buOvDFrtKxVdzc8b-zy-0G00)

#### 5.4.4 US 11 — Replay della partita

Il diagramma mostra la navigazione mossa per mossa durante il replay.

![Diagramma di Sequenza – US 11 Replay della Partita](https://www.plantuml.com/plantuml/png/fPD1Rzim38Nl-XM4JWcsOjWrXw503il5MrOKlXgCnIL4PT6JvBJPhn-jL5bG14E17GpGqlSUdoZxFcMCUHgyIKySHemum0xxftsKARYrU8dmVE1C1lkijVtAqgDMP04JR8rAClSyOiXWLmroM4l8KRodM91c_OPveD7ZQOF1LUHXymRvCKba9x5bUYv4QqopXhilYi8AUaavJfnwWbZCm24qSgGD9urschFo4JFDpI-rTb5rzUXs4tlNfO1ZEaXEYyDP-n5sWj4j2wkmjbrf5tGdu-ZQotYH4G8UUO-_MKBDOW3EKLiLEaxpMbSy5xLPrqkC538j5RvujlhIpiAj2eVvY0YsaPGGli4dUFp-Q9NOLciRw2LRtR1Zf6CfVasSxTcb9kzbq46BBbwbdpkXpwyM-b8ZbydiAL_6ik3Ww0K-mETbmQw7KfbR-a4le-FmK_vbCEyhgGVKBVA9Ne_oZa1t_nlefi6DG7MarR1mcUB00VzUE0LdvkTgnlhbtUkI_bb_0000)

---

### 5.5 Decisioni di progetto commentate

**Perché Facade su QuoridorBoard?** La classe `QuoridorBoard` centralizza l'accesso al dominio per evitare che il controller (o la GUI) debbano conoscere l'esistenza di `MovementHandler` e `WallHandler`. Questo riduce l'accoppiamento tra i livelli e permette di modificare la struttura interna del dominio senza impattare i client.

**Perché composizione invece di ereditarietà?** Seguendo il secondo principio GoF, `QuoridorBoard` contiene istanze di `MovementHandler` e `WallHandler` piuttosto che estenderli. Questo consente di intercambiare le implementazioni degli handler a runtime se necessario (es. per una variante delle regole) senza modificare la gerarchia di classi.

**Perché ReplayHandler separato?** Separare la logica di replay in una classe dedicata rispetta il principio Single Responsibility e il principio DRY: sia la modalità CLI sia quella GUI possono utilizzare lo stesso `ReplayHandler` senza duplicare la logica di ricostruzione degli snapshot.

**Applicazione del principio di presentazione separata ai test.** Poiché le classi di dominio non dipendono dall'interfaccia utente, è stato possibile scrivere 61 casi di test per la logica CLI/dominio e 88 per la GUI utilizzando asserzioni testuali senza alcuna dipendenza da componenti grafici reali.

---

## 6. Riepilogo del Test

**Corso:** Ingegneria del Software — Prof. Filippo Lanubile  
**Metodologia:** Testing & V&V (classi di equivalenza, analisi dei valori limite, criteri white-box)

---

### Struttura dei file di test

| File | Modulo testato | Tipo |
|---|---|---|
| `test_quoridor.py` | `board`, `movement`, `wall`, `win_handler`, `history`, `timer`, `replay` | Unità + Integrazione (CLI) |
| `test_stopwatch.py` | `app._Stopwatch`, `app._fmt_seconds` | Unità (GUI) |
| `test_player_card.py` | `player_card.PlayerCard` | Unità (GUI) |
| `test_board_widget.py` | `board_widget.BoardWidget` | Unità (GUI) |
| `test_setup_screen.py` | `setup_screen.SetupScreen` | Unità (GUI) |
| `test_overlays.py` | `overlays.*` (WinnerOverlay, HistoryOverlay, NotificationOverlay, ReplayScreen) | Unità (GUI) |

**Totale casi di test: 168** (61 CLI + 107 GUI)

---

### Riepilogo per file

---

#### `test_quoridor.py` — Moduli CLI (61 test)

##### `TestQuoridorBoardInit` — Inizializzazione board
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC01 | P1 e P2 nelle posizioni iniziali corrette (2p) | EC valida | `[0,4]` / `[8,4]` |
| TC02 | Muri iniziali = 10 per giocatore (2p) | EC valida | `walls_left == 10` |
| TC03 | P3 e P4 nelle posizioni iniziali corrette (4p) | EC valida | `[4,0]` / `[4,8]` |
| TC04 | Muri iniziali = 5 per giocatore (4p) — valore limite inferiore | Valore limite | `walls_left == 5` |
| TC05 | Turno iniziale è P1 | EC valida | `turn == 1` |
| TC06 | Nessun muro posizionato all'inizio | EC valida | `h_walls`, `v_walls` vuoti |

##### `TestAdvanceTurn` — Rotazione del turno
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC07 | Turno avanza da P1 a P2 | EC valida | avanzamento normale |
| TC08 | Wrap-around: dopo P2 torna P1 — valore limite superiore | Valore limite | `turn == 1` |
| TC09 | Ciclo completo 4 giocatori (P2→P3→P4→P1) | EC valida | ciclo `1..4` |

##### `TestEliminatePlayer` — Eliminazione giocatore
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC10 | Eliminazione del giocatore corrente | EC valida | rimosso da `active_players` |
| TC11 | Doppia eliminazione non solleva eccezioni (idempotenza) | EC non valida | già assente |
| TC12 | `turn_index` si aggiusta dopo eliminazione | EC valida (white-box) | `turn == 2` |
| TC13 | Rimane un solo giocatore — valore limite | Valore limite | `active_players == [2]` |

##### `TestMovementValidCommands` — Movimenti validi
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC14 | Mossa adiacente verso il basso (`e2`) | EC valida | `[1,4]` |
| TC15 | Mossa adiacente verso destra (`f1`) | EC valida | `[0,5]` |
| TC16 | Mossa adiacente verso sinistra (`d1`) | EC valida | `[0,3]` |
| TC17 | La mossa fa avanzare il turno | EC valida | `turn == 2` |

##### `TestMovementInvalidCommands` — Movimenti non validi
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC18 | Comando troppo corto (1 carattere) | EC non valida | `len < 2` |
| TC19 | Comando troppo lungo (3 caratteri non-muro) | EC non valida | `len > 2` |
| TC20 | Colonna `<'a'` (fuori bordo sinistro) | EC non valida | `col < min` |
| TC21 | Colonna `>'i'` (`'j'`) | EC non valida | `col > max` |
| TC22 | Colonna minima `'a'` — distanza > 1 → rifiutata | Valore limite | `col == 'a'` |
| TC23 | Cella corrente (riga `'1'`) già occupata | Valore limite | destinazione == sorgente |
| TC24 | Riga `'0'` — fuori bordo | EC non valida | `row < min` |
| TC25 | Mossa a riga `'9'` con distanza > 1 | Valore limite | `row == '9'` |
| TC26 | Destinazione occupata da un avversario | EC non valida | cella occupata |
| TC27 | Mossa diagonale (non consentita) | EC non valida | mossa illegale |

##### `TestMovementJump` — Salto sopra avversario
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC28 | Salto valido con avversario adiacente | EC valida | `dist==2` + mid occupato |
| TC29 | Salto di 2 celle senza avversario in mezzo | EC non valida | mid libero |
| TC30 | Salto bloccato da muro tra P1 e il punto medio | EC non valida (white-box) | muro pre-mid |
| TC31 | Salto bloccato da muro tra punto medio e destinazione | EC non valida (white-box) | muro post-mid |

##### `TestWallBetween` — Funzione `_is_wall_between`
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC32 | Nessun muro orizzontale → `False` | EC valida | assenza muro |
| TC33 | Muro orizzontale blocca → `True` | EC valida | muro presente |
| TC34 | Nessun muro verticale → `False` | EC valida | assenza muro |
| TC35 | Muro verticale blocca → `True` | EC valida | muro presente |
| TC36 | Muro a offset -1 blocca ugualmente | Valore limite | `(r, c-1)` |
| TC37 | Celle non adiacenti → `False` | EC non valida | fuori logica muro |

##### `TestWallPlacementValid` — Piazzamento muri validi
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC38 | Muro orizzontale in posizione libera | EC valida | `h_walls` aggiornato |
| TC39 | Muro verticale in posizione libera | EC valida | `v_walls` aggiornato |
| TC40 | Il piazzamento decrementa il contatore muri | EC valida | `walls_left -= 1` |
| TC41 | Il piazzamento fa avanzare il turno | EC valida | `turn == 2` |
| TC42 | Ultima colonna valida per muro (`'h'`) | Valore limite | `col == 'h'` |
| TC43 | Ultima riga valida per muro (`'8'`) | Valore limite | `row == '8'` |

##### `TestWallPlacementInvalid` — Piazzamento muri non validi
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC44 | Colonna `'i'` (fuori bordo) | EC non valida | `col > 'h'` |
| TC45 | Riga `'9'` (fuori bordo) | EC non valida | `row > '8'` |
| TC46 | Sovrapposizione su posizione già occupata | EC non valida | `(r,c)` occupato |
| TC47 | Incrocio tra muro orizzontale e verticale | EC non valida | cross h/v |
| TC48 | Nessun muro rimasto | EC non valida | `walls_left == 0` |
| TC49 | Sovrapposizione offset +1 | Valore limite | `(r, c+1)` occupato |
| TC50 | Sovrapposizione offset -1 | Valore limite | `(r, c-1)` occupato |

##### `TestWinHandler` — Condizioni di vittoria
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC51 | Nessun vincitore a inizio partita | EC non valida | `winner == 0` |
| TC52 | P1 vince esattamente a riga 8 | Valore limite | `row == 8` |
| TC53 | P1 a riga 7 NON ha vinto | Valore limite | `row == 7` |
| TC54 | P2 vince esattamente a riga 0 | Valore limite | `row == 0` |
| TC55 | P2 a riga 1 NON ha vinto | Valore limite | `row == 1` |
| TC56 | P3 vince a colonna 8 (4p) | EC valida | `col == 8` |
| TC57 | P4 vince a colonna 0 (4p) | EC valida | `col == 0` |
| TC58 | Ultimo giocatore rimasto vince (4p) | EC valida | `len(active) == 1` |
| TC59 | P1 vince anche in modalità 4 giocatori | EC valida | `row == 8` |

##### `TestMoveHistory` — Cronologia mosse
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC60 | Registrazione di una mossa semplice | EC valida | `type == "spostamento"` |
| TC61 | Registrazione muro orizzontale | EC valida | `type == "muro"` |
| TC62 | Registrazione muro verticale | EC valida | `type == "muro"` |
| TC63 | Registrazione pseudo-mossa "abbandono" | EC valida | `type == "abbandono"` |
| TC64 | Registrazione pseudo-mossa "timeout" | EC valida | `type == "timeout"` |
| TC65 | Numerazione turni progressiva | EC valida (white-box) | `turn == "1"`, `"2"` |
| TC66 | Storia vuota restituisce lista vuota | Valore limite | `moves == []` |

##### `TestGameTimer` — Timer a scacchi
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC67 | Tempo iniziale corretto per entrambi i giocatori | EC valida | `time_left == 300.0` |
| TC68 | Tempo diminuisce dopo `stop_turn` | EC valida | `time_left < 300` |
| TC69 | `get_remaining` durante il turno è < iniziale | EC valida (white-box) | turno in corso |
| TC70 | Tempo = 0 → `is_expired` è `True` | Valore limite | `remaining == 0` |
| TC71 | Tempo > 0 → `is_expired` è `False` | EC non valida | `remaining > 0` |
| TC72 | `remove_player` elimina la voce | EC valida | `1 not in time_left` |
| TC73 | `stop_turn` senza `start_turn` non solleva errori | EC non valida | stato `None` |
| TC74 | `remove_player` del giocatore attivo azzera lo stato | EC valida (white-box) | `_active == None` |
| TC75 | Il tempo non scende sotto 0 | Valore limite | `time_left == 0.0` |

##### `TestReplayHandler` — Ricostruzione snapshot
| ID | Descrizione | Criterio | Classe |
|---|---|---|---|
| TC76 | `total_moves` corrisponde al numero di mosse | EC valida | `total == 2` |
| TC77 | Snapshot 0 è la posizione iniziale | Valore limite | `positions[1] == [0,4]` |
| TC78 | Snapshot 1 riflette la prima mossa | EC valida | `positions[1] == [1,4]` |
| TC79 | `get_move_info(0)` restituisce `None` | Valore limite | indice 0 |
| TC80 | `get_move_info(1)` restituisce la prima mossa | EC valida | `command == "e2"` |
| TC81 | Pseudo-mossa "abbandono" elimina il giocatore | EC valida | `1 not in active` |
| TC82 | Pseudo-mossa "timeout" elimina il giocatore | EC valida | `2 not in active` |
| TC83 | Lista mosse vuota → solo snapshot iniziale | Valore limite | `total == 0` |

##### `TestIntegrationFullGame` — Test di integrazione
| ID | Descrizione | Criterio |
|---|---|---|
| TC84 | P1 percorre la colonna centrale e vince | Integrazione (Board+WinHandler) |
| TC85 | Un muro piazzato blocca il passaggio dell'avversario | Integrazione (Wall+Movement) |
| TC86 | La storia registra tutte le mosse nell'ordine corretto | Integrazione (Board+History) |
| TC87 | Il replay ricostruisce correttamente il piazzamento dei muri | Integrazione (Replay+Wall) |
| TC88 | Il timer si azzera per il giocatore eliminato | Integrazione (Board+Timer+WinHandler) |
| TC89 | Eliminazione progressiva in 4p funziona correttamente | Integrazione (4p mode) |
| TC90 | `process_move` smista correttamente a Wall vs Movement | Integrazione (Board dispatcher) |

---

#### `test_stopwatch.py` — `_Stopwatch` e `_fmt_seconds` (19 test)

##### `TestFmtSeconds`
| ID | Descrizione | Criterio | Input → Output |
|---|---|---|---|
| TC91 | Valore tipico 65 s | EC valida | `65.0` → `"01:05"` |
| TC92 | Zero secondi | Valore limite | `0.0` → `"00:00"` |
| TC93 | Valore negativo → trattato come 0 | EC non valida | `-5.0` → `"00:00"` |
| TC94 | Esattamente 60 s | Valore limite | `60.0` → `"01:00"` |
| TC95 | 599 s | Valore limite | `599.0` → `"09:59"` |
| TC96 | Troncamento (non arrotondamento) | EC valida (white-box) | `59.9` → `"00:59"` |

##### `TestStopwatchInit`
| ID | Descrizione | Criterio |
|---|---|---|
| TC97 | Elapsed iniziale = 0 per tutti i giocatori | EC valida |
| TC98 | 4 giocatori tutti a 0 | EC valida |
| TC99 | Giocatore inesistente → 0 (fallback dict.get) | EC non valida |

##### `TestStopwatchTiming`
| ID | Descrizione | Criterio |
|---|---|---|
| TC100 | Elapsed aumenta dopo `stop_turn` | EC valida |
| TC101 | `get_elapsed` durante il turno tiene conto del tempo corrente | EC valida (white-box) |
| TC102 | Il giocatore inattivo non accumula tempo | EC non valida |
| TC103 | `stop_turn` senza `start_turn` non solleva errori | EC non valida |
| TC104 | Doppio `start_turn` accumula entrambi i giocatori | Valore limite |

##### `TestStopwatchRemovePlayer`
| ID | Descrizione | Criterio |
|---|---|---|
| TC105 | `remove_player` elimina la voce elapsed | EC valida |
| TC106 | `remove_player` del giocatore attivo azzera lo stato | EC valida (white-box) |
| TC107 | `remove_player` di giocatore assente non solleva errori | EC non valida |

---

#### `test_player_card.py` — `PlayerCard` (21 test)

##### `TestPlayerCardInit`
| ID | Descrizione | Criterio |
|---|---|---|
| TC108 | Attributi di default dopo `__init__` | EC valida |
| TC109 | 4 giocatori con 5 muri | EC valida |
| TC110 | `max_seconds=0` → usa default 300 | Valore limite |
| TC111 | `timed=True` → campo `timed` corretto | EC valida |
| TC112 | `_remaining_s` iniziale = `max_seconds` (barra al 100%) | Valore limite |

##### `TestPlayerCardUpdateState`
| ID | Descrizione | Criterio |
|---|---|---|
| TC113 | Aggiornamento standard dei campi | EC valida |
| TC114 | `is_turn=True` aggiunge classe CSS `-active` | EC valida (white-box) |
| TC115 | `is_turn=False` rimuove classe `-active` | EC valida (white-box) |
| TC116 | `is_eliminated=True` aggiunge classe `-eliminated` | EC valida (white-box) |
| TC117 | `is_eliminated=False` rimuove `-eliminated` | EC valida (white-box) |
| TC118 | Eliminato + `is_turn=True` → `-active` NON aggiunta | EC non valida (white-box) |
| TC119 | `remaining_seconds >= 0` aggiorna `_remaining_s` | EC valida |
| TC120 | `remaining_seconds = -1` → `_remaining_s` non cambia | EC non valida |

##### `TestPlayerCardRender`
| ID | Descrizione | Criterio |
|---|---|---|
| TC121 | Render contiene nome giocatore (`P1`) | EC valida |
| TC122 | Render eliminato contiene `"eliminato"` | EC valida (white-box) |
| TC123 | Render con turno attivo contiene `"TURNO"` | EC valida (white-box) |
| TC124 | Render senza `timed` NON mostra il timer | EC non valida |
| TC125 | Render con `timed=True` mostra il testo del timer | EC valida |
| TC126 | 0 muri → barra completamente vuota | Valore limite |
| TC127 | `remaining=0` → barra timer a 0% (20 blocchi vuoti) | Valore limite |
| TC128 | `remaining=max` → barra timer al 100% (20 blocchi pieni) | Valore limite |

---

#### `test_board_widget.py` — `BoardWidget` (26 test)

##### `TestLayoutConstants`
| ID | Descrizione | Criterio |
|---|---|---|
| TC129 | `COL_CYCLE == CELL_W + GUTTER` | EC valida |
| TC130 | `ROW_CYCLE == CELL_H + GUTTER` | EC valida |
| TC131 | `BOARD_W == 9*CELL_W + 8*GUTTER` | EC valida |
| TC132 | `BOARD_H == 9*CELL_H + 8*GUTTER` | EC valida |

##### `TestIsJumpMove`
| ID | Descrizione | Criterio |
|---|---|---|
| TC133 | Salto con avversario in mezzo → `True` | EC valida |
| TC134 | Distanza 1 → non è un salto | EC non valida |
| TC135 | Distanza 2 diagonale → non è un salto | EC non valida |
| TC136 | Distanza 2, cella intermedia libera → `False` | EC non valida |
| TC137 | Distanza 3 → `False` | EC non valida |

##### `TestMouseToTarget`
| ID | Descrizione | Criterio |
|---|---|---|
| TC138 | Click su cella `[0,0]` | EC valida |
| TC139 | Click su gutter orizzontale riga 0 | EC valida |
| TC140 | Click su gutter verticale colonna 0 | EC valida |
| TC141 | Click fuori bordo sinistro → `None` | EC non valida |
| TC142 | Click fuori bordo superiore → `None` | EC non valida |
| TC143 | Click fuori bordo destro → `None` | EC non valida |
| TC144 | Click fuori bordo inferiore → `None` | EC non valida |
| TC145 | Click esatto su `LABEL_LEFT, LABEL_TOP` → `(cell, 0, 0)` | Valore limite |
| TC146 | Click su cella `[8,8]` (ultima cella) | Valore limite |

##### `TestWallValid`, `TestGoalColors`, `TestCellBackground`, `TestBoardWidgetStateChanges`
| ID | Descrizione | Criterio |
|---|---|---|
| TC147 | Muro h/v valido in posizione libera | EC valida |
| TC148 | Muro h/v non valido su posizione occupata | EC non valida |
| TC149 | Muro non valido senza muri rimasti | EC non valida |
| TC150 | Muro riga/colonna limite (7 = max, 8 = fuori) | Valore limite |
| TC151-154 | Colori righe/colonne obiettivo (P1 r8, P2 r0, P3 c8, P4 c0) | EC valida (white-box) |
| TC155 | Colore riga obiettivo con giocatore eliminato → `None` | EC non valida |
| TC156 | In 2 giocatori le colonne non hanno colore | EC non valida |
| TC157 | Cella normale → `CELL_BG` | EC valida |
| TC158 | Cella hover raggiungibile → `HOVER_CELL_BG` | EC valida (white-box) |
| TC159 | Hover su cella non raggiungibile → `CELL_BG` | EC non valida |
| TC160 | Hover in modalità `hwall` → sfondo cella invariato | EC non valida |
| TC161-164 | `set_board`, `set_mode`, `recompute_reachable` aggiornano lo stato | EC valida |

---

#### `test_setup_screen.py` — `SetupScreen` (17 test)

##### `TestSetupScreenInit`
| ID | Descrizione | Criterio | Default atteso |
|---|---|---|---|
| TC165 | 2 giocatori di default | EC valida | `_num_players == 2` |
| TC166 | Timer disattivato di default | EC valida | `_timed == False` |
| TC167 | 5 minuti di default | EC valida | `_minutes == 5` |

##### `TestSetupScreenSubmitLogic`
| ID | Descrizione | Criterio |
|---|---|---|
| TC168 | `timed=False` → `minutes` irrilevante | EC non valida |
| TC169 | Selezione 4 giocatori aggiorna `_num_players` | EC valida |
| TC170 | Attivazione timer aggiorna `_timed` | EC valida |
| TC171 | Minuti validi (intero positivo) | EC valida |
| TC172 | 1 minuto (minimo accettabile) | Valore limite |
| TC173 | `"0"` minuti → usa default 5 | EC non valida |
| TC174 | Stringa non numerica → usa default 5 | EC non valida |
| TC175 | Stringa vuota → usa default 5 | EC non valida |
| TC176 | Config con `timed=False` → `minutes=0` | EC valida |
| TC177 | Config completo con `timed=True` | EC valida |

##### `TestSetupScreenVisibility`
| ID | Descrizione | Criterio |
|---|---|---|
| TC178 | `timed=True` → campo minuti visibile | EC valida |
| TC179 | `timed=False` → campo minuti nascosto | EC valida |
| TC180 | Toggle on→off→on mantiene stato | Valore limite |

---

#### `test_overlays.py` — Overlay modali (24 test)

##### `TestWinnerOverlay`
| ID | Descrizione | Criterio |
|---|---|---|
| TC181 | `winner=1`, `reason="vittoria"` | EC valida |
| TC182 | `winner=4`, `reason="timeout"` | EC valida |
| TC183 | `reason="abbandono"` | EC valida |
| TC184 | Colori disponibili per P1–P4 | EC valida |
| TC185 | `winner=99` → colore fallback `"#ffffff"` | EC non valida |
| TC186 | `winner=1` e `winner=4` (valori limite) | Valore limite |

##### `TestHistoryOverlay`
| ID | Descrizione | Criterio |
|---|---|---|
| TC187 | Lista mosse non vuota | EC valida |
| TC188 | Lista mosse vuota | Valore limite |
| TC189 | Estrazione numero giocatore da `"P1"` | EC valida (white-box) |
| TC190 | Tipo di mossa sconosciuto non solleva errori | EC non valida |
| TC191 | Colori disponibili per tutti i giocatori validi | EC valida |

##### `TestNotificationOverlay`
| ID | Descrizione | Criterio |
|---|---|---|
| TC192 | Titolo e corpo memorizzati correttamente | EC valida |
| TC193 | Markup Rich nel titolo | EC valida |
| TC194 | Titolo e corpo vuoti | Valore limite |
| TC195 | Corpo multi-riga | EC valida |

##### `TestReplayScreen`
| ID | Descrizione | Criterio |
|---|---|---|
| TC196 | Inizializzazione 2 giocatori | EC valida |
| TC197 | Inizializzazione 4 giocatori | EC valida |
| TC198 | Lista mosse vuota | Valore limite |
| TC199 | Indice iniziale = 0 | Valore limite |
| TC200 | `action__next` incrementa l'indice | EC valida |
| TC201 | `action__next` non supera il totale | Valore limite |
| TC202 | `action__prev` decrementa l'indice | EC valida |
| TC203 | `action__prev` non scende sotto 0 | Valore limite |
| TC204 | `_info_text` a indice 0 → `"Posizione iniziale"` | Valore limite |
| TC205 | `_info_text` a indice 1 mostra il comando | EC valida |
| TC206 | Snapshot accessibile per ogni indice valido | EC valida |
| TC207 | Snapshot 0 = posizione iniziale | Valore limite |
| TC208 | Snapshot ultimo = ultima mossa applicata | Valore limite |

---

### Conteggio totale

| File | # Test | Tipo prevalente |
|---|---|---|
| `test_quoridor.py` | 61 | Unità + Integrazione |
| `test_stopwatch.py` | 19 | Unità |
| `test_player_card.py` | 21 | Unità |
| `test_board_widget.py` | 26 | Unità |
| `test_setup_screen.py` | 17 | Unità |
| `test_overlays.py` | 24 | Unità |
| **Totale** | **168** | |

---

### Criteri di copertura applicati

| Criterio | Applicato in |
|---|---|
| Classi di equivalenza valide | Tutti i file |
| Classi di equivalenza non valide | Tutti i file |
| Analisi dei valori limite | Tutti i file |
| Copertura istruzioni / branch (white-box) | `test_quoridor`, `test_board_widget`, `test_player_card` |
| Test di integrazione (incrementale) | `TestIntegrationFullGame` |
| Oracolo automatico (assert) | Tutti i file |

---

## 7. Modalità di Collaborazione del Team

Questa sezione descrive gli strumenti, le regole e i processi adottati dal team durante lo Sprint 2.

### 7.1 Versionamento del Codice e Flusso di Lavoro

Il codice sorgente è ospitato su **GitHub**. Per la gestione dei branch abbiamo adottato una strategia basata su **feature branch**: ogni funzionalità o correzione viene sviluppata su un branch dedicato (es. `feature/gui-timer`, `fix/wall-validation`) e poi integrata su `main` tramite **Pull Request**. Il merge su `main` è consentito solo dopo almeno un'approvazione esplicita da parte di un altro componente del team, garantendo una forma strutturata di code review. Per i messaggi di commit abbiamo adottato la convenzione `tipo: descrizione breve` (es. `feat: aggiunge replay handler`, `fix: corregge wrap-around turno`), in modo da rendere la cronologia del repository leggibile e filtrabile. Ogni Pull Request deve contenere il riferimento `Closes #Numeroissue` per collegare automaticamente l'issue corrispondente e mantenere la tracciabilità tra lavoro pianificato e lavoro consegnato.

### 7.2 Gestione dei Task e Avanzamento Lavori

Per la gestione dei task abbiamo utilizzato la **GitHub Projects board** integrata nel repository, configurata con i cinque stati concordati: *To Do*, *In Progress*, *Review*, *Ready*, *Done*. Il processo di assegnazione è stato guidato dal Team Leader, il quale ha distribuito le diverse issue a ciascun componente del gruppo. La ripartizione è stata effettuata in modo strategico, valutando attentamente le competenze specifiche di ogni membro e il relativo carico di lavoro, così da garantire un'equa e ottimale gestione del progetto. Lo stato *Ready* viene impostato quando il lavoro è completato e in attesa del feedback del docente; lo stato *Done* viene aggiornato solo dopo la validazione formale. Ogni issue rimane aperta finché il branch collegato non è stato mergiato e chiuso.

### 7.3 Comunicazione e Rituali

La comunicazione principale avviene in presenza, incontrandoci tramite accordo, in luoghi comuni (come bar, uffici o a casa) per sessioni di lavoro condiviso e allineamento diretto. Per il coordinamento e il lavoro non in presenza, ci affidiamo a canali digitali: utilizziamo una chat vocale su Discord per le sessioni di sviluppo e confronto a distanza, e un gruppo WhatsApp dedicato al progetto per gli aggiornamenti rapidi, la condivisione di link e la segnalazione di blocchi. Non adottiamo cerimonie formali come i daily scrum, poiché questa impostazione mista tra presenza e canali agili si adatta perfettamente alle dimensioni del nostro team, mantenendo la comunicazione fluida, leggera ed efficace.

### 7.4 Condivisione della Documentazione

La documentazione di progetto (incluso questo report) viene redatta direttamente in Markdown all'interno del repository GitHub, nella cartella /docs/. Questo approccio permette di versionare la documentazione insieme al codice, mantenere la cronologia delle modifiche e facilitare le revisioni tramite Pull Request. Per la stesura di testi più elaborati, come ad esempio questo stesso report, utilizziamo VS Code come strumento intermedio per visualizzare e formattare al meglio il contenuto in anteprima, per poi trasferire e committare il file Markdown finale sul repository.

---

## 8. Analisi Retrospettiva

 
### 8.1 Sprint 0
 
Lo Sprint 0 si è svolto dal **30 marzo al 10 aprile**, con feedback ricevuto il **21–22 aprile**. L'obiettivo era dimostrare familiarità con Git, GitHub Flow e il processo agile, attraverso task individuali auto-assegnati e completati seguendo il GitHub Flow. Di seguito la retrospettiva strutturata secondo il framework Keep / Drop / Learn / Improve.
 
---
 
#### 8.1.1 Keep – Cosa ha funzionato
 

- **Workflow**: La suddivisione del backlog in issue individuali auto-assegnate ha permesso a ogni componente del team di avere un'area di responsabilità chiara fin dall'avvio dello sprint. Tutti i membri hanno registrato almeno un commit a proprio nome, rispettando il vincolo minimo previsto dall'obiettivo.
- Il processo di approvazione delle pull request (merge consentito solo con almeno un'approvazione esplicita da un altro componente) ha introdotto una prima forma strutturata di code review, riducendo il rischio di modifiche non verificate su `main`.
- **Tooling**: La project board con i 5 stati (To Do / In Progress / Review / Ready / Done) ha fornito visibilità immediata sullo stato delle attività durante lo sprint, rendendo facilmente identificabili i task bloccati o non ancora presi in carico.
- **Comunicazione**: L'annuncio dell'esito sul canale `#consegne` con il messaggio concordato ha standardizzato la comunicazione verso il docente, evitando ambiguità sulla consegna.
---
 
#### 8.1.2 Drop – Cosa non ha funzionato
 
**Processi**
- Le pull request non erano collegate alle rispettive issue tramite riferimento esplicito (`Closes #N`), rendendo impossibile ricostruire automaticamente la tracciabilità tra lavoro pianificato e lavoro consegnato. Questo ha obbligato a verifiche manuali durante il feedback.
- Gli issue non si sono fermati sullo stato **Ready** come previsto dalle istruzioni: lo stato Done è stato utilizzato prima del feedback del docente, saltando un passaggio esplicito del flusso concordato.
**Gestione**
- La milestone dello Sprint 0 è stata aperta priva di descrizione degli obiettivi e delle modalità di lavoro, vanificando il suo ruolo di riferimento condiviso per il team.
- Diversi branch sono rimasti aperti al termine dello sprint senza essere stati né mergiati né chiusi, appesantendo inutilmente il repository e rendendo difficile distinguere il lavoro completato da quello abbandonato.
**Tecnica**
- Il messaggio di commit `Update main.py` non descriveva le modifiche effettive, rendendo la cronologia del repository non leggibile né filtrabile. Trattandosi di un problema **major** segnalato nel feedback, indica l'assenza di una convenzione condivisa sui messaggi di commit fin dall'inizio dello sprint.
- La cartella `img` conteneva immagini non utilizzate nella guida, mentre alcune immagini citate nel testo risultavano mancanti. I percorsi errati hanno inoltre reso le figure non visualizzabili su GitHub, classificato come problema **major** nel feedback ricevuto.
---
 
#### 8.1.3 Learn – Lezioni apprese
 
**Pianificazione**
- L'obiettivo dello Sprint 0 era prevalentemente procedurale (familiarizzare con Git e GitHub Flow), ma il team ha trattato i task come semplici modifiche tecniche, trascurando gli aspetti di processo (tracciabilità, stato delle issue, descrizione delle milestone). La qualità del repository non dipende solo dal contenuto dei file, ma dalla correttezza del flusso di lavoro che li produce.
**Tecnologia / Tooling**
- GitHub non collega automaticamente PR e issue: senza il riferimento esplicito `Closes #N` nel corpo della pull request, la tracciabilità va persa e la project board non riflette lo stato reale del lavoro. Questo meccanismo non era noto a tutto il team prima dello sprint.
- La visualizzazione delle immagini Markdown su GitHub dipende dalla correttezza dei percorsi relativi: un percorso valido in locale può risultare rotto nel repository remoto se la struttura delle cartelle differisce. È necessario verificare sempre la visualizzazione direttamente su GitHub prima del merge.
**Gestione**
- La milestone senza descrizione ha reso lo sprint privo di un riferimento scritto sugli obiettivi e sui criteri di completamento. In assenza di questo riferimento, ogni componente del team ha interpretato autonomamente le priorità, generando disomogeneità nel risultato finale.
---
 
#### 8.1.4 Improve – Azioni correttive per il prossimo sprint
 
| # | Problema di origine | Azione concreta | Responsabile |
|---|---|---|---|
| 1 | Commit non descrittivo (major) | Adottare obbligatoriamente il formato `tipo: descrizione breve` (es. `docs: aggiorna guida configurazione repo`) per ogni commit su qualsiasi branch. | Tutto il team |
| 2 | Immagini disallineate (major) | Prima di aprire ogni PR che modifica file Markdown o la cartella `img`, verificare la visualizzazione della pagina direttamente su GitHub e allegare uno screenshot nella descrizione della PR come prova | Autore della PR |
| 3 | PR non collegate alle issue | Inserire obbligatoriamente `Closes #N` nel corpo di ogni pull request. La PR non può essere approvata né mergiata senza questo riferimento: aggiungerlo come voce esplicita nel template di PR | Reviewer |
| 4 | Branch aperti abbandonati | Entro l'ultimo giorno di ogni sprint, chiudere o mergiare tutti i branch aperti. Eventuali branch ancora attivi devono avere una issue aperta collegata che ne giustifichi la sopravvivenza | Team lead |
| 5 | Milestone senza descrizione | Compilare la descrizione della milestone prima di creare il primo issue dello sprint, includendo: obiettivo, modalità di lavoro, criteri di completamento e data di scadenza | Team lead |
| 6 | Issue non in stato Ready a fine sprint | Prima della consegna, verificare che tutti gli issue completati siano nello stato **Ready** sulla project board; lo stato **Done** va aggiornato solo dopo il feedback del docente | Tutto il team |
 
---
 
### 8.2 Sprint 1
 
Lo Sprint 1 ha approfondito la modellazione e la definizione dei requisiti di progetto, facendo seguito allo Sprint 0. L'obiettivo era consolidare l'uso delle metodologie agili, perfezionare il flusso di lavoro su GitHub e applicare rigorosamente la notazione UML per la progettazione del sistema. Di seguito la retrospettiva strutturata secondo il framework Keep / Drop / Learn / Improve.
 
---
 
#### 8.2.1 Keep – Cosa ha funzionato
 
- **Workflow**: La suddivisione del lavoro per issue individuali, ereditata dallo Sprint 0, ha continuato a garantire un'area di responsabilità chiara per ogni componente del team, riducendo la sovrapposizione tra task paralleli.
- **Tooling**: La project board a 5 stati (To Do / In Progress / Review / Ready / Done) ha mantenuto il suo ruolo di strumento principale per la visibilità dell'avanzamento, anche se il suo utilizzo metodologico richiede un irrobustimento negli sprint successivi.
- **Comunicazione**: L'organizzazione del team e la sua relativa comunicazione hanno permesso di svolgere lo sprint con fluidità e precisione.

---
 
#### 8.2.2 Drop – Cosa non ha funzionato
 
**Processi**
- Lo Sprint 0 non è stato formalmente chiuso prima dell'avvio dello Sprint 1: la sovrapposizione tra le due milestone ha generato disordine nella gestione delle issue e reso difficile valutare lo stato reale di avanzamento del progetto.
- Le issue dello Sprint 1 sono state spostate direttamente nello stato **Done** senza transitare per lo stato **Ready**, saltando il passaggio di validazione formale previsto prima del feedback del docente.
- L'11 maggio si è registrata un'assenza totale di partecipazione da parte di tutti i componenti del team, interrompendo il flusso di lavoro per l'intera giornata senza alcuna comunicazione preventiva.
**Gestione**
- La retrospettiva prodotta per lo Sprint 1 si è limitata a elencare azioni correttive per gli errori tecnici segnalati nella review dello Sprint 0, senza analizzare l'andamento del processo organizzativo, la comunicazione interna o i colli di bottiglia del team. Questo ha reso la retrospettiva di fatto un changelog, non uno strumento di miglioramento.
**Tecnica**
- I requisiti funzionali sono stati redatti ignorando il template standard delle User Story, producendo requisiti non conformi al formato agile concordato.
- I requisiti non funzionali inseriti differivano da quelli precedentemente concordati e comunicati, introducendo incoerenza nella documentazione di progetto.
- La sezione testuale dedicata al Modello di Dominio descriveva in realtà l'architettura software del sistema, confondendo i livelli di astrazione: si tratta di un problema **major** che compromette la qualità della progettazione.
- Il diagramma delle classi concettuale del dominio era completamente assente: mancava la rappresentazione diagrammatica del modello di dominio, classificata come problema **major** nel feedback ricevuto.
- Il diagramma dei package includeva elementi estranei e non conformi alla notazione UML ufficiale.
- Il diagramma dei componenti ricalcava il diagramma dei package senza utilizzare la corretta notazione formale UML, duplicando una vista già esistente invece di aggiungerne una nuova — problema **major**.
---
 
#### 8.2.3 Learn – Lezioni apprese
 
**Pianificazione**
- Gli sprint devono avere confini temporali e formali netti: non è possibile lavorare sullo Sprint 1 mantenendo aperta la milestone dello Sprint 0. La sovrapposizione genera ambiguità sullo stato del progetto e rende il feedback del docente difficile da contestualizzare.
- Il calendario di disponibilità del team deve essere definito a inizio sprint e non lasciato implicito: una giornata a presenza zero — senza comunicazione preventiva — è un rischio di progetto evitabile con una pianificazione minima.
**Tecnologia / Tooling**
- Lo stato **Ready** sulla project board ha un significato preciso: indica il materiale pronto per la revisione del docente. Il passaggio a **Done** deve avvenire esclusivamente dopo il feedback e l'approvazione formale, non appena il lavoro è tecnicamente completato dal team.
**Gestione**
- La retrospettiva non è un changelog tecnico: è uno strumento di ispezione del flusso di lavoro e di adattamento del team. Limitarsi a elencare i bug corretti significa ignorare le cause organizzative dei problemi, che tendono a ripresentarsi invariati nello sprint successivo.
**Modellazione UML**
- Il modello di dominio e l'architettura software operano su livelli di astrazione distinti e rispondono a domande diverse: il primo descrive i concetti del mondo reale e del problema (prospettiva concettuale), il secondo la soluzione tecnologica e la struttura del software. Produrre un diagramma dei componenti identico a quello dei package non aggiunge informazione, ma dimostra l'assenza di comprensione della differenza tra le due viste.
- I diagrammi UML (Package, Componenti, Classi) seguono una grammatica formale rigida: ogni tipo di diagramma ha elementi, relazioni e regole sintattiche proprie. Includere elementi non standard in un diagramma dei package non è una scelta stilistica, ma una violazione della specifica.
---
 
#### 8.2.4 Improve – Azioni correttive per il prossimo sprint
 
| # | Problema di origine | Azione concreta | Responsabile |
|---|---|---|---|
| 1 | Modello di dominio descritto come architettura **(major)** | Riscrivere la sezione testuale focalizzandosi esclusivamente sui concetti del dominio; produrre il diagramma delle classi con prospettiva concettuale | Team Lead / Analisti |
| 2 | Diagramma dei componenti clone del package **(major)** | Ridisegnare entrambi i diagrammi separando nettamente le due viste e rispettando la sintassi formale UML per ciascuna | Autore della PR / Progettisti |
| 3 | Diagramma delle classi concettuale assente **(major)** | Creare il diagramma mancante prima dell'apertura della PR di consegna; inserirlo come checklist obbligatoria nel template di PR | Analisti |
| 4 | Requisiti funzionali fuori template | Riformulare tutti i requisiti funzionali nel formato agile standard | Analisti |
| 5 | Requisiti non funzionali disallineati | Revisionare la lista dei requisiti non funzionali per riallinearla a quella ufficialmente comunicata; aggiungere una voce di verifica nel template di PR | Reviewer |
| 6 | Issue passate direttamente a Done | Bloccare lo spostamento a **Done** prima del feedback: ogni issue deve sostare in **Ready** fino alla validazione formale del docente | Tutto il team |
| 7 | Sprint 0 non chiuso formalmente | Chiudere immediatamente la milestone dello Sprint 0 su GitHub; verificare che nessuna issue rimanga aperta su sprint già conclusi | Team Lead |
| 8 | Assenza totale di partecipazione l'11 maggio | Definire a inizio sprint un calendario di disponibilità vincolante; comunicare preventivamente sul canale del team qualsiasi indisponibilità | Tutto il team |
| 9 | Retrospettiva limitata ai fix tecnici | Condurre la retrospettiva analizzando metriche di processo (PR chiuse, tempo medio di merge, issue bloccate), comunicazione interna e colli di bottiglia organizzativi — non solo gli errori tecnici segnalati | Tutto il team |
