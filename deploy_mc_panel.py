import paramiko
import os

HOSTNAME = "192.168.0.193"
USERNAME = "pc"
PASSWORD = "8008"

LOCAL_DIR = r"c:\Users\horis\Downloads\PCManagerBot_Setup_v2\PCControlPersonal_Project\backend\app"

FILES_TO_UPLOAD = [
    ("main.py", "/opt/pcmanager/backend/app/main.py"),
    ("models.py", "/opt/pcmanager/backend/app/models.py"),
    ("schemas.py", "/opt/pcmanager/backend/app/schemas.py"),
    ("database.py", "/opt/pcmanager/backend/app/database.py"),
    ("api/minecraft_routes.py", "/opt/pcmanager/backend/app/api/minecraft_routes.py"),
    ("api/home_routes.py", "/opt/pcmanager/backend/app/api/home_routes.py"),
    ("api/agent_routes.py", "/opt/pcmanager/backend/app/api/agent_routes.py"),
    ("services/agent_service.py", "/opt/pcmanager/backend/app/services/agent_service.py"),
    ("services/minecraft_monitor.py", "/opt/pcmanager/backend/app/services/minecraft_monitor.py"),
    ("web/panel.html", "/opt/pcmanager/backend/app/web/panel.html"),
    ("bot/telegram_bot.py", "/opt/pcmanager/backend/app/bot/telegram_bot.py")
]

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, timeout=10)
    
    sftp = client.open_sftp()
    
    for local_rel, remote_abs in FILES_TO_UPLOAD:
        local_abs = os.path.join(LOCAL_DIR, os.path.normpath(local_rel))
        basename = local_rel.split("/")[-1]
        tmp_path = f"/tmp/{basename}"
        print(f"Uploading {local_abs} to {tmp_path}...")
        sftp.put(local_abs, tmp_path)
        stdin, stdout, stderr = client.exec_command(f"echo '8008' | sudo -S mv {tmp_path} {remote_abs}")
        print(stderr.read().decode('utf-8'))
        
    sftp.close()
    
    print("Restarting pcmanager-server...")
    stdin, stdout, stderr = client.exec_command("echo '8008' | sudo -S systemctl restart pcmanager-server")
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))
    
    print("Restarting pcmanager-bot...")
    stdin, stdout, stderr = client.exec_command("echo '8008' | sudo -S systemctl restart pcmanager-bot")
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))
    
    client.close()
    print("Done!")

if __name__ == "__main__":
    run()
