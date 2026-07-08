import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.gui.overlays import (
    WinnerOverlay,
    HistoryOverlay,
    NotificationOverlay,
    ReplayScreen,
)
from src.gui.board_widget import PLAYER_COLORS_HEX


class TestWinnerOverlay:

    def test_init_winner1(self):
        ov = WinnerOverlay(winner=1, reason="vittoria")
        assert ov._winner == 1
        assert ov._reason == "vittoria"

    def test_init_winner4_timeout(self):
        ov = WinnerOverlay(winner=4, reason="timeout")
        assert ov._winner == 4
        assert ov._reason == "timeout"

    def test_init_reason_abbandono(self):
        ov = WinnerOverlay(winner=2, reason="abbandono")
        assert ov._reason == "abbandono"

    def test_winner_color_exists(self):
        for p in range(1, 5):
            ov = WinnerOverlay(winner=p)
            assert p in PLAYER_COLORS_HEX

    def test_winner_unknown_player_fallback_color(self):
        ov = WinnerOverlay(winner=99)
        color = PLAYER_COLORS_HEX.get(ov._winner, "#ffffff")
        assert color == "#ffffff"

    def test_winner_boundary_values(self):
        ov_min = WinnerOverlay(winner=1)
        ov_max = WinnerOverlay(winner=4)
        assert ov_min._winner == 1
        assert ov_max._winner == 4


class TestHistoryOverlay:

    def _sample_moves(self):
        return [
            {"player": "P1", "turn": "1", "type": "spostamento", "command": "e2"},
            {"player": "P2", "turn": "2", "type": "muro",        "command": "he4"},
        ]

    def test_init_with_moves(self):
        ov = HistoryOverlay(moves=self._sample_moves())
        assert len(ov._moves) == 2

    def test_init_empty_moves(self):
        ov = HistoryOverlay(moves=[])
        assert ov._moves == []

    def test_player_number_extraction(self):
        for move in self._sample_moves():
            pnum = int(move["player"][1])
            assert 1 <= pnum <= 4

    def test_unknown_move_type_no_error(self):
        moves = [{"player": "P1", "turn": "1", "type": "sconosciuto", "command": "??"}]
        ov = HistoryOverlay(moves=moves)
        assert ov._moves[0]["type"] == "sconosciuto"

    def test_all_player_colors_available(self):
        for p in range(1, 5):
            color = PLAYER_COLORS_HEX.get(p, "#ffffff")
            assert color.startswith("#")


class TestNotificationOverlay:

    def test_init_stores_title_body(self):
        ov = NotificationOverlay(title="Titolo", body="Corpo del messaggio")
        assert ov._title == "Titolo"
        assert ov._body == "Corpo del messaggio"

    def test_init_rich_markup_in_title(self):
        ov = NotificationOverlay(
            title="[bold red]Eliminato![/bold red]",
            body="Giocatore rimosso."
        )
        assert "Eliminato" in ov._title

    def test_init_empty_strings(self):
        ov = NotificationOverlay(title="", body="")
        assert ov._title == ""
        assert ov._body == ""

    def test_init_multiline_body(self):
        body = "Riga 1\nRiga 2\nRiga 3"
        ov = NotificationOverlay(title="Test", body=body)
        assert "\n" in ov._body


class TestReplayScreen:

    def _sample_moves(self):
        return [
            {"player": "P1", "turn": "1", "type": "spostamento", "command": "e2"},
            {"player": "P2", "turn": "2", "type": "spostamento", "command": "e8"},
            {"player": "P1", "turn": "3", "type": "muro",        "command": "he4"},
        ]

    def test_init_2players(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        assert rs._num_players == 2
        assert rs._total == 3

    def test_init_4players(self):
        moves = [{"player": "P3", "turn": "1", "type": "spostamento", "command": "e5"}]
        rs = ReplayScreen(moves, num_players=4)
        assert rs._num_players == 4

    def test_init_empty_moves(self):
        rs = ReplayScreen([], num_players=2)
        assert rs._total == 0
        assert rs._index == 0

    def test_initial_index_zero(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        assert rs._index == 0

    def test_next_increments_index(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        rs.action__next()
        assert rs._index == 1

    def test_next_does_not_exceed_total(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        rs._index = 3
        rs.action__next()
        assert rs._index == 3

    def test_prev_decrements_index(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        rs._index = 2
        rs.action__prev()
        assert rs._index == 1

    def test_prev_does_not_go_below_zero(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        rs._index = 0
        rs.action__prev()
        assert rs._index == 0

    def test_info_text_at_zero(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        text = rs._info_text()
        assert "Posizione iniziale" in text

    def test_info_text_at_one(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        rs._index = 1
        text = rs._info_text()
        assert "e2" in text

    def test_snapshots_accessible(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        for i in range(rs._total + 1):
            snap = rs._replay.get_snapshot(i)
            assert snap is not None

    def test_snapshot_zero_is_initial(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        snap = rs._replay.get_snapshot(0)
        assert snap.positions[1] == [0, 4]

    def test_snapshot_last_reflects_last_move(self):
        rs = ReplayScreen(self._sample_moves(), num_players=2)
        snap = rs._replay.get_snapshot(rs._total)
        assert (3, 4) in snap.h_walls
