import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pytest
from src.board import QuoridorBoard
from src.movement import MovementHandler
from src.history import MoveHistory
from src.timer import GameTimer
from src.replay import ReplayHandler
from src.win_handler import WinHandler


def make_board(num_players: int = 2) -> QuoridorBoard:
    return QuoridorBoard(num_players)


class TestIntegrationFullGame:

    def test_full_2player_win_p1(self):
        b = make_board(2)
        h = MoveHistory()
        moves_p1 = ["e2", "e4", "e6", "e8"]
        moves_p2 = ["e7", "e5", "e3", "e1"]
        for m1, m2 in zip(moves_p1, moves_p2):
            ok, _ = b.process_move(m1)
            assert ok
            h.record_move(1, m1)
            winner = WinHandler.check_win(b)
            if winner:
                break
            ok, _ = b.process_move(m2)
            assert ok
            h.record_move(2, m2)
        assert b.positions[1][0] == 8
        assert WinHandler.check_win(b) == 1

    def test_wall_blocks_opponent_path(self):
        b = make_board(2)
        b.positions[1] = [0, 4]
        b.positions[2] = [8, 4]
        ok, _ = b.process_move("he7")
        assert ok
        b.h_walls.add((6, 4))
        assert MovementHandler._is_wall_between(b, 7, 4, 6, 4) is True

    def test_history_records_complete_game(self):
        b = make_board(2)
        h = MoveHistory()
        commands = [("e2", 1), ("e8", 2), ("he3", 1)]
        for cmd, player in commands:
            b.process_move(cmd)
            h.record_move(player, cmd)
        moves = h.get_all_moves()
        assert len(moves) == 3
        assert moves[2]["type"] == "muro"

    def test_replay_reconstructs_wall_placement(self):
        moves = [{"player": "P1", "turn": "1", "type": "muro", "command": "he4"}]
        r = ReplayHandler(moves, 2)
        assert (3, 4) in r.get_snapshot(1).h_walls

    def test_timer_integration_with_board(self):
        b = make_board(2)
        t = GameTimer(300, 2)
        t.start_turn(b.turn)
        b.process_move("e2")
        t.stop_turn()
        b.eliminate_player(2)
        t.remove_player(2)
        assert 2 not in t.time_left
        assert WinHandler.check_win(b) == 1

    def test_4player_elimination_sequence(self):
        b = make_board(4)
        b.eliminate_player(3)
        b.eliminate_player(4)
        assert b.active_players == [1, 2]
        assert WinHandler.check_win(b) == 0

    def test_process_move_delegates_correctly(self):
        b = make_board(2)
        ok, _ = b.process_move("he3")
        assert ok is True
        assert (2, 4) in b.h_walls
        ok, _ = b.process_move("e8")
        assert ok is True
        assert b.positions[2] == [7, 4]
