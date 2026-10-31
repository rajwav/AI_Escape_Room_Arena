"""
AI Escape Room & Game Arena — Game UI Modules Registry
"""

from .escape_room import render_escape_room_game
from .sudoku import render_sudoku_game
from .minesweeper import render_minesweeper_game
from .tic_tac_toe import render_tic_tac_toe_game
from .chess import render_chess_game

__all__ = [
    "render_escape_room_game",
    "render_sudoku_game",
    "render_minesweeper_game",
    "render_tic_tac_toe_game",
    "render_chess_game"
]
