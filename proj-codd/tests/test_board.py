import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pytest
from src.board import QuoridorBoard


def make_board(num_players: int = 2) -> QuoridorBoard:
    return QuoridorBoard(num_players)


class TestQuoridorBoardInit:

    def test_init_2_players_positions(self):
        b = make_board(2)
        assert b.positions[1] == [0, 4]
        assert b.positions[2] == [8, 4]

    def test_init_2_players_walls(self):
        b = make_board(2)
        assert b.walls_left[1] == 10
        assert b.walls_left[2] == 10

    def test_init_4_players_positions(self):
        b = make_board(4)
        assert b.positions[3] == [4, 0]
        assert b.positions[4] == [4, 8]

    def test_init_4_players_walls(self):
        b = make_board(4)
        for p in range(1, 5):
            assert b.walls_left[p] == 5

    def test_init_turn_is_player1(self):
        b = make_board(2)
        assert b.turn == 1

    def test_init_no_walls(self):
        b = make_board(2)
        assert len(b.h_walls) == 0
        assert len(b.v_walls) == 0


class TestAdvanceTurn:

    def test_advance_turn_2_players(self):
        b = make_board(2)
        b.advance_turn()
        assert b.turn == 2

    def test_advance_turn_wraps_around(self):
        b = make_board(2)
        b.advance_turn()
        b.advance_turn()
        assert b.turn == 1

    def test_advance_turn_4_players_cycle(self):
        b = make_board(4)
        expected = [2, 3, 4, 1]
        for exp in expected:
            b.advance_turn()
            assert b.turn == exp


class TestEliminatePlayer:

    def test_eliminate_current_player(self):
        b = make_board(4)
        b.eliminate_player(1)
        assert 1 not in b.active_players

    def test_eliminate_already_absent_player(self):
        b = make_board(2)
        b.eliminate_player(1)
        b.eliminate_player(1)
        assert 1 not in b.active_players

    def test_eliminate_adjusts_turn_index(self):
        b = make_board(4)
        b.eliminate_player(1)
        assert b.turn == 2

    def test_eliminate_until_one_remains(self):
        b = make_board(2)
        b.eliminate_player(1)
        assert b.active_players == [2]
