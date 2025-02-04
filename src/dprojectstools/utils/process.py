import subprocess

def run_stdout(command: str) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout.strip()
     