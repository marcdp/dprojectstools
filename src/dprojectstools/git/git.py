import subprocess
from ..commands import command, CommandsManager

class GitManager:

    # commands
    @command("Git status", index = 90)
    def git_status(self):
        return subprocess.run("git status --short")

    @command("Git add")
    def git_add(self):
        return subprocess.run("git add . --all")

    @command("Git commit")
    def git_commit(self):
        message = input("Enter changes: ")
        return subprocess.run(f"git commit -a -m \"{message}\"")

    @command("Git push")
    def git_push(self):
        return subprocess.run("git push")
    
    # methods
    def exec(self, argv):
        commandsManager = CommandsManager()
        commandsManager.register(self)
        return commandsManager.execute(argv)   