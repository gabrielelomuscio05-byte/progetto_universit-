"""Package GUI per Quoridor — interfaccia grafica basata su Textual.

Tutti i moduli di questo package fanno da livello presentazione sopra
il dominio definito in `src/board.py`, `src/movement.py`, `src/wall.py`,
`src/win_handler.py`, `src/timer.py`, `src/history.py`, `src/replay.py`.

La logica di gioco NON viene riscritta: la GUI orchestra le classi
del dominio esattamente come fa il controller CLI in `src/main.py`.
"""
