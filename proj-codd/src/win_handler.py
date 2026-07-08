class WinHandler:
    """Handles win conditions for Quoridor in 2 and 4-player modes. No UI logic."""

    @classmethod
    def check_win(cls, board) -> int:
        """Return the winner's player number (1–4), or 0 if no winner yet.

        P1 (starts row 0) wins by reaching row 8.
        P2 (starts row 8) wins by reaching row 0.
        P3 (starts col 0) wins by reaching col 8.
        P4 (starts col 8) wins by reaching col 0.
        In 4-player mode, also returns the last remaining player
        if all others were eliminated.
        """
        active = board.active_players

        if 1 in active and board.positions[1][0] == 8:
            return 1
        if 2 in active and board.positions[2][0] == 0:
            return 2
        if board.num_players == 4:
            if 3 in active and board.positions[3][1] == 8:
                return 3
            if 4 in active and board.positions[4][1] == 0:
                return 4
            if len(active) == 1:
                return active[0]

        return 0