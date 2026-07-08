import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pytest
from src.history import MoveHistory


class TestMoveHistory:

    def test_record_movement(self):
        h = MoveHistory()
        h.record_move(1, "e2")
        moves = h.get_all_moves()
        assert len(moves) == 1
        assert moves[0]["type"] == "spostamento"
        assert moves[0]["command"] == "e2"
        assert moves[0]["player"] == "P1"

    def test_record_horizontal_wall(self):
        h = MoveHistory()
        h.record_move(2, "he4")
        assert h.get_all_moves()[0]["type"] == "muro"

    def test_record_vertical_wall(self):
        h = MoveHistory()
        h.record_move(1, "vc3")
        assert h.get_all_moves()[0]["type"] == "muro"

    def test_record_abandon(self):
        h = MoveHistory()
        h.record_move(1, "abbandono")
        assert h.get_all_moves()[0]["type"] == "abbandono"

    def test_record_timeout(self):
        h = MoveHistory()
        h.record_move(2, "timeout")
        assert h.get_all_moves()[0]["type"] == "timeout"

    def test_turn_numbers_sequential(self):
        h = MoveHistory()
        h.record_move(1, "e2")
        h.record_move(2, "e8")
        moves = h.get_all_moves()
        assert moves[0]["turn"] == "1"
        assert moves[1]["turn"] == "2"

    def test_empty_history(self):
        h = MoveHistory()
        assert h.get_all_moves() == []
