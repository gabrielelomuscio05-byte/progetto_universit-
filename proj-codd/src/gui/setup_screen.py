"""Schermata di configurazione iniziale."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static


class SetupScreen(Screen):
    """Schermata di configurazione iniziale della partita."""

    BINDINGS = [("escape", "app.quit", "Esci")]

    def __init__(self) -> None:
        super().__init__()
        self._num_players: int = 2
        self._timed: bool = False
        self._minutes: int = 5

    def compose(self) -> ComposeResult:
        with Container(id="setup-root"), Container(id="setup-card"):
            yield Static("\u25c6 QUORIDOR \u25c6", id="setup-title")
            yield Static(
                "Configura la partita prima di iniziare",
                id="setup-subtitle",
            )

            # Numero giocatori
            yield Static("Numero di giocatori", classes="setup-label")
            with Horizontal(classes="setup-row"):
                yield Button(
                    "2 giocatori",
                    id="players-2",
                    classes="-active",
                    variant="success",
                )
                yield Button("4 giocatori", id="players-4")

            # Modalità a tempo
            yield Static("Modalit\u00e0 a tempo", classes="setup-label")
            with Horizontal(classes="setup-row"):
                yield Button(
                    "Disattivata",
                    id="timed-off",
                    classes="-active",
                    variant="success",
                )
                yield Button("Attivata",    id="timed-on")

            # Label + input minuti — nascosti quando timed=False
            yield Static(
                "Minuti per giocatore",
                id="time-label",
                classes="setup-time-label hidden",
            )
            with Horizontal(id="setup-time-row", classes="hidden"):
                yield Input(
                    value="5",
                    placeholder="minuti",
                    id="minutes-input",
                    restrict=r"[0-9]*",
                    max_length=3,
                )
                yield Label("minuti per giocatore", id="minutes-label")

            # Pulsanti finali
            with Horizontal(id="setup-buttons"):
                yield Button("Avvia partita", id="start-btn", variant="primary")
                yield Button("Esci", id="quit-btn", variant="error")

    def _set_active(self, group_ids: list[str], active_id: str) -> None:
        # Usa il variant del bottone invece di una classe CSS: Textual
        # rispetta sempre il colore del variant, mentre le regole
        # background/border su classi custom su Button possono essere
        # sovrascritte dal tema base.
        for bid in group_ids:
            btn = self.query_one(f"#{bid}", Button)
            if bid == active_id:
                btn.variant = "success"
                btn.add_class("-active")
            else:
                btn.variant = "default"
                btn.remove_class("-active")

    def _update_time_visibility(self) -> None:
        time_row   = self.query_one("#setup-time-row")
        time_label = self.query_one("#time-label")
        if self._timed:
            time_row.remove_class("hidden")
            time_label.remove_class("hidden")
        else:
            time_row.add_class("hidden")
            time_label.add_class("hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id

        if bid == "players-2":
            self._num_players = 2
            self._set_active(["players-2", "players-4"], "players-2")
        elif bid == "players-4":
            self._num_players = 4
            self._set_active(["players-2", "players-4"], "players-4")
        elif bid == "timed-off":
            self._timed = False
            self._set_active(["timed-off", "timed-on"], "timed-off")
            self._update_time_visibility()
        elif bid == "timed-on":
            self._timed = True
            self._set_active(["timed-off", "timed-on"], "timed-on")
            self._update_time_visibility()
        elif bid == "start-btn":
            self._submit()
        elif bid == "quit-btn":
            self.app.exit()

    def _submit(self) -> None:
        minutes_input = self.query_one("#minutes-input", Input)
        raw = minutes_input.value.strip()
        if self._timed:
            if not raw.isdigit() or int(raw) <= 0:
                minutes_input.value = "5"
                self._minutes = 5
            else:
                self._minutes = int(raw)
        config = {
            "num_players": self._num_players,
            "timed": self._timed,
            "minutes": self._minutes if self._timed else 0,
        }
        # Avvia la partita: l'app sostituisce questa SetupScreen con la
        # GameScreen via switch_screen, evitando lo "schermo nero" del bug
        # precedente.
        self.app.start_game(config)