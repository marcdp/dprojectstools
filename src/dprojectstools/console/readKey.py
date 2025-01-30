from .keys import Keys
import sys
import os
from dataclasses import dataclass

# asdad
def is_complete_vt_sequence(sequence):
    if not sequence:
        return False

    # A valid VT sequence must start with the escape character
    if not sequence.startswith("\x1b"):
        return False

    # Single ESC key press (just `\x1b`) is a valid sequence
    if sequence == "\x1b":
        return True

    # Check for Control Sequence Introducer (CSI) sequences
    if sequence[1] == "[":
        # CSI sequences end with a final byte in the range `@` to `~`
        if len(sequence) > 2 and sequence[-1] in "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~":
            return True
        return False

    # Check for Function Key sequences (ESC + O + final byte)
    if sequence[1] == "O":
        # Function key sequences end with a single final byte (A-Z or a-z)
        if len(sequence) == 3 and sequence[-1].isalpha():
            return True
        return False

    # Any other sequence (e.g., malformed)
    return False

# Read key
if os.name == 'nt':  
    import msvcrt
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL('user32', use_last_error=True)

    console_encoding = os.device_encoding(0)

    # https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
    ansi_equivalences = {
        b';': Keys.F1,
        b'<': Keys.F2,
        b'=': Keys.F3,
        b'>': Keys.F4,
        b'?': Keys.F5,
        b'@': Keys.F6,
        b'A': Keys.F7,
        b'B': Keys.F8,
        b'C': Keys.F9,
        b'D': Keys.F10,
        b'E': Keys.F11,
        b'\x86': Keys.F12,    

        b'T': Keys.SHIFT_F1,
        b'U': Keys.SHIFT_F2,
        b'V': Keys.SHIFT_F3,
        b'W': Keys.SHIFT_F4,
        b'X': Keys.SHIFT_F5,
        b'Y': Keys.SHIFT_F6,
        b'Z': Keys.SHIFT_F7,
        b'[': Keys.SHIFT_F8,
        b'\\': Keys.SHIFT_F9,
        b']': Keys.SHIFT_F10,
        b'\x87': Keys.SHIFT_F11,
        b'\x88': Keys.SHIFT_F12,

        b'^': Keys.CTRL_F1,
        b'_': Keys.CTRL_F2,
        b'`': Keys.CTRL_F3,
        b'a': Keys.CTRL_F4,
        b'b': Keys.CTRL_F5,
        b'c': Keys.CTRL_F6,
        b'd': Keys.CTRL_F7,
        b'e': Keys.CTRL_F8,
        b'f': Keys.CTRL_F9,
        b'g': Keys.CTRL_F10,
        b'\x89': Keys.CTRL_F11,
        b'\x8a': Keys.CTRL_F12,

        b'H': Keys.UP_ARROW,
        b'P': Keys.DOWN_ARROW,
        b'M': Keys.RIGHT_ARROW,
        b'K': Keys.LEFT_ARROW,
        b'G': Keys.HOME_ARROW,
        b'O': Keys.END_ARROW,

        b't': Keys.CTRL_RIGHT_ARROW,
        b's': Keys.CTRL_LEFT_ARROW,
        b'\x8d': Keys.CTRL_UP_ARROW,
        b'\x91': Keys.CTRL_DOWN_ARROW,
        b'\x92': Keys.CTRL_INSERT,
        b'\x93': Keys.CTRL_DELETE,

        b'\x97': Keys.ALT_HOME_ARROW,
        b'\x9f': Keys.ALT_END_ARROW,

        b'\x9d': Keys.ALT_RIGHT_ARROW,
        b'\x9b': Keys.ALT_LEFT_ARROW,
        b'\x98': Keys.ALT_UP_ARROW,
        b'\xa0': Keys.ALT_DOWN_ARROW,

        b'\x99': Keys.ALT_PAGE_UP,
        b'\xa1': Keys.ALT_PAGE_DOWN,

        b'\xa2': Keys.ALT_INSERT,
        b'\xa3': Keys.ALT_DELETE,

        b'R': Keys.INSERT,
        b'S': Keys.DELETE,
        b'I': Keys.PAGE_UP,
        b'Q': Keys.PAGE_DOWN,
    }
    
    # constants
    VK_RIGHT = 0x27
    VK_SHIFT = 0x10
    VK_CTRL = 0x11
    VK_ALT = 0x12
    KEY_PRESSED = 0x8000

    # utils
    def is_key_pressed(vk_code):
        return bool(user32.GetAsyncKeyState(vk_code) & KEY_PRESSED)
    
    def is_shift_pressed():
        return is_key_pressed(VK_SHIFT)
    def is_ctrl_pressed():
        return is_key_pressed(VK_CTRL)
    def is_alt_pressed():
        return is_key_pressed(VK_ALT)
    
    def filter(key):

        #print(is_ctrl_pressed())
        #print(is_shift_pressed())
        #print(key)

        # ctrl + shift
        if key == Keys.CTRL_RIGHT_ARROW and is_shift_pressed():
            return Keys.CTRL_SHIFT_RIGHT_ARROW
        if key == Keys.CTRL_LEFT_ARROW and is_shift_pressed():
            return Keys.CTRL_SHIFT_LEFT_ARROW
        if key == Keys.CTRL_UP_ARROW and is_shift_pressed():
            return Keys.CTRL_SHIFT_UP_ARROW
        if key == Keys.CTRL_DOWN_ARROW and is_shift_pressed():
            return Keys.CTRL_SHIFT_DOWN_ARROW
        
        #if key == Keys.CTRL_PAGE_UP and is_shift_pressed():
        #    return Keys.CTRL_SHIFT_PAGE_UP
        #if key == Keys.CTRL_PAGE_DOWN and is_shift_pressed():
        #    return Keys.CTRL_SHIFT_PAGE_DOWN
        
        if key == Keys.CTRL_HOME_ARROW and is_shift_pressed():
            return Keys.CTLR_SHIFT_HOME_ARROW
        if key == Keys.CTRL_END_ARROW and is_shift_pressed():
            return Keys.CTLR_SHIFT_END_ARROW
        if key == Keys.CTRL_CENTER_ARROW and is_shift_pressed():
            return Keys.CTLR_SHIFT_CENTER_ARROW
        
        if key == Keys.CTRL_DELETE and is_shift_pressed():
            return Keys.CTRL_SHIFT_DELETE
        if key == Keys.CTRL_INSERT and is_shift_pressed():
            return Keys.CTRL_SHIFT_INSERT

        if key == Keys.CTRL_F1 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F1
        if key == Keys.CTRL_F2 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F2
        if key == Keys.CTRL_F3 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F3
        if key == Keys.CTRL_F4 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F4
        if key == Keys.CTRL_F5 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F5
        if key == Keys.CTRL_F6 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F6
        if key == Keys.CTRL_F7 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F7
        if key == Keys.CTRL_F8 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F8
        if key == Keys.CTRL_F9 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F9
        if key == Keys.CTRL_F10 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F11
        if key == Keys.CTRL_F11 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F11
        if key == Keys.CTRL_F12 and is_shift_pressed():
            return Keys.CTRL_SHIFT_F12

        # shift
        if key == Keys.RIGHT_ARROW and is_shift_pressed():
            return Keys.SHIFT_RIGHT_ARROW
        if key == Keys.LEFT_ARROW and is_shift_pressed():
            return Keys.SHIFT_LEFT_ARROW
        if key == Keys.UP_ARROW and is_shift_pressed():
            return Keys.SHIFT_UP_ARROW
        if key == Keys.DOWN_ARROW and is_shift_pressed():
            return Keys.SHIFT_DOWN_ARROW
        if key == Keys.PAGE_UP and is_shift_pressed():
            return Keys.SHIFT_PAGE_UP
        if key == Keys.PAGE_DOWN and is_shift_pressed():
            return Keys.SHIFT_PAGE_DOWN

        if key == Keys.HOME_ARROW and is_shift_pressed():
            return Keys.SHIFT_HOME_ARROW
        if key == Keys.END_ARROW and is_shift_pressed():
            return Keys.SHIFT_END_ARROW
        if key == Keys.CENTER_ARROW and is_shift_pressed():
            return Keys.SHIFT_CENTER_ARROW

        if key == Keys.DELETE and is_shift_pressed():
            return Keys.SHIFT_DELETE
        if key == Keys.TAB and is_shift_pressed():
            return Keys.SHIFT_TAB
        
        # ctrl
        if key == Keys.PAGE_UP and is_ctrl_pressed():
            return Keys.CTRL_PAGE_UP
        if key == Keys.PAGE_DOWN and is_ctrl_pressed():
            return Keys.CTRL_PAGE_DOWN

        if key == 'w' and is_ctrl_pressed():
            return Keys.CTRL_HOME_ARROW
        if key == 'u' and is_ctrl_pressed():
            return Keys.CTRL_END_ARROW
        if key == 'a' and is_ctrl_pressed():
            return Keys.CTRL_A

        return key
    
    def readKey():
        byte = msvcrt.getch()
        #byte = msvcrt.getwch()
        #print(byte)
        #return byte
        if byte == b'\x08':
            return filter(Keys.BACKSPACE)
        if byte == b'\x00' or byte == b'\xe0':
            byte = msvcrt.getch()
            #print(byte)
            if byte in ansi_equivalences:
                 return filter(ansi_equivalences[byte])
        return filter(byte.decode(console_encoding))
else:
    import termios
    import tty
    def readKey():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)  # Set terminal to raw mode
            key = sys.stdin.read(1)  # Read a single character
            #print(bytes(key[0], encoding='ascii'))
            #print(type(key))
            #print(key)
            if key == '\x08':
                key = Keys.BACKSPACE
            if key == '\x1b':
                sequence = key
                while True:
                    key = sys.stdin.read(1)
                    sequence += key
                    if is_complete_vt_sequence(sequence):
                        return sequence
                #print(sequence)    
                return sequence
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # Restore settings
        return key

#def readKey():
#    sequence = readSequence()
#    char = ' '
#    shift = False
#    ctrl = False
#    alt = False
#    return Key(char, shift, ctrl, alt, sequence)
