import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pytest
from src.board import QuoridorBoard
from src.win_handler import WinHandler


def make_board(num_players: int = 2) -> QuoridorBoard:
    return QuoridorBoard(num_players)


class TestWinHandler:

    def test_no_winner_at_start(self):
        b = make_board(2)
        assert WinHandler.check_win(b) == 0

    def test_p1_wins_at_row8(self):
        b = make_board(2)
        b.positions[1] = [8, 4]
        assert WinHandler.check_win(b) == 1

    def test_p1_not_winner_at_row7(self):
        b = make_board(2)
        b.positions[1] = [7, 4]
        assert WinHandler.check_win(b) == 0

    def test_p2_wins_at_row0(self):
        b = make_board(2)
        b.positions[2] = [0, 4]
        assert WinHandler.check_win(b) == 2

    def test_p2_not_winner_at_row1(self):
        b = make_board(2)
        b.positions[2] = [1, 4]
        assert WinHandler.check_win(b) == 0

    def test_p3_wins_at_col8(self):
        b = make_board(4)
        b.positions[3] = [4, 8]
        assert WinHandler.check_win(b) == 3

    def test_p4_wins_at_col0(self):
        b = make_board(4)
        b.positions[4] = [4, 0]
        assert WinHandler.check_win(b) == 4

    def test_last_player_standing_wins(self):
        b = make_board(4)
        b.eliminate_player(1)
        b.eliminate_player(2)
        b.eliminate_player(3)
        assert WinHandler.check_win(b) == 4

    def test_p1_still_wins_in_4p(self):
        b = make_board(4)
        b.positions[1] = [8, 4]
        assert WinHandler.check_win(b) == 1
