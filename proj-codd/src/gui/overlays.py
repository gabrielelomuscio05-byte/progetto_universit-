"""Overlay modali: Aiuto, Cronologia, Vittoria, Replay.

Tutti gli overlay sono `ModalScreen` di Textual: si sovrappongono alla
GameScreen con sfondo semi-trasparente scuro e non consumano il turno
del giocatore corrente (chi era di turno prima dell'apertura resta
di turno alla chiusura — la chiusura non chiama mai `process_move`).

Le funzionalità testuali (titoli, etichette, descrizioni dei comandi)
sono ispirate a `view.py` per equivalenza CLI ↔ GUI, ma il layout
visivo è completamente diverso.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static

from src.gui.board_widget import PLAYER_COLORS_HEX, BoardWidget
from src.replay import ReplayHandler

# ============================================================
# Aiuto — overlay testuale con guida ai comandi e alle regole
# ============================================================

class HelpOverlay(ModalScreen):
    """Mostra le istruzioni di gioco. Equivalente GUI del comando `help`."""

    BINDINGS = [("escape", "dismiss", "Chiudi")]
    CSS_PATH = None

    def compose(self) -> ComposeResult:
        with Container(classes="overlay-card"):
            yield Static("◆ GUIDA AI COMANDI ◆", classes="overlay-title")
            with VerticalScroll(classes="overlay-content"):
                yield Static(self._help_text())
            with Horizontal(classes="overlay-buttons"):
                yield Button("Chiudi", id="close-help", variant="primary")

    def _help_text(self) -> str:
        return (
            "[bold]Muovere il pedone:[/bold] seleziona [green]Muovi[/green] "
            "nel pannello AZIONE e clicca su una cella verde evidenziata.\n\n"
            "[bold]Piazzare un muro orizzontale:[/bold] seleziona "
            "[green]Muro —[/green] "
            "e clicca sullo slot tra le righe: l'anteprima è ambra se valida, "
            "rossa se non valida.\n\n"
            "[bold]Piazzare un muro verticale:[/bold] seleziona [green]Muro |[/green] "
            "e clicca sullo slot tra le colonne, con la stessa logica di anteprima.\n\n"
            "[bold]Cronologia:[/bold] il pulsante [green]Cronologia[/green] mostra "
            "la lista ordinata delle mosse effettuate. Non consuma il turno.\n\n"
            "[bold]Abbandono:[/bold] il pulsante [green]Abbandona[/green] elimina "
            "il giocatore di turno. In 2 giocatori l'avversario vince; in 4 giocatori "
            "la partita prosegue tra i rimanenti.\n\n"
            "[bold]Modalità a tempo:[/bold] all'avvio puoi attivare un orologio "
            "stile scacchi indipendente per ogni giocatore. Sotto 30 secondi il "
            "timer si colora di rosso; se scade, il giocatore viene eliminato.\n\n"
            "[bold]Vittoria:[/bold]\n"
            "  • P1 (Nord) → raggiunge la riga 9.\n"
            "  • P2 (Sud) → raggiunge la riga 1.\n"
            "  • P3 (Ovest) → raggiunge la colonna i.\n"
            "  • P4 (Est) → raggiunge la colonna a.\n\n"
            "[bold]Replay:[/bold] al termine della partita puoi rivedere ogni "
            "mossa snapshot per snapshot con i pulsanti "
            "← Precedente / Successiva →.\n\n"
            "[bold]Esci:[/bold] pulsante [green]Esci[/green] in alto a destra "
            "oppure [green]Ctrl+Q[/green]."
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-help":
            self.dismiss()


# ============================================================
# Cronologia — overlay con tabella delle mosse
# ============================================================

class HistoryOverlay(ModalScreen):
    """Mostra la cronologia delle mosse in una tabella formattata.

    Riceve la lista di mosse da `MoveHistory.get_all_moves()`.
    """

    BINDINGS = [("escape", "dismiss", "Chiudi")]

    def __init__(self, moves: list[dict[str, str]]) -> None:
        super().__init__()
        self._moves = moves

    def compose(self) -> ComposeResult:
        with Container(classes="overlay-card"):
            yield Static("◆ CRONOLOGIA MOSSE ◆", classes="overlay-title")
            if not self._moves:
                with VerticalScroll(classes="overlay-content"):
                    yield Static(
                        "[italic]Nessuna mossa effettuata.[/italic]",
                    )
            else:
                table = DataTable(zebra_stripes=True, cursor_type="row")
                table.add_columns("Turno", "Giocatore", "Tipo", "Comando")
                for move in self._moves:
                    pnum = int(move["player"][1])
                    color = PLAYER_COLORS_HEX.get(pnum, "#ffffff")
                    player_cell = f"[bold {color}]{move['player']}[/bold {color}]"
                    table.add_row(
                        move["turn"],
                        player_cell,
                        move["type"],
                        move["command"],
                    )
                yield table
            with Horizontal(classes="overlay-buttons"):
                yield Button("Chiudi", id="close-history", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-history":
            self.dismiss()


# ============================================================
# Vittoria / Fine partita
# ============================================================

class WinnerOverlay(ModalScreen):
    """Schermata di fine partita con messaggio del vincitore e azioni.

    Restituisce al chiamante (via `dismiss`) una delle stringhe:
        "replay", "new", "exit"
    """

    BINDINGS = [("escape", "_quit", "Esci")]

    def __init__(self, winner: int, reason: str = "vittoria") -> None:
        """Inizializza l'overlay di fine partita.

        winner: numero del giocatore vincente.
        reason: stringa informativa ("vittoria", "abbandono", "timeout").
        """
        super().__init__()
        self._winner = winner
        self._reason = reason

    def compose(self) -> ComposeResult:
        color = PLAYER_COLORS_HEX.get(self._winner, "#ffffff")
        with Container(classes="overlay-card"):
            yield Static(
                f"[bold {color}]◆ Il Giocatore {self._winner} ha vinto! ◆"
                f"[/bold {color}]",
                id="winner-banner",
            )
            yield Static(
                f"[italic]Causa: {self._reason}[/italic]",
                classes="overlay-content",
            )
            with Horizontal(classes="overlay-buttons"):
                yield Button("Replay", id="replay-btn", variant="primary")
                yield Button("Nuova partita", id="new-game-btn")
                yield Button("Esci", id="exit-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "replay-btn":
            self.dismiss("replay")
        elif event.button.id == "new-game-btn":
            self.dismiss("new")
        elif event.button.id == "exit-btn":
            self.dismiss("exit")

    def action__quit(self) -> None:
        self.dismiss("exit")


# ============================================================
# Replay — schermata con board + controlli avanti/indietro
# ============================================================

class ReplayScreen(ModalScreen):
    """Schermata di replay: ricostruisce gli snapshot e li mostra uno per uno.

    Restituisce sempre "back" al `dismiss` per indicare ritorno alla
    WinnerOverlay (in modo che l'utente possa scegliere "Nuova partita"
    o "Esci" dopo aver visto il replay).
    """

    BINDINGS = [
        ("escape", "_quit", "Esci"),
        ("left", "_prev", "Precedente"),
        ("right", "_next", "Successiva"),
    ]

    def __init__(
        self,
        moves: list[dict[str, str]],
        num_players: int,
    ) -> None:
        super().__init__()
        self._moves = moves
        self._num_players = num_players
        self._replay = ReplayHandler(moves, num_players)
        self._total = self._replay.total_moves()
        self._index = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="game-root"):
            yield Static(self._info_text(), id="replay-info")
            with Container(id="board-area"):
                yield BoardWidget(self._replay.get_snapshot(0))
            with Horizontal(id="replay-controls"):
                yield Button("← Precedente", id="prev-btn")
                yield Button("Successiva →", id="next-btn")
                yield Button("Esci dal replay", id="quit-replay-btn", variant="warning")

    def on_mount(self) -> None:
        # Disabilita interazioni sul board durante il replay.
        board = self.query_one(BoardWidget)
        board.set_mode("disabled")

    def _info_text(self) -> str:
        if self._index == 0:
            return f"REPLAY — Posizione iniziale (0 / {self._total})"
        move = self._moves[self._index - 1]
        pnum = int(move["player"][1])
        color = PLAYER_COLORS_HEX.get(pnum, "#ffffff")
        return (
            f"REPLAY — Mossa {self._index} / {self._total}    "
            f"[bold {color}]{move['player']}[/bold {color}] "
            f"({move['type']}): [bold]{move['command']}[/bold]"
        )

    def _update_view(self) -> None:
        info = self.query_one("#replay-info", Static)
        info.update(self._info_text())
        board_widget = self.query_one(BoardWidget)
        board_widget.set_board(self._replay.get_snapshot(self._index))

    def action__prev(self) -> None:
        if self._index > 0:
            self._index -= 1
            self._update_view()

    def action__next(self) -> None:
        if self._index < self._total:
            self._index += 1
            self._update_view()

    def action__quit(self) -> None:
        self.dismiss("back")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "prev-btn":
            self.action__prev()
        elif event.button.id == "next-btn":
            self.action__next()
        elif event.button.id == "quit-replay-btn":
            self.action__quit()


# ============================================================
# Notifica di eliminazione (timeout / abbandono in 4 giocatori)
# ============================================================

class NotificationOverlay(ModalScreen):
    """Piccolo overlay informativo: eliminazione di un giocatore.

    Si chiude da sé al click del pulsante "OK".
    """

    BINDINGS = [("escape", "dismiss", "OK")]

    def __init__(self, title: str, body: str) -> None:
        super().__init__()
        self._title = title
        self._body = body

    def compose(self) -> ComposeResult:
        with Container(classes="overlay-card"):
            yield Static(self._title, classes="overlay-title")
            with VerticalScroll(classes="overlay-content"):
                yield Static(self._body)
            with Horizontal(classes="overlay-buttons"):
                yield Button("OK", id="ok-btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            self.dismiss()
