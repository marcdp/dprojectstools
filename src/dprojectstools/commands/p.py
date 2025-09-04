import subprocess
import os


# main
def main():
    if os.path.exists("p.py"):
        subprocess.run("python p.py")
    else:
        print("This is: p.py")
        return -1

if __name__ == "__main__":
    main()

