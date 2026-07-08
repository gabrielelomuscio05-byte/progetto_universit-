from rich import print
from rich.console import Console
from rich.table import Table

console = Console()

PLAYER_COLORS = {
    1: "green",
    2: "red",
    3: "yellow",
    4: "cyan",
}


class QuoridorView:
    """Handles all output rendering for the Quoridor game. No game logic."""

    def __init__(self, accent_color: str = "blue"):
        self.accent_color = accent_color

    def display_board(self, board, timer=None) -> None:
        header = "    a   b   c   d   e   f   g   h   i"
        print(f"[bold {self.accent_color}]{header}[/bold {self.accent_color}]")

        top_border = "  " + "┏" + "━━━┳" * 8 + "━━━┓"
        print(top_border)

        for r in range(9):
            row_content = f"{r + 1} ┃"
            for c in range(9):
                cell = self._render_cell(board, r, c)
                row_content += cell

                if c < 8:
                    if (r, c) in board.v_walls or (r - 1, c) in board.v_walls:
                        row_content += "█"
                    else:
                        row_content += "┊"
                else:
                    row_content += "┃"
            print(row_content)

            if r < 8:
                row_sep = "  ┣"
                for c in range(9):
                    if (r, c) in board.h_walls or (r, c - 1) in board.h_walls:
                        row_sep += "━━━"
                    else:
                        row_sep += "---"

                    if c < 8:
                        if (r, c) in board.h_walls or (r, c) in board.v_walls:
                            row_sep += "█"
                        else:
                            row_sep += "┼"
                    else:
                        row_sep += "┫"
                print(row_sep)

        bottom_border = "  " + "┗" + "━━━┻" * 8 + "━━━┛"
        print(bottom_border)

        walls_parts = []
        for p in board.active_players:
            color = PLAYER_COLORS.get(p, "white")
            walls_parts.append(
                f"[bold {color}]P{p}: {board.walls_left[p]}[/bold {color}]"
            )
        print(f"\n[bold]Muri disponibili:[/bold] {' | '.join(walls_parts)}")

        if timer is not None:
            self._display_timers(timer, board.active_players)

        turn = board.turn
        color = PLAYER_COLORS.get(turn, "white")
        print(
            f"[bold]Turno corrente:[/bold] "
            f"[bold {color}]Giocatore {turn}[/bold {color}]\n"
        )

    def _render_cell(self, board, r: int, c: int) -> str:
        for p in board.active_players:
            if board.positions[p] == [r, c]:
                color = PLAYER_COLORS.get(p, "white")
                return f"[bold {color}]P{p} [/bold {color}]"
        return " . "

    def _display_timers(self, timer, active_players: list[int]) -> None:
        def fmt(seconds: float) -> str:
            total = int(seconds)
            return f"{total // 60:02d}:{total % 60:02d}"

        parts = []
        for p in active_players:
            t = timer.get_remaining(p)
            c = "red" if t < 30 else "green"
            parts.append(f"[bold {c}]P{p}: {fmt(t)}[/bold {c}]")
        print(f"[bold]Tempo rimanente:[/bold] {' | '.join(parts)}")

    def show_history(self, moves: list[dict[str, str]]) -> None:
        print(
            f"\n[bold {self.accent_color}]--- CRONOLOGIA MOSSE ---"
            f"[/bold {self.accent_color}]"
        )
        if not moves:
            print("[italic]Nessuna mossa effettuata.[/italic]")
        else:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Turno", justify="right", style="dim")
            table.add_column("Giocatore", justify="center")
            table.add_column("Tipo", justify="center")
            table.add_column("Comando", justify="center")
            for move in moves:
                pnum = int(move["player"][1])
                color = PLAYER_COLORS.get(pnum, "white")
                table.add_row(
                    move["turn"],
                    f"[bold {color}]{move['player']}[/bold {color}]",
                    move["type"],
                    move["command"],
                )
            console.print(table)
        print(
            f"[bold {self.accent_color}]------------------------"
            f"[/bold {self.accent_color}]\n"
        )

    def show_error(self, message: str) -> None:
        print(f"[bold red]{message}[/bold red]")

    def show_winner(self, player: int) -> None:
        color = PLAYER_COLORS.get(player, "white")
        print(
            f"\n[bold {color}]Il Giocatore {player} "
            f"ha vinto la partita![/bold {color}]\n"
        )

    def show_timeout_loss(self, player: int, remaining_players: list[int]) -> None:
        print(
            f"\n[bold red]Il Giocatore {player} ha esaurito il tempo "
            f"ed è stato eliminato![/bold red]"
        )
        if len(remaining_players) > 1:
            names = ", ".join(f"P{p}" for p in remaining_players)
            print(f"[bold]La partita continua in {len(remaining_players)}. "
                  f"Giocatori rimasti: {names}[/bold]\n")

    def show_exit(self, loser: int, remaining_players: list[int]) -> None:
        color = PLAYER_COLORS.get(loser, "white")
        print(
            f"\n[bold {color}]Il Giocatore {loser} ha abbandonato"
            f" la partita.[/bold {color}]"
        )
        if len(remaining_players) == 1:
            winner = remaining_players[0]
            wcolor = PLAYER_COLORS.get(winner, "white")
            print(
                f"[bold {wcolor}]Il Giocatore {winner} vince"
                f" la partita![/bold {wcolor}]\n"
            )
        else:
            names = ", ".join(f"P{p}" for p in remaining_players)
            print(
                f"[bold]La partita continua in {len(remaining_players)}. "
                f"Giocatori rimasti: {names}[/bold]\n"
            )

    def show_quit_message(self) -> None:
        print("\nUscita dal gioco in corso... Arrivederci!\n")

    def show_invalid_menu_choice(self) -> None:
        print("[bold red]Comando non valido.[/bold red]")

    def show_help(self, num_players: int = 2) -> None:
        print("\n[bold cyan]--- GUIDA AI COMANDI ---[/bold cyan]")
        print(
            "[bold]Muovere il pedone:[/bold] Inserisci le coordinate "
            "della casella (es. [green]e2[/green])."
        )
        print(
            "[bold]Muro orizzontale:[/bold] Inserisci 'h' + casella "
            "di riferimento (es. [green]he3[/green])."
        )
        print(
            "[bold]Muro verticale:[/bold] Inserisci 'v' + casella "
            "di riferimento (es. [green]vc2[/green])."
        )
        print(
            "[bold]Cronologia mosse:[/bold] Digita [green]history[/green] "
            "per visualizzare la lista ordinata di tutte le mosse effettuate."
        )
        print(
            "[bold]Modalità a tempo:[/bold] All'avvio puoi attivare "
            "l'orologio stile scacchi. Ogni giocatore ha il proprio "
            "timer indipendente."
        )
        print("\n[bold cyan]--- MODALITÀ DI GIOCO ---[/bold cyan]")
        print(
            "[bold]2 giocatori:[/bold] Classico 1v1. "
            "P1 parte dal lato Nord (riga 1), P2 dal lato Sud (riga 9). "
            "Ogni giocatore dispone di [bold]10 muri[/bold]. "
            "Vince chi raggiunge il lato opposto."
        )
        print(
            "[bold]4 giocatori:[/bold] "
            "P1 (Nord), P2 (Sud), P3 (Ovest), P4 (Est). "
            "Ogni giocatore dispone di [bold]5 muri[/bold]. "
            "Se un giocatore abbandona o esaurisce il tempo, "
            "viene eliminato e la partita prosegue tra i rimanenti. "
            "Vince il primo che raggiunge il lato opposto a quello di partenza."
        )
        print(
            "[bold]Replay:[/bold] Al termine della partita puoi rivedere "
            "la partita mossa per mossa. "
            "[green]next[/green] (o Invio) per avanzare, "
            "[green]prev[/green] per tornare indietro, "
            "[green]quit[/green] per uscire dal replay."
        )
        print(
            "[bold]Altri comandi:[/bold] [green]help[/green], "
            "[green]history[/green], [green]exit[/green], [green]quit[/green]."
        )
        print("[bold cyan]------------------------[/bold cyan]\n")

    def prompt_replay(self) -> bool:
        answer = input("Vuoi rivedere la partita? [s/n]: ").strip().lower()
        return answer == "s"

    def show_replay_header(
        self, current: int, total: int, move_info: dict[str, str] | None
    ) -> None:
        print(
            f"\n[bold {self.accent_color}]--- REPLAY: "
            f"Mossa {current} / {total} ---"
            f"[/bold {self.accent_color}]"
        )
        if move_info is None:
            print("[italic]Posizione iniziale.[/italic]\n")
        else:
            pnum = int(move_info["player"][1])
            color = PLAYER_COLORS.get(pnum, "white")
            print(
                f"[bold {color}]{move_info['player']}[/bold {color}] — "
                f"{move_info['type']}: [bold]{move_info['command']}[/bold]\n"
            )

    def show_replay_end(self) -> None:
        print(
            f"\n[bold {self.accent_color}]Fine del replay.[/bold {self.accent_color}]\n"
        )

    def show_replay_no_moves(self) -> None:
        print("\n[italic]Nessuna mossa da riprodurre.[/italic]\n")

    def show_replay_game_input_blocked(self) -> None:
        print(
            "[bold red]Non puoi inserire mosse durante il replay. "
            "Usa: next, prev, quit.[/bold red]"
        )

    def prompt_replay_command(self, current: int, total: int) -> str:
        return input(f"[{current}/{total}] Comando (next/prev/quit): ").strip().lower()

    def prompt_command(self, turn: int) -> str:
        return input(f"[P{turn}] Inserisci comando: ").strip().lower()

    def prompt_welcome(self) -> str:
        return input("Benvenuto! Inserisci il tuo nome: ")

    def prompt_num_players(self) -> int:
        while True:
            raw = input("Quanti giocatori? [2/4]: ").strip()
            if raw in ("2", "4"):
                return int(raw)
            print("[bold red]Inserisci 2 o 4.[/bold red]")

    def prompt_post_game(self) -> str:
        return (
            input("Vuoi iniziare una nuova partita (n) o uscire (q)? ")
            .strip()
            .lower()
        )

    def show_welcome(self, name: str) -> None:
        print(
            f"Ciao [bold {self.accent_color}]{name}[/bold {self.accent_color}]! "
            "Iniziamo a giocare!\n"
        )

    def prompt_timed_mode(self) -> bool:
        answer = (
            input("Vuoi giocare con un limite di tempo? [s/n]: ").strip().lower()
        )
        return answer == "s"

    def prompt_time_per_player(self) -> int:
        while True:
            raw = input(
                "Inserisci il tempo per giocatore in minuti (es. 5, 10, 20): "
            ).strip()
            if raw.isdigit() and int(raw) > 0:
                return int(raw) * 60
            print("Inserisci un numero intero positivo.")