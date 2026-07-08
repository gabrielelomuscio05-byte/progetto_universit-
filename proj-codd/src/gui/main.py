import argparse
import os
import sys

from src.board import QuoridorBoard
from src.history import MoveHistory
from src.replay import ReplayHandler
from src.timer import GameTimer
from src.view import QuoridorView
from src.win_handler import WinHandler


def clear_screen() -> None:
    """Clear the terminal screen based on the current OS."""
    os.system("cls" if os.name == "nt" else "clear")


def setup_timer(view: QuoridorView, num_players: int) -> GameTimer | None:
    """Prompt the user for timed mode and return a configured GameTimer or None."""
    timed_mode = view.prompt_timed_mode()
    if timed_mode:
        seconds = view.prompt_time_per_player()
        return GameTimer(seconds, num_players)
    return None


def new_game(
    view: QuoridorView,
) -> tuple[QuoridorBoard, GameTimer | None, MoveHistory]:
    """Initialize a brand new game session, asking for player count and timer."""
    num_players = view.prompt_num_players()
    board = QuoridorBoard(num_players)
    history = MoveHistory()
    timer = setup_timer(view, num_players)
    clear_screen()
    view.display_board(board, timer)
    return board, timer, history


def run_replay(
    view: QuoridorView, history: MoveHistory, num_players: int
) -> None:
    """Step through every move of the finished game, one board state at a time."""
    moves = history.get_all_moves()
    if not moves:
        view.show_replay_no_moves()
        return

    replay = ReplayHandler(moves, num_players)
    total = replay.total_moves()
    index = 0

    clear_screen()
    view.show_replay_header(index, total, replay.get_move_info(index))
    view.display_board(replay.get_snapshot(index))

    while True:
        command = view.prompt_replay_command(index, total)

        if command in ("next", ""):
            if index < total:
                index += 1
                clear_screen()
                view.show_replay_header(index, total, replay.get_move_info(index))
                view.display_board(replay.get_snapshot(index))
            else:
                view.show_replay_end()
                return
        elif command == "prev":
            if index > 0:
                index -= 1
                clear_screen()
                view.show_replay_header(index, total, replay.get_move_info(index))
                view.display_board(replay.get_snapshot(index))
        elif command == "quit":
            return
        else:
            view.show_replay_game_input_blocked()


def handle_post_game(
    view: QuoridorView,
    history: MoveHistory,
    num_players: int,
) -> tuple[QuoridorBoard, GameTimer | None, MoveHistory] | tuple[None, None, None]:
    """Prompt the player after a game ends.

    Returns a new board, timer and history, or (None, None, None) to quit.
    """
    view.show_history(history.get_all_moves())
    if view.prompt_replay():
        run_replay(view, history, num_players)
    while True:
        choice = view.prompt_post_game()
        if choice == "n":
            return new_game(view)
        elif choice == "q":
            return None, None, None
        else:
            view.show_invalid_menu_choice()


def eliminate_player(
    board: QuoridorBoard,
    timer: GameTimer | None,
    player: int,
) -> None:
    """Remove a player from the active game and their timer entry if applicable."""
    board.eliminate_player(player)
    if timer is not None:
        timer.remove_player(player)


def cli_main() -> None:
    """Coordinate Model, View, Timer and History as the main controller.

    Contains no UI rendering.
    """
    view = QuoridorView(accent_color="blue")

    name = view.prompt_welcome()
    view.show_welcome(name)

    board, timer, history = new_game(view)

    if timer is not None:
        timer.start_turn(board.turn)

    while True:
        current_player = board.turn

        if timer is not None and timer.is_expired(current_player):
            remaining = [p for p in board.active_players if p != current_player]
            view.show_timeout_loss(current_player, remaining)
            eliminate_player(board, timer, current_player)

            winner = WinHandler.check_win(board)
            if winner != 0:
                view.display_board(board, timer)
                view.show_winner(winner)
                num_p = board.num_players
                board, timer, history = handle_post_game(view, history, num_p)
                if board is None:
                    return
                if timer is not None:
                    timer.start_turn(board.turn)
                continue

            clear_screen()
            view.display_board(board, timer)
            if timer is not None:
                timer.start_turn(board.turn)
            continue

        command = view.prompt_command(current_player)

        if command == "quit":
            if timer is not None:
                timer.stop_turn()
            view.show_quit_message()
            sys.exit(0)

        if command == "help":
            view.show_help(board.num_players)
            continue

        if command == "history":
            view.show_history(history.get_all_moves())
            continue

        if command == "exit":
            if timer is not None:
                timer.stop_turn()
            remaining = [p for p in board.active_players if p != current_player]
            view.show_exit(current_player, remaining)
            eliminate_player(board, timer, current_player)

            winner = WinHandler.check_win(board)
            if winner != 0:
                view.display_board(board, timer)
                view.show_winner(winner)
                num_p = board.num_players
                board, timer, history = handle_post_game(view, history, num_p)
                if board is None:
                    return
                if timer is not None:
                    timer.start_turn(board.turn)
                continue

            clear_screen()
            view.display_board(board, timer)
            if timer is not None:
                timer.start_turn(board.turn)
            continue

        if timer is not None:
            timer.stop_turn()

        success, error = board.process_move(command)
        if not success:
            view.show_error(error)
            if timer is not None:
                timer.start_turn(board.turn)
            continue

        history.record_move(current_player, command)

        clear_screen()
        winner = WinHandler.check_win(board)
        if winner != 0:
            view.display_board(board, timer)
            view.show_winner(winner)
            num_p = board.num_players
            board, timer, history = handle_post_game(view, history, num_p)
            if board is None:
                return
            if timer is not None:
                timer.start_turn(board.turn)
        else:
            view.display_board(board, timer)
            if timer is not None:
                timer.start_turn(board.turn)


def main() -> None:
    """Entry point: instrada CLI o GUI in base al flag --gui."""
    parser = argparse.ArgumentParser(description="Quoridor")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Avvia la GUI Textual",
    )
    args = parser.parse_args()

    if args.gui:
        # Import lazy: la GUI viene caricata solo se richiesta,
        # così la CLI non dipende da Textual quando non serve.
        from src.gui.app import QuoridorApp
        QuoridorApp().run()
    else:
        cli_main()


if __name__ == "__main__":
    main()
