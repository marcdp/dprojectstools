
from dataclasses import dataclass

@dataclass(frozen=True)
class Sequences:
    RESET = "\033[0m"          # Reset all styles
    BOLD = "\033[1m"           # Bold text
    DIM = "\033[2m"            # Dim text
    ITALIC = "\033[3m"         # Italic text
    UNDERLINE = "\033[4m"      # Underline text
    BLINK = "\033[5m"          # Blinking text
    REVERSE = "\033[7m"        # Reverse text (swap foreground and background)
    HIDDEN = "\033[8m"         # Hidden text

    # Foreground Colors
    FG_BLACK = "\033[30m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_BLUE = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN = "\033[36m"
    FG_WHITE = "\033[37m"
    FG_DEFAULT = "\033[39m"

    # Bright Foreground Colors
    FG_BRIGHT_BLACK = "\033[90m"
    FG_BRIGHT_RED = "\033[91m"
    FG_BRIGHT_GREEN = "\033[92m"
    FG_BRIGHT_YELLOW = "\033[93m"
    FG_BRIGHT_BLUE = "\033[94m"
    FG_BRIGHT_MAGENTA = "\033[95m"
    FG_BRIGHT_CYAN = "\033[96m"
    FG_BRIGHT_WHITE = "\033[97m"

    # Background Colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_DEFAULT = "\033[49m"

    # Bright Background Colors
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"

    # Commands
    CLEAR_SCREEN = "\033[2J\033[H"
    SET_CURSOR_POSITION_X_Y = "\033[{1};{0}H"

    CURSOR_BLINKING_ENABLE = "\033[?12h"
    CURSOR_BLINKING_DISABLE = "\033[?12l"
    CURSOR_HIDE = "\033[?25l"
    CURSOR_SHOW = "\033[?25h"

    CURSOR_SHAPE_DEFAULT = "\033[0 q"
    CURSOR_SHAPE_BLINKING_BLOCK = "\033[1 q"
    CURSOR_SHAPE_STEADY_BLOCK = "\033[2 q"
    CURSOR_SHAPE_BLINKING_UNDERLINE = "\033[3 q"
    CURSOR_SHAPE_STEADY_UNDERLINE = "\033[4 q"
    CURSOR_SHAPE_BLINKING_BAR = "\033[5 q"
    CURSOR_SHAPE_STEADY_BAR = "\033[6 q"

    BUFFER_MAIN = "\033[?1049l"
    BUFFER_ALTERNATE = "\033[?1049h"
    