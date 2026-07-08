import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.gui.app import _Stopwatch, _fmt_seconds


class TestFmtSeconds:

    def test_typical_value(self):
        assert _fmt_seconds(65.0) == "01:05"

    def test_zero(self):
        assert _fmt_seconds(0.0) == "00:00"

    def test_negative(self):
        assert _fmt_seconds(-5.0) == "00:00"

    def test_exactly_one_minute(self):
        assert _fmt_seconds(60.0) == "01:00"

    def test_near_ten_minutes(self):
        assert _fmt_seconds(599.0) == "09:59"

    def test_truncation_not_rounding(self):
        assert _fmt_seconds(59.9) == "00:59"


class TestStopwatchInit:

    def test_initial_elapsed_zero(self):
        sw = _Stopwatch(2)
        assert sw.get_elapsed(1) == 0.0
        assert sw.get_elapsed(2) == 0.0

    def test_initial_4players(self):
        sw = _Stopwatch(4)
        for p in range(1, 5):
            assert sw.get_elapsed(p) == 0.0

    def test_elapsed_unknown_player_returns_zero(self):
        sw = _Stopwatch(2)
        assert sw.get_elapsed(99) == 0.0


class TestStopwatchTiming:

    def test_elapsed_increases_after_turn(self):
        sw = _Stopwatch(2)
        sw.start_turn(1)
        time.sleep(0.05)
        sw.stop_turn()
        assert sw.get_elapsed(1) > 0.0

    def test_elapsed_during_turn(self):
        sw = _Stopwatch(2)
        sw.start_turn(1)
        time.sleep(0.05)
        mid = sw.get_elapsed(1)
        sw.stop_turn()
        assert mid > 0.0

    def test_inactive_player_unchanged(self):
        sw = _Stopwatch(2)
        sw.start_turn(1)
        time.sleep(0.05)
        sw.stop_turn()
        assert sw.get_elapsed(2) == 0.0

    def test_stop_without_start_no_error(self):
        sw = _Stopwatch(2)
        sw.stop_turn()
        assert sw.get_elapsed(1) == 0.0

    def test_start_twice_accumulates(self):
        sw = _Stopwatch(2)
        sw.start_turn(1)
        time.sleep(0.03)
        sw.start_turn(2)
        time.sleep(0.03)
        sw.stop_turn()
        assert sw.get_elapsed(1) > 0.0
        assert sw.get_elapsed(2) > 0.0


class TestStopwatchRemovePlayer:

    def test_remove_player_deletes_entry(self):
        sw = _Stopwatch(2)
        sw.remove_player(1)
        assert sw.get_elapsed(1) == 0.0

    def test_remove_active_player_resets_state(self):
        sw = _Stopwatch(2)
        sw.start_turn(1)
        sw.remove_player(1)
        assert sw._active is None
        assert sw._start is None

    def test_remove_absent_player_no_error(self):
        sw = _Stopwatch(2)
        sw.remove_player(99)
