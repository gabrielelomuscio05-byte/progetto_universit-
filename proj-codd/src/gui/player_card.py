"""Widget Card-giocatore: nome, muri, timer e barra progressiva.

Fix rispetto alla versione precedente:
- Barra timer con larghezza fissa di 20 char (prima era walls_max*2 = 10,
  troppo corta e semivuota visivamente).
- La barra parte SEMPRE al 100% e decresce: ratio = remaining / max_seconds.
- Modalità senza tempo: non mostra né timer né barra.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

PLAYER_COLORS_HEX: dict[int, str] = {
    1: "#4ecdc4",
    2: "#ff6b6b",
    3: "#f7dc6f",
    4: "#a29bfe",
}

TIMER_WARN_COLOR = "#ff4444"
TIMER_OK_COLOR   = "#4ecdc4"
TIMER_LOW_COLOR  = "#f0a500"

# Larghezza fissa della barra del timer in caratteri
TIMER_BAR_WIDTH = 20


class PlayerCard(Widget):
    """Card che mostra nome, muri, timer e stato di un giocatore."""

    def __init__(
        self,
        player: int,
        walls_max: int,
        timed: bool = False,
        max_seconds: int = 300,
    ) -> None:
        super().__init__(id=f"player-card-{player}")
        self.player      = player
        self.walls_max   = walls_max
        self.timed       = timed
        self.max_seconds = max_seconds if max_seconds > 0 else 300

        self.walls_left    = walls_max
        self.is_turn       = False
        self.time_text     = "--:--"
        self.timer_warning = False
        self.is_eliminated = False
        # Parte al 100%: remaining == max_seconds
        self._remaining_s  = float(self.max_seconds)

    def update_state(
        self,
        *,
        walls_left: int,
        is_turn: bool,
        time_text: str,
        timer_warning: bool = False,
        is_eliminated: bool = False,
        remaining_seconds: float = -1.0,
    ) -> None:
        self.walls_left    = walls_left
        self.is_turn       = is_turn
        self.time_text     = time_text
        self.timer_warning = timer_warning
        self.is_eliminated = is_eliminated
        if remaining_seconds >= 0:
            self._remaining_s = remaining_seconds

        if is_turn and not is_eliminated:
            self.add_class("-active")
        else:
            self.remove_class("-active")

        if is_eliminated:
            self.add_class("-eliminated")
        else:
            self.remove_class("-eliminated")

        self.refresh()

    def render(self) -> Text:
        color = PLAYER_COLORS_HEX.get(self.player, "#ffffff")
        text  = Text()

        # Riga 1: nome + turno
        if self.is_eliminated:
            text.append(f" P{self.player}", style="bold #888888")
            text.append("  eliminato", style="italic #888888")
        else:
            text.append(f" P{self.player}", style=f"bold {color}")
            if self.is_turn:
                text.append("  \u25cf TURNO", style=f"bold {color}")
        text.append("\n")

        # Riga 2: muri numerici
        text.append(f" Muri: {self.walls_left}/{self.walls_max}", style="#b0b8c8")
        text.append("\n")

        # Riga 3: barra muri
        filled = "\u2588" * self.walls_left
        empty  = "\u2591" * (self.walls_max - self.walls_left)
        text.append(" ", style="")
        text.append(filled, style=color)
        text.append(empty,  style="#2a3a4a")

        # Righe 4+5: timer e barra progressiva (SOLO modalità timed)
        if self.timed and not self.is_eliminated:
            text.append("\n")

            # Colore in base al tempo residuo
            if self.timer_warning:
                timer_color = TIMER_WARN_COLOR
            elif self._remaining_s < 60:
                timer_color = TIMER_LOW_COLOR
            else:
                timer_color = TIMER_OK_COLOR

            text.append(" \u23f1 ", style="bold #b0b8c8")
            text.append(self.time_text, style=f"bold {timer_color}")
            text.append("\n")

            # Barra progressiva: TIMER_BAR_WIDTH fisso, ratio = remaining/max
            ratio    = max(0.0, min(1.0, self._remaining_s / self.max_seconds))
            filled_w = round(ratio * TIMER_BAR_WIDTH)
            empty_w  = TIMER_BAR_WIDTH - filled_w
            text.append(" ", style="")
            text.append("\u2588" * filled_w, style=timer_color)
            text.append("\u2591" * empty_w,  style="#2a3a4a")

        return text