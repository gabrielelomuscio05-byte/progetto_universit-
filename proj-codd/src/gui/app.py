"""QuoridorApp + GameScreen — controller principale della GUI Textual.

Fix rispetto alla versione precedente:
- Sidebar ristrutturata: AZIONE e ALTRO sempre visibili, GIOCATORI scrollabile
  → "Abbandona la partita" raggiungibile anche con 4 giocatori.
- Vittoria 2 giocatori: WinHandler.check_win() controlla ultimo-in-piedi
  solo per 4 giocatori. La GUI aggiunge il controllo len(active)==1 per
  qualsiasi modalità, così l'abbandono in 2 giocatori dà vittoria immediata.
- Schermata nera: _do_restart usa pop_screen + call_after_refresh.
- Replay: copia esplicita delle mosse.
"""

from __future__ import annotations

import time
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static

from src.board import QuoridorBoard
from src.gui.board_widget import PLAYER_COLORS_HEX, BoardWidget
from src.gui.overlays import (
    HelpOverlay,
    HistoryOverlay,
    NotificationOverlay,
    ReplayScreen,
    WinnerOverlay,
)
from src.gui.player_card import PlayerCard
from src.gui.setup_screen import SetupScreen
from src.history import MoveHistory
from src.timer import GameTimer
from src.win_handler import WinHandler

# ============================================================
# Cronometro crescente (modalità senza tempo)
# ============================================================

class _Stopwatch:
    def __init__(self, num_players: int) -> None:
        self._elapsed: dict[int, float] = {p: 0.0 for p in range(1, num_players + 1)}
        self._active: int | None = None
        self._start:  float | None = None

    def start_turn(self, player: int) -> None:
        self.stop_turn()
        self._active = player
        self._start  = time.monotonic()

    def stop_turn(self) -> None:
        if self._active is not None and self._start is not None:
            self._elapsed[self._active] += time.monotonic() - self._start
        self._active = None
        self._start  = None

    def get_elapsed(self, player: int) -> float:
        elapsed = self._elapsed.get(player, 0.0)
        if self._active == player and self._start is not None:
            elapsed += time.monotonic() - self._start
        return elapsed

    def remove_player(self, player: int) -> None:
        self._elapsed.pop(player, None)
        if self._active == player:
            self._active = None
            self._start  = None


def _fmt_seconds(seconds: float) -> str:
    s = max(0, int(seconds))
    return f"{s // 60:02d}:{s % 60:02d}"


# ============================================================
# GameScreen
# ============================================================

class GameScreen(Screen):
    """Schermata principale di gioco del Quoridor."""

    BINDINGS = [
        ("ctrl+q", "app.quit", "Esci"),
        ("ctrl+h", "show_help", "Aiuto"),
    ]

    def __init__(self, num_players: int, timed: bool, minutes: int) -> None:
        super().__init__()
        self._num_players  = num_players
        self._timed        = timed
        self._minutes      = minutes
        self._max_seconds  = minutes * 60 if timed else 0

        self.board: QuoridorBoard = QuoridorBoard(num_players)
        self.history: MoveHistory = MoveHistory()
        self.timer: GameTimer | None = (
            GameTimer(self._max_seconds, num_players) if timed else None
        )
        self.stopwatch: _Stopwatch | None = (
            None if timed else _Stopwatch(num_players)
        )

        self._mode:      str  = "move"
        self._game_over: bool = False

    # ============================================================
    # Compose — sidebar con scroll per i giocatori
    # ============================================================

    def compose(self) -> ComposeResult:
        walls_max = 10 if self._num_players == 2 else 5

        with Vertical(id="game-root"):
            # Header
            with Horizontal(id="game-header"):
                yield Static("\u25c6 QUORIDOR", id="title")
                yield Button("Cronologia", id="history-btn",     variant="primary")
                yield Button("Aiuto",      id="help-header-btn", variant="primary")
                yield Button("Esci",       id="quit-header-btn", variant="error")

            # Corpo principale
            with Horizontal(id="main-row"):
                with Container(id="board-area"):
                    yield BoardWidget(self.board)

                with Vertical(id="sidebar"):
                    # AZIONE — sempre visibile in alto
                    with Container(classes="section-panel", id="action-panel"):
                        yield Static("AZIONE", classes="section-title")
                        with Horizontal(id="action-buttons"):
                            yield Button(
                                "Muovi",
                                id="mode-move-btn",
                                classes="-active",
                                variant="success",
                            )
                            yield Button("Muro \u2500", id="mode-hwall-btn")
                            yield Button("Muro |", id="mode-vwall-btn")

                    # GIOCATORI — scrollabile se necessario
                    with VerticalScroll(id="players-scroll"):
                        yield Static("GIOCATORI", classes="section-title")
                        for p in range(1, self._num_players + 1):
                            yield PlayerCard(
                                p, walls_max,
                                timed=self._timed,
                                max_seconds=self._max_seconds,
                            )

                    # ALTRO — sempre visibile in basso
                    with Container(id="bottom-panel"):
                        yield Button(
                            "Abbandona la partita",
                            id="abandon-btn",
                            variant="error",
                        )

            # Status bar
            yield Static("", id="status-bar")

    # ============================================================
    # on_mount
    # ============================================================

    def on_mount(self) -> None:
        self._start_turn_timer()
        self._refresh_all_cards()
        self._refresh_status()
        self.set_interval(1.0, self._on_tick)

    # ============================================================
    # Helpers
    # ============================================================

    def _start_turn_timer(self) -> None:
        if self._game_over:
            return
        if self.timer is not None:
            self.timer.start_turn(self.board.turn)
        if self.stopwatch is not None:
            self.stopwatch.start_turn(self.board.turn)

    def _stop_turn_timer(self) -> None:
        if self.timer is not None:
            self.timer.stop_turn()
        if self.stopwatch is not None:
            self.stopwatch.stop_turn()

    def _refresh_board(self) -> None:
        self.query_one(BoardWidget).refresh_after_change()

    def _refresh_all_cards(self) -> None:
        current_turn = self.board.turn if self.board.active_players else None
        for p in range(1, self._num_players + 1):
            try:
                card = self.query_one(f"#player-card-{p}", PlayerCard)
            except Exception:
                continue

            is_eliminated = p not in self.board.active_players
            walls_left    = self.board.walls_left.get(p, 0)
            is_turn       = (p == current_turn) and not is_eliminated

            if is_eliminated:
                time_text      = "--:--"
                warning        = False
                remaining_secs = -1.0
            elif self.timer is not None:
                remaining      = self.timer.get_remaining(p)
                time_text      = _fmt_seconds(remaining)
                warning        = remaining < 30
                remaining_secs = float(remaining)
            elif self.stopwatch is not None:
                elapsed        = self.stopwatch.get_elapsed(p)
                time_text      = _fmt_seconds(elapsed)
                warning        = False
                remaining_secs = -1.0
            else:
                time_text      = "--:--"
                warning        = False
                remaining_secs = -1.0

            card.update_state(
                walls_left        = walls_left,
                is_turn           = is_turn,
                time_text         = time_text,
                timer_warning     = warning,
                is_eliminated     = is_eliminated,
                remaining_seconds = remaining_secs,
            )

    def _refresh_status(self, override: str | None = None) -> None:
        bar = self.query_one("#status-bar", Static)
        if override is not None:
            bar.update(override)
            return
        if self._game_over:
            bar.update("Partita conclusa.")
            return
        if not self.board.active_players:
            bar.update("Nessun giocatore attivo.")
            return
        turn  = self.board.turn
        color = PLAYER_COLORS_HEX.get(turn, "#ffffff")
        hint  = {
            "move":  "Clicca una cella per muovere il pedone.",
            "hwall": "Clicca uno slot per un muro orizzontale.",
            "vwall": "Clicca uno slot per un muro verticale.",
        }.get(self._mode, "")
        bar.update(f"Turno di [bold {color}]P{turn}[/bold {color}] \u2014 {hint}")

    # ============================================================
    # Tick
    # ============================================================

    def _on_tick(self) -> None:
        if self._game_over:
            return
        if self.timer is not None and self.board.active_players:
            cur = self.board.turn
            if self.timer.is_expired(cur):
                self._handle_timeout(cur)
                return
        self._refresh_all_cards()

    # ============================================================
    # Bottoni
    # ============================================================

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "mode-move-btn":
            self._set_mode("move")
        elif bid == "mode-hwall-btn":
            self._set_mode("hwall")
        elif bid == "mode-vwall-btn":
            self._set_mode("vwall")
        elif bid == "history-btn":
            self._open_history()
        elif bid == "help-header-btn":
            self.action_show_help()
        elif bid == "abandon-btn":
            self._handle_abandon()
        elif bid == "quit-header-btn":
            self.app.exit()

    def _set_mode(self, mode: str) -> None:
        if self._game_over:
            return
        self._mode = mode
        for btn_id, m in (
            ("mode-move-btn",  "move"),
            ("mode-hwall-btn", "hwall"),
            ("mode-vwall-btn", "vwall"),
        ):
            btn = self.query_one(f"#{btn_id}", Button)
            if m == mode:
                btn.variant = "success"
                btn.add_class("-active")
            else:
                btn.variant = "default"
                btn.remove_class("-active")
        self.query_one(BoardWidget).set_mode(mode)
        self._refresh_status()

    # ============================================================
    # Overlay
    # ============================================================

    def action_show_help(self) -> None:
        if self._game_over:
            return
        self._stop_turn_timer()
        self.app.push_screen(HelpOverlay(), callback=self._after_overlay_close)

    def _open_history(self) -> None:
        self._stop_turn_timer()
        moves_snapshot = list(self.history.get_all_moves())
        self.app.push_screen(
            HistoryOverlay(moves_snapshot),
            callback=self._after_overlay_close,
        )

    def _after_overlay_close(self, _result) -> None:
        if not self._game_over:
            self._start_turn_timer()
            self._refresh_all_cards()

    # ============================================================
    # Mosse
    # ============================================================

    def on_board_widget_cell_selected(self, event: BoardWidget.CellSelected) -> None:
        if self._game_over:
            return
        command = f"{chr(ord('a') + event.col)}{event.row + 1}"
        self._apply_command(command)

    def on_board_widget_wall_selected(self, event: BoardWidget.WallSelected) -> None:
        if self._game_over:
            return
        command = f"{event.orientation}{chr(ord('a') + event.col)}{event.row + 1}"
        self._apply_command(command)

    def _apply_command(self, command: str) -> None:
        current_player = self.board.turn
        self._stop_turn_timer()

        success, error = self.board.process_move(command)
        if not success:
            self._refresh_status(override=f"[red]{error}[/red]")
            self._start_turn_timer()
            return

        self.history.record_move(current_player, command)
        self._refresh_board()
        self._refresh_all_cards()

        winner = WinHandler.check_win(self.board)
        if winner != 0:
            self._finish_game(winner, reason="vittoria")
            return

        self._start_turn_timer()
        self._refresh_all_cards()
        self._refresh_status()

    # ============================================================
    # Abbandono / Timeout
    # ============================================================

    def _handle_abandon(self) -> None:
        if self._game_over or not self.board.active_players:
            return
        current_player = self.board.turn
        self._stop_turn_timer()
        self._eliminate(current_player, reason="abbandono")

    def _handle_timeout(self, player: int) -> None:
        self._stop_turn_timer()
        self._eliminate(player, reason="timeout")

    def _eliminate(self, player: int, reason: str) -> None:
        """Elimina il giocatore.

        FIX VITTORIA 2 GIOCATORI: WinHandler.check_win() controlla
        'ultimo in piedi' SOLO in modalità 4 giocatori. La GUI aggiunge
        il controllo esplicito: se dopo l'eliminazione resta un solo
        giocatore attivo, quello vince — indipendentemente dalla modalità.

        FIX REPLAY: registriamo l'eliminazione come pseudo-mossa nella
        history (command="abbandono" o "timeout") così il ReplayHandler
        può ricostruirla correttamente e il replay non si interrompe.
        """
        # Registra l'eliminazione nella history come pseudo-mossa.
        if reason in ("abbandono", "timeout"):
            self.history.record_move(player, reason)

        self.board.eliminate_player(player)
        if self.timer is not None:
            self.timer.remove_player(player)
        if self.stopwatch is not None:
            self.stopwatch.remove_player(player)

        self._refresh_board()
        self._refresh_all_cards()

        # Controlla vincitore: prima via WinHandler, poi fallback last-standing
        winner = WinHandler.check_win(self.board)
        if winner == 0 and len(self.board.active_players) == 1:
            winner = self.board.active_players[0]

        if winner != 0:
            # Vittoria immediata → WinnerOverlay con replay/nuova/esci
            self._finish_game(winner, reason=reason)
        else:
            # 4 giocatori: la partita prosegue
            remaining = ", ".join(f"P{p}" for p in self.board.active_players)
            body = (
                f"Il Giocatore {player} \u00e8 stato eliminato ({reason}).\n"
                f"Giocatori rimasti: {remaining}."
            )

            def _resume(_result) -> None:
                if not self._game_over:
                    self._start_turn_timer()
                    self._refresh_all_cards()
                    self._refresh_status()

            self.app.push_screen(
                NotificationOverlay("Giocatore eliminato", body),
                callback=_resume,
            )

    # ============================================================
    # Fine partita
    # ============================================================

    def _finish_game(self, winner: int, reason: str) -> None:
        self._game_over = True
        self._stop_turn_timer()
        self._refresh_board()
        self._refresh_all_cards()
        self._refresh_status()
        self.query_one(BoardWidget).set_mode("disabled")

        self.app.push_screen(
            WinnerOverlay(winner, reason=reason),
            callback=self._post_game_choice,
        )

    def _post_game_choice(self, result) -> None:
        if result == "replay":
            moves_snapshot = list(self.history.get_all_moves())
            self.app.push_screen(
                ReplayScreen(moves_snapshot, self._num_players),
                callback=lambda _r: self._post_replay(),
            )
        elif result == "new":
            self._restart_new_game()
        else:
            self.app.exit()

    def _post_replay(self) -> None:
        winners = list(self.board.active_players)
        winner  = winners[0] if len(winners) == 1 else 0
        if winner == 0:
            self.app.exit()
            return
        self.app.push_screen(
            WinnerOverlay(winner, reason="fine replay"),
            callback=self._post_game_choice,
        )

    def _restart_new_game(self) -> None:
        self.app._do_restart()


# ============================================================
# QuoridorApp
# ============================================================

class QuoridorApp(App):
    """Applicazione Textual per il gioco Quoridor."""

    CSS_PATH  = str(Path(__file__).parent / "styles.tcss")
    TITLE     = "Quoridor"
    SUB_TITLE = "GUI Textual"
    BINDINGS  = [("ctrl+q", "quit", "Esci")]

    def on_mount(self) -> None:
        self.push_screen(SetupScreen())

    def _do_restart(self) -> None:
        # switch_screen sostituisce in modo atomico la GameScreen con una
        # nuova SetupScreen, evitando lo "schermo nero" del bug precedente
        # che usava pop_screen + call_after_refresh.
        self.switch_screen(SetupScreen())

    def start_game(self, config: dict) -> None:
        """Avvia una nuova GameScreen sostituendo la screen corrente.

        Chiamato dalla SetupScreen al submit (sia al primo avvio sia
        dopo una partita conclusa con "Nuova partita").
        """
        self.switch_screen(
            GameScreen(
                num_players=config["num_players"],
                timed=config["timed"],
                minutes=config.get("minutes", 0),
            )
        )

    def _on_setup_done(self, config: dict | None) -> None:
        if not config:
            self.exit()
            return
        self.start_game(config)