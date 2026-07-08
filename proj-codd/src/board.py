from src.movement import MovementHandler
from src.wall import WallHandler


class QuoridorBoard:
    """Represents the Quoridor game board state for 2 or 4 players. No UI logic."""

    def __init__(self, num_players: int = 2):
        self.num_players = num_players
        walls_each = 10 if num_players == 2 else 5

        self.positions = {
            1: [0, 4],
            2: [8, 4],
        }
        self.walls_left = {
            1: walls_each,
            2: walls_each,
        }

        if num_players == 4:
            self.positions[3] = [4, 0]
            self.positions[4] = [4, 8]
            self.walls_left[3] = walls_each
            self.walls_left[4] = walls_each

        self.active_players: list[int] = list(range(1, num_players + 1))
        self.h_walls: set[tuple[int, int]] = set()
        self.v_walls: set[tuple[int, int]] = set()
        self.turn_index: int = 0

    @property
    def turn(self) -> int:
        return self.active_players[self.turn_index]

    def advance_turn(self) -> None:
        self.turn_index = (self.turn_index + 1) % len(self.active_players)

    def eliminate_player(self, player: int) -> None:
        if player not in self.active_players:
            return
        idx = self.active_players.index(player)
        self.active_players.remove(player)
        if self.turn_index >= len(self.active_players):
            self.turn_index = 0
        elif idx < self.turn_index:
            self.turn_index -= 1

    def process_move(self, command: str) -> tuple[bool, str]:
        """Process a move or wall placement command.

        Returns (success: bool, error_message: str).
        On success, error_message is an empty string.
        Wall commands are exactly 3 chars starting with 'h' or 'v'.
        Movement commands are exactly 2 chars (col + row).
        """
        if len(command) == 3 and command[0] in ("h", "v"):
            return WallHandler.process_wall(self, command)
        return MovementHandler.process_move(self, command)