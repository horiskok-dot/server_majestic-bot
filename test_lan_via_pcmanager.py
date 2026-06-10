import requests
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SERVER_IP = "192.168.0.193"
PORT = 8765

def main():
    url = f"http://{SERVER_IP}:{PORT}/releases/agent.exe"
    print(f"Downloading from {url} to test LAN speed...")
    
    start_time = time.time()
    try:
        r = requests.get(url, timeout=10)
        elapsed = time.time() - start_time
        if r.status_code == 200:
            size_bytes = len(r.content)
            size_mb = size_bytes / (1024 * 1024)
            speed_mbps = (size_mb * 8) / elapsed
            speed_mbytes_sec = size_mb / elapsed
            print("\n--- LAN Speed Test (via PCManager Server) ---")
            print(f"Downloaded: {size_mb:.2f} MB in {elapsed:.6f} seconds")
            print(f"LAN Speed: {speed_mbps:.2f} Mbps ({speed_mbytes_sec:.2f} MB/s)")
        else:
            print(f"Failed to fetch agent.exe: HTTP {r.status_code}")
    except Exception as e:
        print("Error during LAN test:", e)

if __name__ == "__main__":
    main()
