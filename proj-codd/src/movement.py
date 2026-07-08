class MovementHandler:
    """Handles pawn movement and jump logic for Quoridor. No UI logic."""

    @classmethod
    def _is_wall_between(cls, board, r1: int, c1: int, r2: int, c2: int) -> bool:
        if r1 == r2:
            left_c = min(c1, c2)
            return (r1, left_c) in board.v_walls or (r1 - 1, left_c) in board.v_walls
        elif c1 == c2:
            top_r = min(r1, r2)
            return (top_r, c1) in board.h_walls or (top_r, c1 - 1) in board.h_walls
        return False

    @classmethod
    def process_move(cls, board, command: str) -> tuple[bool, str]:
        """Validate and apply a pawn move.

        Returns (True, "") on success, or (False, error_message) on failure.
        """
        if len(command) != 2:
            return (
                False,
                "Comando invalido: usa il formato per la coordinata (es. 'e2').",
            )

        col_str, row_str = command[0], command[1]
        if not ("a" <= col_str <= "i" and "1" <= row_str <= "9"):
            return False, "Mossa invalida: coordinate fuori dai bordi 9x9."

        c2 = ord(col_str) - ord("a")
        r2 = int(row_str) - 1

        current_player = board.turn
        curr_pos = board.positions[current_player]
        r1, c1 = curr_pos

        all_positions = [board.positions[p] for p in board.active_players]
        if [r2, c2] == curr_pos or [r2, c2] in all_positions:
            return False, "Mossa invalida: casella di destinazione occupata."

        dist = abs(r1 - r2) + abs(c1 - c2)

        occupied_adjacent = [
            pos for pos in all_positions
            if pos != curr_pos and abs(pos[0] - r1) + abs(pos[1] - c1) == 1
        ]

        if dist == 1:
            if cls._is_wall_between(board, r1, c1, r2, c2):
                return False, "Mossa invalida: un muro blocca il passaggio."
        elif dist == 2 and (r1 == r2 or c1 == c2):
            mid_r = (r1 + r2) // 2
            mid_c = (c1 + c2) // 2
            if [mid_r, mid_c] not in occupied_adjacent:
                return (
                    False,
                    "Mossa invalida: casella irraggiungibile per distanza consentita.",
                )
            if cls._is_wall_between(board, r1, c1, mid_r, mid_c) or \
               cls._is_wall_between(board, mid_r, mid_c, r2, c2):
                return (
                    False,
                    "Mossa invalida: salto bloccato dalla presenza di un muro.",
                )
        else:
            return False, "Mossa invalida: mossa illegale non consentita."

        board.positions[current_player] = [r2, c2]
        board.advance_turn()
        return True, ""