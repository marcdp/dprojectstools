import json
import os
from pathlib import Path
from ..commands import command, CommandsManager
import docker



class DockerManager:

    # context
    _context: str
    _client = None

    # ctor
    def __init__(self, context):
        self._context = context
        self._client = self._createFromContext(context)

    # props
    @property
    def client(self):
        return self._client
    

    # commands
    #@command("Info", index = 1)
    #def docker_info(self):
    #    info = self._client.info()
    #    print(info)


    # methods
    #def exec(self, argv):
    #    commandsManager = CommandsManager()
    #    commandsManager.register(self)
    #    return commandsManager.execute(argv)
    
    # utils
    def _createFromContext(self, context_name):
        # Paths to Docker configuration
        docker_config_path = Path.home() / ".docker"
        config_file = docker_config_path / "config.json"
        context_dir = docker_config_path / "contexts" / "meta"

        # Ensure configuration files exist
        if not config_file.exists() or not context_dir.exists():
            raise FileNotFoundError("Docker configuration files are not found.")

        # Load config.json to get the current context details
        with open(config_file, "r") as f:
            config = json.load(f)

        # If the context name matches the default or current, use that
        current_context = config.get("currentContext", "default")
        if context_name == "default" or context_name == current_context:
            return docker.from_env()

        # Search for the specified context by name in the meta directory
        for uuid_dir in context_dir.iterdir():
            meta_file = uuid_dir / "meta.json"
            if meta_file.exists():
                with open(meta_file, "r") as f:
                    meta = json.load(f)
                    if meta.get("Name") == context_name:
                        # Extract the Docker endpoint from the meta file
                        docker_endpoint = meta.get("Endpoints", {}).get("docker", {})
                        if not docker_endpoint:
                            raise ValueError(f"No Docker endpoint found for context '{context_name}'.")

                        host = docker_endpoint.get("Host", "unix:///var/run/docker.sock")
                        skip_tls_verify = docker_endpoint.get("SkipTLSVerify", False)
                        ca_cert_dir = Path(docker_endpoint.get("CACertDir", ""))

                        if ca_cert_dir.absolute() == Path(os.getcwd()):
                            ca_cert_dir = docker_config_path / "contexts" / "tls" / uuid_dir.name / "docker"

                        # Configure TLS if required
                        tls_config = None
                        if not skip_tls_verify and ca_cert_dir.exists():
                            tls_config = docker.tls.TLSConfig(
                                ca_cert=ca_cert_dir / "ca.pem",
                                client_cert=(
                                    ca_cert_dir / "cert.pem",  # Client certificate
                                    ca_cert_dir / "key.pem"   # Private key
                                ),
                                verify=True
                            )

                        # Return a configured Docker client
                        return docker.DockerClient(base_url=host, tls=tls_config)

        # Raise an error if the context name is not found
        raise ValueError(f"Docker context '{context_name}' not found.")