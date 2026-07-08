import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import pytest
from src.timer import GameTimer


class TestGameTimer:

    def test_initial_time(self):
        t = GameTimer(300, 2)
        assert t.time_left[1] == 300.0
        assert t.time_left[2] == 300.0

    def test_time_decreases_after_turn(self):
        t = GameTimer(300, 2)
        t.start_turn(1)
        time.sleep(0.05)
        t.stop_turn()
        assert t.time_left[1] < 300.0

    def test_get_remaining_during_turn(self):
        t = GameTimer(300, 2)
        t.start_turn(1)
        time.sleep(0.05)
        remaining = t.get_remaining(1)
        assert remaining < 300.0
        t.stop_turn()

    def test_is_expired_when_zero(self):
        t = GameTimer(0, 2)
        assert t.is_expired(1) is True

    def test_not_expired_with_time_left(self):
        t = GameTimer(300, 2)
        assert t.is_expired(1) is False

    def test_remove_player(self):
        t = GameTimer(300, 2)
        t.remove_player(1)
        assert 1 not in t.time_left

    def test_stop_without_start(self):
        t = GameTimer(300, 2)
        t.stop_turn()
        assert t.time_left[1] == 300.0

    def test_remove_active_player_resets(self):
        t = GameTimer(300, 2)
        t.start_turn(1)
        t.remove_player(1)
        assert t._active_player is None
        assert t._turn_start is None

    def test_time_never_negative(self):
        t = GameTimer(0, 2)
        t.start_turn(1)
        time.sleep(0.02)
        t.stop_turn()
        assert t.time_left[1] == 0.0
