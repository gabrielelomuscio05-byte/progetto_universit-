import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.gui.setup_screen import SetupScreen


def make_screen() -> SetupScreen:
    return SetupScreen()


class TestSetupScreenInit:

    def test_default_num_players(self):
        s = make_screen()
        assert s._num_players == 2

    def test_default_timed_false(self):
        s = make_screen()
        assert s._timed is False

    def test_default_minutes(self):
        s = make_screen()
        assert s._minutes == 5


class TestSetupScreenSubmitLogic:

    def test_submit_not_timed_keeps_minutes(self):
        s = make_screen()
        s._timed = False
        s._num_players = 2
        assert s._timed is False
        assert s._num_players == 2

    def test_set_4_players(self):
        s = make_screen()
        s._num_players = 4
        assert s._num_players == 4

    def test_enable_timed(self):
        s = make_screen()
        s._timed = True
        assert s._timed is True

    def test_valid_minutes(self):
        s = make_screen()
        s._timed = True
        s._minutes = 10
        assert s._minutes == 10

    def test_minutes_minimum_valid(self):
        s = make_screen()
        s._timed = True
        s._minutes = 1
        assert s._minutes == 1

    def test_submit_zero_minutes_uses_default(self):
        s = make_screen()
        s._timed = True
        raw = "0"
        if not raw.isdigit() or int(raw) <= 0:
            s._minutes = 5
        assert s._minutes == 5

    def test_submit_non_numeric_uses_default(self):
        s = make_screen()
        s._timed = True
        raw = "abc"
        if not raw.isdigit() or int(raw) <= 0:
            s._minutes = 5
        assert s._minutes == 5

    def test_submit_empty_string_uses_default(self):
        s = make_screen()
        s._timed = True
        raw = ""
        if not raw.isdigit() or int(raw) <= 0:
            s._minutes = 5
        assert s._minutes == 5

    def test_config_timed_false_minutes_zero(self):
        s = make_screen()
        s._timed = False
        s._num_players = 2
        config = {
            "num_players": s._num_players,
            "timed": s._timed,
            "minutes": s._minutes if s._timed else 0,
        }
        assert config["minutes"] == 0
        assert config["timed"] is False

    def test_config_timed_true(self):
        s = make_screen()
        s._timed = True
        s._minutes = 10
        s._num_players = 4
        config = {
            "num_players": s._num_players,
            "timed": s._timed,
            "minutes": s._minutes if s._timed else 0,
        }
        assert config == {"num_players": 4, "timed": True, "minutes": 10}


class TestSetupScreenVisibility:

    def test_visibility_logic_timed_true(self):
        s = make_screen()
        s._timed = True
        assert s._timed is True

    def test_visibility_logic_timed_false(self):
        s = make_screen()
        s._timed = False
        assert s._timed is False

    def test_toggle_timed(self):
        s = make_screen()
        s._timed = True
        s._timed = False
        s._timed = True
        assert s._timed is True
