import sys

def read_password(prompt: str = "Enter password: ", mask: str = "*") -> str:
    print(prompt, end="", flush=True)
    chars = []

    if sys.platform == "win32":
        import msvcrt

        while True:
            ch = msvcrt.getwch()

            if ch in ("\r", "\n"):
                print()
                return "".join(chars)

            if ch == "\003":
                raise KeyboardInterrupt

            if ch == "\b":
                if chars:
                    chars.pop()
                    print("\b \b", end="", flush=True)
                continue

            if ch in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue

            chars.append(ch)
            print(mask, end="", flush=True)

    else:
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)

                if ch in ("\r", "\n"):
                    print()
                    return "".join(chars)

                if ch == "\x03":
                    raise KeyboardInterrupt

                if ch in ("\x7f", "\b"):
                    if chars:
                        chars.pop()
                        print("\b \b", end="", flush=True)
                    continue

                chars.append(ch)
                print(mask, end="", flush=True)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)