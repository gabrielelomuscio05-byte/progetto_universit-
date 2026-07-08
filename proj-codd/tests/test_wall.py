import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pytest
from src.board import QuoridorBoard


def make_board(num_players: int = 2) -> QuoridorBoard:
    return QuoridorBoard(num_players)


class TestWallPlacementValid:

    def test_place_horizontal_wall(self):
        b = make_board(2)
        ok, err = b.process_move("he4")
        assert ok is True
        assert (3, 4) in b.h_walls

    def test_place_vertical_wall(self):
        b = make_board(2)
        ok, err = b.process_move("vc4")
        assert ok is True
        assert (3, 2) in b.v_walls

    def test_wall_decrements_counter(self):
        b = make_board(2)
        b.process_move("he4")
        assert b.walls_left[1] == 9

    def test_wall_advances_turn(self):
        b = make_board(2)
        b.process_move("he4")
        assert b.turn == 2

    def test_wall_col_max_valid(self):
        b = make_board(2)
        ok, _ = b.process_move("hh1")
        assert ok is True

    def test_wall_row_max_valid(self):
        b = make_board(2)
        ok, _ = b.process_move("ha8")
        assert ok is True


class TestWallPlacementInvalid:

    def test_wall_col_above_max(self):
        b = make_board(2)
        ok, err = b.process_move("hi4")
        assert ok is False

    def test_wall_row_above_max(self):
        b = make_board(2)
        ok, err = b.process_move("ha9")
        assert ok is False

    def test_wall_overlap_same_position(self):
        b = make_board(2)
        b.process_move("he4")
        b.advance_turn()
        b.h_walls.discard((3, 4))
        b.h_walls.add((3, 4))
        ok, err = b.process_move("he4")
        assert ok is False

    def test_wall_cross_h_v(self):
        b = make_board(2)
        b.process_move("he4")
        ok, err = b.process_move("ve4")
        assert ok is False

    def test_wall_no_walls_left(self):
        b = make_board(2)
        b.walls_left[1] = 0
        ok, err = b.process_move("he4")
        assert ok is False

    def test_wall_overlap_offset_plus1(self):
        b = make_board(2)
        b.process_move("he4")
        ok, err = b.process_move("he5")
        assert ok is False

    def test_wall_overlap_offset_minus1(self):
        b = make_board(2)
        b.process_move("he4")
        ok, err = b.process_move("he3")
        assert ok is False
