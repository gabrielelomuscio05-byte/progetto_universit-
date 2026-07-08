import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.board import QuoridorBoard
from src.gui.board_widget import (
    BoardWidget,
    _is_jump_move,
    CELL_W, CELL_H, GUTTER,
    COL_CYCLE, ROW_CYCLE,
    LABEL_LEFT, LABEL_TOP,
    BOARD_W, BOARD_H,
    HOVER_CELL_BG, CELL_BG,
    PLAYER_COLORS_HEX,
)


def make_board(n=2):
    return QuoridorBoard(n)


def make_widget(n=2):
    return BoardWidget(make_board(n))


class TestLayoutConstants:

    def test_col_cycle(self):
        assert COL_CYCLE == CELL_W + GUTTER

    def test_row_cycle(self):
        assert ROW_CYCLE == CELL_H + GUTTER

    def test_board_width(self):
        assert BOARD_W == 9 * CELL_W + 8 * GUTTER

    def test_board_height(self):
        assert BOARD_H == 9 * CELL_H + 8 * GUTTER


class TestIsJumpMove:

    def test_jump_detected(self):
        b = make_board(2)
        b.positions[1] = [3, 4]
        b.positions[2] = [4, 4]
        assert _is_jump_move(b, 3, 4, 5, 4) is True

    def test_no_jump_distance_one(self):
        b = make_board(2)
        b.positions[1] = [3, 4]
        b.positions[2] = [7, 4]
        assert _is_jump_move(b, 3, 4, 4, 4) is False

    def test_no_jump_diagonal(self):
        b = make_board(2)
        assert _is_jump_move(b, 3, 3, 5, 5) is False

    def test_no_jump_empty_middle(self):
        b = make_board(2)
        b.positions[1] = [3, 4]
        b.positions[2] = [7, 4]
        assert _is_jump_move(b, 3, 4, 5, 4) is False

    def test_no_jump_distance_three(self):
        b = make_board(2)
        assert _is_jump_move(b, 0, 4, 3, 4) is False


class TestMouseToTarget:

    def test_click_cell_0_0(self):
        w = make_widget()
        x = LABEL_LEFT + CELL_W // 2
        y = LABEL_TOP  + CELL_H // 2
        assert w._mouse_to_target(x, y) == ("cell", 0, 0)

    def test_click_hwall_row0(self):
        w = make_widget()
        x = LABEL_LEFT + CELL_W // 2
        y = LABEL_TOP  + CELL_H
        result = w._mouse_to_target(x, y)
        assert result is not None and result[0] == "hwall"

    def test_click_vwall_col0(self):
        w = make_widget()
        x = LABEL_LEFT + CELL_W
        y = LABEL_TOP  + CELL_H // 2
        result = w._mouse_to_target(x, y)
        assert result is not None and result[0] == "vwall"

    def test_click_outside_left(self):
        w = make_widget()
        assert w._mouse_to_target(0, LABEL_TOP + 1) is None

    def test_click_outside_top(self):
        w = make_widget()
        assert w._mouse_to_target(LABEL_LEFT + 1, 0) is None

    def test_click_outside_right(self):
        w = make_widget()
        assert w._mouse_to_target(LABEL_LEFT + BOARD_W + 5, LABEL_TOP + CELL_H // 2) is None

    def test_click_outside_bottom(self):
        w = make_widget()
        assert w._mouse_to_target(LABEL_LEFT + CELL_W // 2, LABEL_TOP + BOARD_H + 5) is None

    def test_click_exact_top_left_corner(self):
        w = make_widget()
        assert w._mouse_to_target(LABEL_LEFT, LABEL_TOP) == ("cell", 0, 0)

    def test_click_cell_8_8(self):
        w = make_widget()
        x = LABEL_LEFT + 8 * COL_CYCLE + CELL_W // 2
        y = LABEL_TOP  + 8 * ROW_CYCLE + CELL_H // 2
        assert w._mouse_to_target(x, y) == ("cell", 8, 8)


class TestWallValid:

    def test_hwall_valid_free(self):
        assert make_widget()._wall_valid("h", 3, 4) is True

    def test_vwall_valid_free(self):
        assert make_widget()._wall_valid("v", 3, 4) is True

    def test_hwall_invalid_occupied(self):
        w = make_widget()
        w.board.h_walls.add((3, 4))
        assert w._wall_valid("h", 3, 4) is False

    def test_vwall_invalid_occupied(self):
        w = make_widget()
        w.board.v_walls.add((3, 4))
        assert w._wall_valid("v", 3, 4) is False

    def test_hwall_invalid_no_walls(self):
        w = make_widget()
        w.board.walls_left[1] = 0
        assert w._wall_valid("h", 3, 4) is False

    def test_hwall_row_max_valid(self):
        assert make_widget()._wall_valid("h", 7, 0) is True

    def test_hwall_row_above_max_invalid(self):
        assert make_widget()._wall_valid("h", 8, 0) is False

    def test_hwall_col_max_valid(self):
        assert make_widget()._wall_valid("h", 0, 7) is True

    def test_hwall_col_above_max_invalid(self):
        assert make_widget()._wall_valid("h", 0, 8) is False


class TestGoalColors:

    def test_goal_row_8_p1_active(self):
        assert make_widget(2)._goal_row_color(8) == PLAYER_COLORS_HEX[1]

    def test_goal_row_0_p2_active(self):
        assert make_widget(2)._goal_row_color(0) == PLAYER_COLORS_HEX[2]

    def test_goal_row_middle_none(self):
        assert make_widget(2)._goal_row_color(4) is None

    def test_goal_row_8_p1_eliminated(self):
        w = make_widget(2)
        w.board.eliminate_player(1)
        assert w._goal_row_color(8) is None

    def test_goal_col_8_p3_active(self):
        assert make_widget(4)._goal_column_color(8) == PLAYER_COLORS_HEX[3]

    def test_goal_col_0_p4_active(self):
        assert make_widget(4)._goal_column_color(0) == PLAYER_COLORS_HEX[4]

    def test_goal_col_2player_none(self):
        w = make_widget(2)
        assert w._goal_column_color(0) is None
        assert w._goal_column_color(8) is None


class TestCellBackground:

    def test_normal_cell_bg(self):
        w = make_widget()
        w.set_mode("move")
        assert w._cell_bg(4, 4) == CELL_BG

    def test_hover_cell_bg(self):
        w = make_widget()
        w.set_mode("move")
        w.hover_target = ("cell", 1, 4)
        assert w._cell_bg(1, 4) == HOVER_CELL_BG

    def test_hover_unreachable_cell_bg(self):
        w = make_widget()
        w.set_mode("move")
        w.hover_target = ("cell", 0, 0)
        assert w._cell_bg(0, 0) == CELL_BG

    def test_hover_in_wall_mode_no_cell_hover(self):
        w = make_widget()
        w.set_mode("hwall")
        w.hover_target = ("cell", 1, 4)
        assert w._cell_bg(1, 4) == CELL_BG


class TestBoardWidgetStateChanges:

    def test_set_board_updates(self):
        w = make_widget()
        new_board = make_board(2)
        new_board.positions[1] = [5, 5]
        w.set_board(new_board)
        assert w.board.positions[1] == [5, 5]

    def test_set_mode_updates(self):
        w = make_widget()
        w.set_mode("hwall")
        assert w.mode == "hwall"

    def test_set_mode_resets_hover(self):
        w = make_widget()
        w.hover_target = ("cell", 1, 4)
        w.set_mode("vwall")
        assert w.hover_target is None

    def test_reachable_disabled_mode(self):
        w = make_widget()
        w.set_mode("disabled")
        w.recompute_reachable()
        assert isinstance(w._reachable_cells, set)

    def test_reachable_no_active_players(self):
        w = make_widget()
        w.board.active_players.clear()
        w.recompute_reachable()
        assert w._reachable_cells == set()

    def test_reachable_updates_after_move(self):
        w = make_widget()
        old_reachable = set(w._reachable_cells)
        w.board.process_move("e2")
        w.recompute_reachable()
        assert w._reachable_cells != old_reachable
