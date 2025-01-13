import os
import subprocess
from typing import Annotated
from ..commands import command, CommandsManager

class Restic:

    # vars
    _repository: str
    _repository_password: str
    _aws_access_key_id: str
    _aws_secret_access_key: str
    
    # ctor
    def __init__(self, repository, repository_password, aws_access_key_id, aws_secret_access_key):
        self._repository = repository
        self._repository_password = repository_password
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key

    # commands
    @command("Init repository", index = 1)
    def init(self):
        return subprocess.run("restic init", env = self._getEnv())

    @command("Backup ", index = 10)
    def backup(self):
        return subprocess.run("restic backup ./data ./data2 --verbose", env = self._getEnv())

    @command("List snapshots ", index = 20)
    def snapshots_list(self):
        return subprocess.run("restic snapshots", env = self._getEnv())
    
    @command("List snapshot contents ")
    def snapshots_contents(self, 
            id: Annotated[str, "ID"]
        ):
        return subprocess.run("restic ls --long {0}".format(id), env = self._getEnv())

    @command("Restore ")
    def snapshots_restore(self, 
            id: Annotated[str, "ID"]
        ):
        return subprocess.run("restic restore {0} --target ./restore --verbose".format(id), env = self._getEnv())

    # methods
    def exec(self, argv):
        commandsManager = CommandsManager()
        commandsManager.register(self)
        return commandsManager.execute(argv)
    
    # utils
    def _getEnv(self):
        myenv = os.environ.copy()
        myenv['RESTIC_REPOSITORY'] = self._repository
        myenv['RESTIC_PASSWORD'] = self._repository_password
        myenv["AWS_ACCESS_KEY_ID"] = self._aws_access_key_id
        myenv['AWS_SECRET_ACCESS_KEY'] = self._aws_secret_access_key
        return myenv
    


