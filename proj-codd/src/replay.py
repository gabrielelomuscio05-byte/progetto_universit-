from src.board import QuoridorBoard


class ReplayHandler:
    """Rebuilds board snapshots from move history to support step-by-step replay.

    Le pseudo-mosse "abbandono"/"timeout" eliminano il giocatore invece di
    chiamare process_move, così il replay non si interrompe quando un
    giocatore viene rimosso dalla partita.
    """

    def __init__(self, moves: list[dict[str, str]], num_players: int = 2) -> None:
        self._moves = moves
        self._num_players = num_players
        self._snapshots: list[QuoridorBoard] = self._build_snapshots()

    def _build_snapshots(self) -> list[QuoridorBoard]:
        board = QuoridorBoard(self._num_players)
        snapshots = [self._copy_board(board)]
        for move in self._moves:
            command = move["command"]
            if command in ("abbandono", "timeout"):
                # Eliminazione: rimuovi il giocatore indicato dal record.
                # `player` è del formato "P1", "P2", ...
                try:
                    player_num = int(move["player"][1:])
                    board.eliminate_player(player_num)
                except (ValueError, IndexError, KeyError):
                    pass
            else:
                board.process_move(command)
            snapshots.append(self._copy_board(board))
        return snapshots

    @staticmethod
    def _copy_board(board: QuoridorBoard) -> QuoridorBoard:
        snap = QuoridorBoard(board.num_players)
        snap.positions = {p: list(pos) for p, pos in board.positions.items()}
        snap.walls_left = dict(board.walls_left)
        snap.active_players = list(board.active_players)
        snap.h_walls = set(board.h_walls)
        snap.v_walls = set(board.v_walls)
        snap.turn_index = board.turn_index
        return snap

    def total_moves(self) -> int:
        return len(self._moves)

    def get_snapshot(self, index: int) -> QuoridorBoard:
        return self._snapshots[index]

    def get_move_info(self, index: int) -> dict[str, str] | None:
        return self._moves[index - 1] if index > 0 else None