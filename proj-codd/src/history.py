class MoveHistory:
    """Manages the history collection and structural storage of game moves.

    Supporta tre tipi di voci:
      - "spostamento": comando tipo "e2"
      - "muro":        comando tipo "he4" o "vc3"
      - "abbandono"/"timeout": pseudo-mossa per eliminazione giocatore
        (il `command` coincide con il tipo: "abbandono" o "timeout").
    """

    def __init__(self) -> None:
        self.moves: list[dict[str, str]] = []

    def record_move(self, player: int, command: str) -> None:
        if command in ("abbandono", "timeout"):
            move_type = command
        elif command.startswith(("h", "v")):
            move_type = "muro"
        else:
            move_type = "spostamento"
        self.moves.append({
            "player": f"P{player}",
            "turn": str(len(self.moves) + 1),
            "type": move_type,
            "command": command,
        })

    def get_all_moves(self) -> list[dict[str, str]]:
        return self.moves