import paramiko
import sys
import time
import threading
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SERVER_IP = "192.168.0.193"
PORT = 9999
USER = "pc"
PASSWORD = "8008"

# Python code to run on the server
remote_server_code = f"""
import http.server
import socketserver

class DummyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/test':
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Length', '100000000') # 100MB
            self.end_headers()
            data = b'0' * (1024 * 1024) # 1MB
            for _ in range(100):
                try:
                    self.wfile.write(data)
                except Exception:
                    break
        else:
            self.send_error(404)

socketserver.TCPServer.allow_reuse_address = True
try:
    with socketserver.TCPServer(("", {PORT}), DummyHandler) as httpd:
        httpd.handle_request() # handle single request and exit
except Exception as e:
    print("Server error:", e)
"""

def run_remote_server():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SERVER_IP, port=22, username=USER, password=PASSWORD, timeout=15)
        # Execute the python code on the server
        # We write it to a remote temp file first
        sftp = ssh.open_sftp()
        temp_file = "/tmp/lan_speedtest_srv.py"
        with sftp.file(temp_file, "w") as f:
            f.write(remote_server_code)
        sftp.close()
        
        # Start server and wait
        ssh.exec_command(f"python3 {temp_file}")
    except Exception as e:
        print("SSH Server thread error:", e)
    finally:
        ssh.close()

def main():
    print("Starting LAN speed test server on remote machine...")
    srv_thread = threading.Thread(target=run_remote_server, daemon=True)
    srv_thread.start()
    
    # Wait for server to boot up
    time.sleep(2)
    
    print(f"Downloading 100MB from server (http://{SERVER_IP}:{PORT}/test)...")
    url = f"http://{SERVER_IP}:{PORT}/test"
    start_time = time.time()
    try:
        r = requests.get(url, timeout=15, stream=True)
        if r.status_code == 200:
            total_bytes = 0
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                total_bytes += len(chunk)
            elapsed = time.time() - start_time
            size_mb = total_bytes / (1024 * 1024)
            speed_mbps = (size_mb * 8) / elapsed
            speed_mbytes_sec = size_mb / elapsed
            print("\n--- Local LAN Speed Test Results ---")
            print(f"Download speed: {speed_mbps:.2f} Mbps ({speed_mbytes_sec:.2f} MB/s)")
            print(f"Transferred: {size_mb:.2f} MB in {elapsed:.2f} seconds")
        else:
            print(f"Failed: HTTP {r.status_code}")
    except Exception as e:
        print("LAN speed test error:", e)

if __name__ == "__main__":
    main()
