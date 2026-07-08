import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pytest
from src.replay import ReplayHandler


def make_moves():
    return [
        {"player": "P1", "turn": "1", "type": "spostamento", "command": "e2"},
        {"player": "P2", "turn": "2", "type": "spostamento", "command": "e8"},
    ]


class TestReplayHandler:

    def test_total_moves(self):
        r = ReplayHandler(make_moves(), 2)
        assert r.total_moves() == 2

    def test_snapshot_zero_is_initial(self):
        r = ReplayHandler(make_moves(), 2)
        assert r.get_snapshot(0).positions[1] == [0, 4]

    def test_snapshot_one_after_first_move(self):
        r = ReplayHandler(make_moves(), 2)
        assert r.get_snapshot(1).positions[1] == [1, 4]

    def test_move_info_at_zero_is_none(self):
        r = ReplayHandler(make_moves(), 2)
        assert r.get_move_info(0) is None

    def test_move_info_at_one(self):
        r = ReplayHandler(make_moves(), 2)
        assert r.get_move_info(1)["command"] == "e2"

    def test_abandon_in_replay_eliminates_player(self):
        moves = [{"player": "P1", "turn": "1", "type": "abbandono", "command": "abbandono"}]
        r = ReplayHandler(moves, 2)
        assert 1 not in r.get_snapshot(1).active_players

    def test_timeout_in_replay_eliminates_player(self):
        moves = [{"player": "P2", "turn": "1", "type": "timeout", "command": "timeout"}]
        r = ReplayHandler(moves, 2)
        assert 2 not in r.get_snapshot(1).active_players

    def test_empty_moves_gives_one_snapshot(self):
        r = ReplayHandler([], 2)
        assert r.total_moves() == 0
        assert r.get_snapshot(0).positions[1] == [0, 4]
