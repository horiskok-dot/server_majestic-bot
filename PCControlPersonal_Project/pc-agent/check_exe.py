import subprocess
import time
import sys

def main():
    print("Launching dist\\PCManager_Agent.exe...")
    p = subprocess.Popen(
        [r"dist\PCManager_Agent.exe"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for 3 seconds to see if it crashes or stays alive
    time.sleep(3)
    
    ret = p.poll()
    if ret is None:
        print("Agent is still running (no immediate crash detected).")
        print("Terminating process...")
        p.terminate()
    else:
        print(f"Agent terminated with exit code: {ret}")
        stdout, stderr = p.communicate()
        print("Stdout:")
        print(stdout)
        print("Stderr:")
        print(stderr)

if __name__ == "__main__":
    main()
