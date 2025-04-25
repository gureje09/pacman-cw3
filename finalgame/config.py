# config.py - Game settings and constants

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
GRID_WIDTH = 25
GRID_HEIGHT = 19

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
WALL_COLOR = (33, 33, 255)
DEBUG_PATH_COLOR = (0, 255, 255, 128)

# Game settings
FPS = 10
PACMAN_SPEED = 1
GHOST_SPEED = 0.8
BLINKY_COLOR = RED
PINKY_COLOR = PINK
INKY_COLOR = CYAN
CLYDE_COLOR = ORANGE
GHOST_SCARED_COLOR = PURPLE

# Maze layout
MAZE = [
    "XXXXXXXXXXXXXXXXXXXXXXXXX",
    "XP           X          X",
    "X XXXXX XXXX X XXXXX XX X",
    "X X   X X    X      X XX X",
    "X XXX X XXXXXXXX XXXX XX X",
    "X X   X        X X    X  X",
    "X X XXXXXXX XX X X XX XX X",
    "X X     X XX     X XX XX X",
    "X XXXXX X XXXXXXX XX XX X",
    "X       X         XX    X",
    "XXXXX X XXX XXXXX XX XXXX",
    "X     X X     X      X  X",
    "X XXXXX X XXX XXXXXXXX  X",
    "X X     X X X      X    X",
    "X X XXXXX X XXXXXX X XXXX",
    "X X       X        X    X",
    "X XXXXXXXXX XXXXXXXX XX X",
    "X                      GX",
    "XXXXXXXXXXXXXXXXXXXXXXXXX"
]

# Game states
GAME_RUNNING = 0
GAME_PAUSED = 1
GAME_OVER = 2
GAME_WON = 3
GAME_START = 4

# Direction vectors
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]