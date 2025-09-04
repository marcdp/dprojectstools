#!/usr/bin/env python3
from ..commands import command, CommandsManager
from math import sqrt, pow
import sys

# handler
def handler(line, history):
    line = line.strip()
    if line.startswith("*") or line.startswith("+") or line.startswith("-") or line.startswith("/") or line.startswith("^"):
        if len(history) > 0:
            line = history[-1].result + " " + line        
    return eval(line)


# main
def main():
    commandsManager = CommandsManager()
    commandsManager.register()
    commandsManager.execute(argv = sys.argv, repl = handler)
if __name__ == "__main__":
    main()



