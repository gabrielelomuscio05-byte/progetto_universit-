import time


class GameTimer:
    """Manages independent countdown timers for each player in chess-clock style."""

    def __init__(self, seconds_per_player: int, num_players: int = 2):
        self.time_left = {
            p: float(seconds_per_player) for p in range(1, num_players + 1)
        }
        self._turn_start: float | None = None
        self._active_player: int | None = None

    def start_turn(self, player: int) -> None:
        """Start counting down for the given player."""
        self._active_player = player
        self._turn_start = time.monotonic()

    def stop_turn(self) -> None:
        """Stop the current player's timer and deduct elapsed time."""
        if self._active_player is None or self._turn_start is None:
            return
        elapsed = time.monotonic() - self._turn_start
        self.time_left[self._active_player] = max(
            0.0, self.time_left[self._active_player] - elapsed
        )
        self._active_player = None
        self._turn_start = None

    def get_remaining(self, player: int) -> float:
        """Return the remaining seconds for the given player.

        Accounts for the ongoing turn.
        """
        remaining = self.time_left[player]
        if self._active_player == player and self._turn_start is not None:
            elapsed = time.monotonic() - self._turn_start
            remaining = max(0.0, remaining - elapsed)
        return remaining

    def is_expired(self, player: int) -> bool:
        """Return True if the given player has run out of time."""
        return self.get_remaining(player) <= 0.0

    def remove_player(self, player: int) -> None:
        """Remove a player's timer entry when they are eliminated."""
        self.time_left.pop(player, None)
        if self._active_player == player:
            self._active_player = None
            self._turn_start = None