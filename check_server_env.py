import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SERVER = "192.168.0.193"
USER = "pc"
PASSWORD = "8008"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SERVER, port=22, username=USER, password=PASSWORD, timeout=15)
        # Read .env file on the remote server
        _, stdout, _ = ssh.exec_command("cat /opt/pcmanager/backend/.env")
        content = stdout.read().decode('utf-8', errors='replace')
        print("=== Remote Server .env Contents ===")
        print(content)
    except Exception as e:
        print("Error reading remote .env:", e)
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
