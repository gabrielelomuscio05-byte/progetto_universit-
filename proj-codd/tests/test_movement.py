import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pytest
from src.board import QuoridorBoard
from src.movement import MovementHandler


def make_board(num_players: int = 2) -> QuoridorBoard:
    return QuoridorBoard(num_players)


class TestMovementValidCommands:

    def test_move_one_step_down(self):
        b = make_board(2)
        ok, err = b.process_move("e2")
        assert ok is True
        assert err == ""
        assert b.positions[1] == [1, 4]

    def test_move_one_step_right(self):
        b = make_board(2)
        ok, _ = b.process_move("f1")
        assert ok is True
        assert b.positions[1] == [0, 5]

    def test_move_one_step_left(self):
        b = make_board(2)
        ok, _ = b.process_move("d1")
        assert ok is True
        assert b.positions[1] == [0, 3]

    def test_move_advances_turn(self):
        b = make_board(2)
        b.process_move("e2")
        assert b.turn == 2


class TestMovementInvalidCommands:

    def test_move_command_too_short(self):
        b = make_board(2)
        ok, err = b.process_move("e")
        assert ok is False
        assert err != ""

    def test_move_command_too_long(self):
        b = make_board(2)
        ok, err = b.process_move("e12")
        assert ok is False

    def test_move_col_below_min(self):
        b = make_board(2)
        ok, err = b.process_move("`1")
        assert ok is False

    def test_move_col_above_max(self):
        b = make_board(2)
        ok, err = b.process_move("j1")
        assert ok is False

    def test_move_col_min_valid(self):
        b = make_board(2)
        ok, err = b.process_move("a1")
        assert ok is False

    def test_move_row_min_valid_occupied(self):
        b = make_board(2)
        ok, err = b.process_move("e1")
        assert ok is False

    def test_move_row_zero_invalid(self):
        b = make_board(2)
        ok, err = b.process_move("e0")
        assert ok is False

    def test_move_row_nine_valid_boundary(self):
        b = make_board(2)
        ok, err = b.process_move("e9")
        assert ok is False

    def test_move_to_occupied_cell(self):
        b = make_board(2)
        b.positions[1] = [4, 4]
        b.positions[2] = [4, 5]
        ok, err = b.process_move("f5")
        assert ok is False

    def test_move_diagonal_rejected(self):
        b = make_board(2)
        ok, err = b.process_move("f2")
        assert ok is False


class TestMovementJump:

    def test_jump_over_adjacent_opponent(self):
        b = make_board(2)
        b.positions[1] = [3, 4]
        b.positions[2] = [4, 4]
        ok, err = b.process_move("e6")
        assert ok is True
        assert b.positions[1] == [5, 4]

    def test_jump_without_adjacent_opponent_rejected(self):
        b = make_board(2)
        b.positions[1] = [3, 4]
        b.positions[2] = [7, 4]
        ok, err = b.process_move("e6")
        assert ok is False

    def test_jump_blocked_by_wall_before_mid(self):
        b = make_board(2)
        b.positions[1] = [3, 4]
        b.positions[2] = [4, 4]
        b.h_walls.add((3, 4))
        ok, err = b.process_move("e6")
        assert ok is False

    def test_jump_blocked_by_wall_after_mid(self):
        b = make_board(2)
        b.positions[1] = [3, 4]
        b.positions[2] = [4, 4]
        b.h_walls.add((4, 4))
        ok, err = b.process_move("e6")
        assert ok is False


class TestWallBetween:

    def test_no_wall_horizontal(self):
        b = make_board(2)
        assert MovementHandler._is_wall_between(b, 0, 4, 1, 4) is False

    def test_wall_horizontal_blocks(self):
        b = make_board(2)
        b.h_walls.add((0, 4))
        assert MovementHandler._is_wall_between(b, 0, 4, 1, 4) is True

    def test_no_wall_vertical(self):
        b = make_board(2)
        assert MovementHandler._is_wall_between(b, 3, 3, 3, 4) is False

    def test_wall_vertical_blocks(self):
        b = make_board(2)
        b.v_walls.add((3, 3))
        assert MovementHandler._is_wall_between(b, 3, 3, 3, 4) is True

    def test_wall_offset_minus1_blocks(self):
        b = make_board(2)
        b.h_walls.add((0, 3))
        assert MovementHandler._is_wall_between(b, 0, 4, 1, 4) is True

    def test_non_adjacent_returns_false(self):
        b = make_board(2)
        assert MovementHandler._is_wall_between(b, 0, 0, 2, 2) is False
