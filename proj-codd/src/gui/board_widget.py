"""BoardWidget — widget Textual custom che disegna la griglia 9x9.

Fix rispetto alla versione precedente:
- Contenuto pedone ora esattamente CELL_W (7) caratteri — prima era 6,
  causando sfasamento di tutta la riga e "tagli" nelle linee orizzontali.
- Rimosso salto avversario (dist==2) dalla GUI.
- Grafica aggiornata con bordi più visibili.
"""

from __future__ import annotations

import copy

from rich.text import Text
from textual.events import Click, Leave, MouseMove
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget

from src.board import QuoridorBoard

# ============================================================
# Costanti di layout
# ============================================================

CELL_W    = 7
CELL_H    = 2
GUTTER    = 1

COL_CYCLE = CELL_W + GUTTER   # 8
ROW_CYCLE = CELL_H + GUTTER   # 3

BOARD_W = 9 * CELL_W + 8 * GUTTER   # 71
BOARD_H = 9 * CELL_H + 8 * GUTTER   # 26

LABEL_LEFT = 2
LABEL_TOP  = 1

WIDGET_W = LABEL_LEFT + BOARD_W   # 73
WIDGET_H = LABEL_TOP  + BOARD_H   # 27

# ============================================================
# Palette colori
# ============================================================

PLAYER_COLORS_HEX: dict[int, str] = {
    1: "#4ecdc4",
    2: "#ff6b6b",
    3: "#f7dc6f",
    4: "#a29bfe",
}

APP_BG       = "#0a1520"
CELL_BG      = "#132840"
CELL_BG_ALT  = "#0f2035"
TEXT_COLOR    = "#e0e0e0"
ACCENT       = "#4ecdc4"

HOVER_CELL_BG = "#1e4060"
HOVER_CELL_FG = "#7ffff0"

WALL_OK     = "#f0a500"
WALL_KO     = "#ff4444"
WALL_PLACED = "#c8d8e8"
GRID_LINE   = "#253a52"

# Colore meta-riga tintato (solo background leggero)
GOAL_ROW_BG = "#0c3020"
GOAL_COL_BG = "#18162e"


# ============================================================
# Filtro anti-salto (Cat.2: rimuovere meccanica salto avversario)
# ============================================================

def _is_jump_move(board: QuoridorBoard, r1: int, c1: int, r2: int, c2: int) -> bool:
    """Controlla se la mossa è un salto sopra un avversario.

    Condizione: distanza == 2 in linea retta con cella intermedia occupata.
    La GUI blocca il salto anche se il backend lo accetterebbe.
    """
    if abs(r1 - r2) + abs(c1 - c2) != 2:
        return False
    if r1 != r2 and c1 != c2:
        return False
    mid_r = (r1 + r2) // 2
    mid_c = (c1 + c2) // 2
    all_positions = [board.positions[p] for p in board.active_players]
    return [mid_r, mid_c] in all_positions


# ============================================================
# BoardWidget
# ============================================================

class BoardWidget(Widget):
    """Widget grafico della scacchiera di Quoridor."""

    DEFAULT_CSS = f"""
    BoardWidget {{
        width: {WIDGET_W};
        height: {WIDGET_H};
        background: {APP_BG};
        color: {TEXT_COLOR};
    }}
    """

    mode: reactive[str] = reactive("move")
    hover_target: reactive[tuple | None] = reactive(None, layout=False)

    class CellSelected(Message):
        """Messaggio emesso quando l'utente seleziona una cella."""

        def __init__(self, row: int, col: int) -> None:
            self.row = row
            self.col = col
            super().__init__()

    class WallSelected(Message):
        """Messaggio emesso quando l'utente seleziona uno slot muro."""

        def __init__(self, orientation: str, row: int, col: int) -> None:
            self.orientation = orientation
            self.row = row
            self.col = col
            super().__init__()

    def __init__(self, board: QuoridorBoard) -> None:
        super().__init__(id="board")
        self.board = board
        self._reachable_cells: set[tuple[int, int]] = set()
        self.recompute_reachable()

    def set_board(self, board: QuoridorBoard) -> None:
        self.board = board
        self.recompute_reachable()
        self.refresh()

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.hover_target = None
        self.refresh()

    def refresh_after_change(self) -> None:
        self.recompute_reachable()
        self.refresh()

    # ============================================================
    # Celle raggiungibili (con filtro anti-salto)
    # ============================================================

    def recompute_reachable(self) -> None:
        self._reachable_cells = set()
        if not self.board.active_players:
            return
        cur = self.board.turn
        r1, c1 = self.board.positions[cur]
        for r in range(9):
            for c in range(9):
                if _is_jump_move(self.board, r1, c1, r, c):
                    continue
                test = self._snapshot_board()
                command = f"{chr(ord('a') + c)}{r + 1}"
                ok, _ = test.process_move(command)
                if ok:
                    self._reachable_cells.add((r, c))

    def _wall_valid(self, orientation: str, r: int, c: int) -> bool:
        if not (0 <= r <= 7 and 0 <= c <= 7):
            return False
        test = self._snapshot_board()
        command = f"{orientation}{chr(ord('a') + c)}{r + 1}"
        ok, _ = test.process_move(command)
        return ok

    def _snapshot_board(self) -> QuoridorBoard:
        return copy.deepcopy(self.board)

    # ============================================================
    # Mouse → coordinata logica
    # ============================================================

    def _mouse_to_target(self, x: int, y: int) -> tuple | None:
        bx = x - LABEL_LEFT
        by = y - LABEL_TOP
        if bx < 0 or by < 0 or bx >= BOARD_W or by >= BOARD_H:
            return None
        col_div, col_mod = divmod(bx, COL_CYCLE)
        row_div, row_mod = divmod(by, ROW_CYCLE)
        if col_div > 8 or row_div > 8:
            return None
        is_v_gutter = col_mod >= CELL_W
        is_h_gutter = row_mod >= CELL_H
        if not is_v_gutter and not is_h_gutter:
            return ("cell", row_div, col_div)
        if is_h_gutter and not is_v_gutter:
            return ("hwall", min(row_div, 7), min(col_div, 7))
        if is_v_gutter and not is_h_gutter:
            return ("vwall", min(row_div, 7), min(col_div, 7))
        return None

    # ============================================================
    # Event handlers
    # ============================================================

    def on_mouse_move(self, event: MouseMove) -> None:
        if self.mode == "disabled":
            if self.hover_target is not None:
                self.hover_target = None
                self.refresh()
            return
        target = self._mouse_to_target(event.x, event.y)
        if target is not None:
            kind = target[0]
            if (
                (self.mode == "move" and kind != "cell")
                or (self.mode == "hwall" and kind != "hwall")
                or (self.mode == "vwall" and kind != "vwall")
            ):
                target = None
        if target != self.hover_target:
            self.hover_target = target
            self.refresh()

    def on_leave(self, _event: Leave) -> None:
        if self.hover_target is not None:
            self.hover_target = None
            self.refresh()

    def on_click(self, event: Click) -> None:
        if self.mode == "disabled":
            return
        target = self._mouse_to_target(event.x, event.y)
        if target is None:
            return
        kind, r, c = target
        if self.mode == "move" and kind == "cell":
            if (r, c) in self._reachable_cells:
                self.post_message(self.CellSelected(r, c))
        elif self.mode == "hwall" and kind == "hwall":
            if self._wall_valid("h", r, c):
                self.post_message(self.WallSelected("h", r, c))
        elif self.mode == "vwall" and kind == "vwall" and self._wall_valid("v", r, c):
            self.post_message(self.WallSelected("v", r, c))

    # ============================================================
    # Rendering
    # ============================================================

    def render(self) -> Text:
        text = Text(no_wrap=True, overflow="ignore")
        text.append(self._render_header())
        text.append("\n")
        for r in range(9):
            for row_in_cell in range(CELL_H):
                if row_in_cell == 0:
                    text.append(self._render_cell_row(r))
                else:
                    text.append(self._render_cell_row_bottom(r))
                text.append("\n")
            if r < 8:
                text.append(self._render_wall_row(r))
                text.append("\n")
        return text

    # --- Header ---

    def _render_header(self) -> Text:
        t = Text()
        t.append("  ", style=f"on {APP_BG}")
        for c in range(9):
            letter    = chr(ord("a") + c)
            highlight = self._goal_column_color(c)
            lbl_style = (
                f"bold {highlight} on {APP_BG}" if highlight
                else f"bold {ACCENT} on {APP_BG}"
            )
            # Esattamente CELL_W (7) caratteri per allineamento
            pad = CELL_W - 1          # 6
            left = pad // 2           # 3
            right = pad - left        # 3
            t.append(" " * left + letter + " " * right, style=lbl_style)
            if c < 8:
                t.append(" ", style=f"on {APP_BG}")
        return t

    def _goal_column_color(self, c: int) -> str | None:
        if self.board.num_players == 4:
            if c == 8 and 3 in self.board.active_players:
                return PLAYER_COLORS_HEX[3]
            if c == 0 and 4 in self.board.active_players:
                return PLAYER_COLORS_HEX[4]
        return None

    def _goal_row_color(self, r: int) -> str | None:
        if r == 8 and 1 in self.board.active_players:
            return PLAYER_COLORS_HEX[1]
        if r == 0 and 2 in self.board.active_players:
            return PLAYER_COLORS_HEX[2]
        return None

    # --- Colore background cella ---

    def _cell_bg(self, r: int, c: int) -> str:
        # Hover: unica eccezione al colore unificato.
        is_hover = (
            self.mode == "move"
            and self.hover_target == ("cell", r, c)
            and (r, c) in self._reachable_cells
        )
        if is_hover:
            return HOVER_CELL_BG
        # Tutta la scacchiera dello stesso colore — niente pattern,
        # niente tinte goal-row/goal-col (su alcuni monitor le righe/
        # colonne goal sembravano sparire perché troppo scure).
        return CELL_BG

    def _player_at(self, r: int, c: int) -> int | None:
        for p in self.board.active_players:
            if self.board.positions[p] == [r, c]:
                return p
        return None

    # --- Riga di celle (prima riga, con pedone) ---

    def _render_cell_row(self, r: int) -> Text:
        t = Text()
        goal_color = self._goal_row_color(r)
        lbl_style  = (
            f"bold {goal_color} on {APP_BG}" if goal_color
            else f"bold {ACCENT} on {APP_BG}"
        )
        t.append(f"{r + 1} ", style=lbl_style)

        for c in range(9):
            bg    = self._cell_bg(r, c)
            pawn  = self._player_at(r, c)
            content, style = self._cell_top_content(r, c, bg, pawn)
            t.append(content, style=style)
            if c < 8:
                ch, st = self._vgutter_char(r, c)
                t.append(ch, style=st)
        return t

    def _cell_top_content(
        self, r: int, c: int, bg: str, pawn: int | None
    ) -> tuple[str, str]:
        """Prima riga della cella — ESATTAMENTE CELL_W (7) caratteri."""
        if pawn is not None:
            color = PLAYER_COLORS_HEX.get(pawn, "#ffffff")
            # "  P1   " = 7 chars: 2 + P + digit + 3 spazi
            label   = f"P{pawn}"
            pad     = CELL_W - len(label)   # 5
            left    = pad // 2              # 2
            right   = pad - left            # 3
            content = " " * left + label + " " * right
            return (content, f"bold {color} on {bg}")

        if self.mode == "move" and (r, c) in self._reachable_cells:
            is_hover = self.hover_target == ("cell", r, c)
            fg = HOVER_CELL_FG if is_hover else ACCENT
            # "   ·   " = 7 chars
            content = "   \u00b7   "
            return (content, f"bold {fg} on {bg}")

        return (" " * CELL_W, f"on {bg}")

    # --- Seconda riga della cella ---

    def _render_cell_row_bottom(self, r: int) -> Text:
        t = Text()
        t.append("  ", style=f"on {APP_BG}")
        for c in range(9):
            bg = self._cell_bg(r, c)
            t.append(" " * CELL_W, style=f"on {bg}")
            if c < 8:
                ch, st = self._vgutter_char(r, c)
                t.append(ch, style=st)
        return t

    # --- Gutter verticale ---

    def _vgutter_char(self, r: int, c: int) -> tuple[str, str]:
        v_covered = (r, c) in self.board.v_walls or (r - 1, c) in self.board.v_walls

        if (
            self.mode == "vwall"
            and self.hover_target
            and self.hover_target[0] == "vwall"
        ):
            _, hr, hc = self.hover_target
            if hc == c and (hr == r or hr + 1 == r):
                ok    = self._wall_valid("v", hr, hc)
                color = WALL_OK if ok else WALL_KO
                return ("\u2503", f"bold {color} on {APP_BG}")

        if v_covered:
            return ("\u2503", f"bold {WALL_PLACED} on {APP_BG}")
        return ("\u2502", f"{GRID_LINE} on {APP_BG}")

    # --- Riga gutter orizzontale ---

    def _render_wall_row(self, r: int) -> Text:
        t = Text()
        t.append("  ", style=f"on {APP_BG}")
        for c in range(9):
            seg, st = self._hgutter_segment(r, c)
            t.append(seg, style=st)
            if c < 8:
                ch, st2 = self._hgutter_intersection(r, c)
                t.append(ch, style=st2)
        return t

    def _hgutter_segment(self, r: int, c: int) -> tuple[str, str]:
        h_covered = (r, c) in self.board.h_walls or (r, c - 1) in self.board.h_walls

        if (
            self.mode == "hwall"
            and self.hover_target
            and self.hover_target[0] == "hwall"
        ):
            _, hr, hc = self.hover_target
            if hr == r and hc <= c <= hc + 1:
                ok    = self._wall_valid("h", hr, hc)
                color = WALL_OK if ok else WALL_KO
                return ("\u2501" * CELL_W, f"bold {color} on {APP_BG}")

        if h_covered:
            return ("\u2501" * CELL_W, f"bold {WALL_PLACED} on {APP_BG}")
        return ("\u2500" * CELL_W, f"{GRID_LINE} on {APP_BG}")

    def _hgutter_intersection(self, r: int, c: int) -> tuple[str, str]:
        h_inter = (r, c) in self.board.h_walls or (r, c - 1) in self.board.h_walls
        v_inter = (r, c) in self.board.v_walls or (r - 1, c) in self.board.v_walls

        hover_h  = False
        hover_v  = False
        hover_ok = True
        if self.hover_target:
            kind, hr, hc = self.hover_target
            if self.mode == "hwall" and kind == "hwall" and hr == r:
                if hc <= c <= hc + 1:
                    hover_h  = True
                    hover_ok = self._wall_valid("h", hr, hc)
            elif (
                self.mode == "vwall"
                and kind == "vwall"
                and hc == c
                and hr <= r <= hr + 1
            ):
                hover_v  = True
                hover_ok = self._wall_valid("v", hr, hc)

        if hover_h:
            color = WALL_OK if hover_ok else WALL_KO
            return ("\u253f", f"bold {color} on {APP_BG}")
        if hover_v:
            color = WALL_OK if hover_ok else WALL_KO
            return ("\u2542", f"bold {color} on {APP_BG}")
        if h_inter or v_inter:
            return ("\u254b", f"bold {WALL_PLACED} on {APP_BG}")
        return ("\u253c", f"{GRID_LINE} on {APP_BG}")