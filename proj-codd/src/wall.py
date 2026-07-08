class WallHandler:
    """Handles wall placement logic for Quoridor. No UI logic."""

    @classmethod
    def process_wall(cls, board, command: str) -> tuple[bool, str]:
        """Validate and place a wall.

        Returns (True, "") on success, or (False, error_message) on failure.
        """
        if len(command) != 3 or command[0] not in ["h", "v"]:
            return (
                False,
                "Comando invalido: usa il formato per la coordinata"
                " (es. 'he3' o 'vc2').",
            )

        orientation = command[0]
        col_str, row_str = command[1], command[2]

        if not ("a" <= col_str <= "h" and "1" <= row_str <= "8"):
            return (
                False,
                "Piazzamento invalido: il muro supera i confini destri"
                " o superiori della scacchiera.",
            )

        c = ord(col_str) - ord("a")
        r = int(row_str) - 1

        current_player = board.turn
        if board.walls_left[current_player] <= 0:
            return False, "Piazzamento invalido: muri esauriti."

        if orientation == "h":
            if (
                (r, c) in board.h_walls
                or (r, c - 1) in board.h_walls
                or (r, c + 1) in board.h_walls
            ):
                return (
                    False,
                    "Piazzamento invalido: il muro si sovrappone"
                    " a un altro muro orizzontale.",
                )
            if (r, c) in board.v_walls:
                return (
                    False,
                    "Piazzamento invalido: il muro incrocia a croce"
                    " un muro verticale esistente.",
                )
            board.h_walls.add((r, c))

        elif orientation == "v":
            if (
                (r, c) in board.v_walls
                or (r - 1, c) in board.v_walls
                or (r + 1, c) in board.v_walls
            ):
                return (
                    False,
                    "Piazzamento invalido: il muro si sovrappone"
                    " a un altro muro verticale.",
                )
            if (r, c) in board.h_walls:
                return (
                    False,
                    "Piazzamento invalido: il muro incrocia a croce"
                    " un muro orizzontale esistente.",
                )
            board.v_walls.add((r, c))

        board.walls_left[current_player] -= 1
        board.advance_turn()
        return True, ""