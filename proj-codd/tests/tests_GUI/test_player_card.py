import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.gui.player_card import PlayerCard, TIMER_BAR_WIDTH, PLAYER_COLORS_HEX


def make_card(player=1, walls_max=10, timed=False, max_seconds=300):
    return PlayerCard(player, walls_max, timed=timed, max_seconds=max_seconds)


class TestPlayerCardInit:

    def test_defaults(self):
        c = make_card(player=1, walls_max=10)
        assert c.player == 1
        assert c.walls_max == 10
        assert c.walls_left == 10
        assert c.is_turn is False
        assert c.is_eliminated is False

    def test_4player_walls(self):
        c = make_card(player=3, walls_max=5)
        assert c.walls_max == 5
        assert c.walls_left == 5

    def test_max_seconds_zero_uses_default(self):
        c = make_card(timed=True, max_seconds=0)
        assert c.max_seconds == 300

    def test_timed_flag(self):
        c = make_card(timed=True, max_seconds=300)
        assert c.timed is True

    def test_initial_remaining_equals_max(self):
        c = make_card(timed=True, max_seconds=300)
        assert c._remaining_s == 300.0


class TestPlayerCardUpdateState:

    def test_basic_update(self):
        c = make_card()
        c.update_state(walls_left=7, is_turn=True, time_text="04:30")
        assert c.walls_left == 7
        assert c.is_turn is True
        assert c.time_text == "04:30"

    def test_active_class_added_on_turn(self):
        c = make_card()
        c.update_state(walls_left=10, is_turn=True, time_text="--:--")
        assert c.has_class("-active")

    def test_active_class_removed_off_turn(self):
        c = make_card()
        c.update_state(walls_left=10, is_turn=True,  time_text="--:--")
        c.update_state(walls_left=10, is_turn=False, time_text="--:--")
        assert not c.has_class("-active")

    def test_eliminated_class_added(self):
        c = make_card()
        c.update_state(walls_left=0, is_turn=False, time_text="--:--", is_eliminated=True)
        assert c.has_class("-eliminated")

    def test_eliminated_class_removed(self):
        c = make_card()
        c.update_state(walls_left=0, is_turn=False, time_text="--:--", is_eliminated=True)
        c.update_state(walls_left=0, is_turn=False, time_text="--:--", is_eliminated=False)
        assert not c.has_class("-eliminated")

    def test_eliminated_player_not_active(self):
        c = make_card()
        c.update_state(walls_left=0, is_turn=True, time_text="--:--", is_eliminated=True)
        assert not c.has_class("-active")

    def test_remaining_seconds_updated(self):
        c = make_card(timed=True, max_seconds=300)
        c.update_state(walls_left=10, is_turn=False, time_text="02:00", remaining_seconds=120.0)
        assert c._remaining_s == 120.0

    def test_remaining_seconds_negative_unchanged(self):
        c = make_card(timed=True, max_seconds=300)
        c.update_state(walls_left=10, is_turn=False, time_text="--:--", remaining_seconds=-1.0)
        assert c._remaining_s == 300.0


class TestPlayerCardRender:

    def test_render_contains_player_name(self):
        c = make_card(player=1)
        text = c.render()
        assert "P1" in text.plain

    def test_render_eliminated_contains_label(self):
        c = make_card(player=2)
        c.update_state(walls_left=0, is_turn=False, time_text="--:--", is_eliminated=True)
        text = c.render()
        assert "eliminato" in text.plain

    def test_render_active_turn_contains_turno(self):
        c = make_card(player=1)
        c.update_state(walls_left=10, is_turn=True, time_text="--:--")
        text = c.render()
        assert "TURNO" in text.plain

    def test_render_no_timer_when_not_timed(self):
        c = make_card(timed=False)
        c.update_state(walls_left=10, is_turn=False, time_text="05:00")
        text = c.render()
        assert "05:00" not in text.plain

    def test_render_shows_timer_when_timed(self):
        c = make_card(timed=True, max_seconds=300)
        c.update_state(walls_left=10, is_turn=False, time_text="04:59", remaining_seconds=299.0)
        text = c.render()
        assert "04:59" in text.plain

    def test_render_zero_walls(self):
        c = make_card(walls_max=10)
        c.update_state(walls_left=0, is_turn=False, time_text="--:--")
        text = c.render()
        assert "0/10" in text.plain

    def test_render_timer_bar_empty_at_zero(self):
        c = make_card(timed=True, max_seconds=300)
        c.update_state(walls_left=10, is_turn=False, time_text="00:00", remaining_seconds=0.0)
        text = c.render()
        assert "\u2591" * TIMER_BAR_WIDTH in text.plain

    def test_render_timer_bar_full_at_max(self):
        c = make_card(timed=True, max_seconds=300)
        c.update_state(walls_left=10, is_turn=False, time_text="05:00", remaining_seconds=300.0)
        text = c.render()
        assert "\u2588" * TIMER_BAR_WIDTH in text.plain
