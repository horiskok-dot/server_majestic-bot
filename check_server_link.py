import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SERVER = "192.168.0.193"
USER = "pc"
PASSWORD = "8008"

def run(client, cmd):
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out.strip(), err.strip()

def main():
    print(f"Connecting to server {SERVER}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SERVER, port=22, username=USER, password=PASSWORD, timeout=15)
        print("[OK] Connected.")
        
        # 1. Get interfaces
        out_ip, _ = run(ssh, "ip -o link show | awk -F': ' '{print $2}'")
        interfaces = [iface.strip() for iface in out_ip.split('\n') if iface.strip() and iface.strip() != 'lo']
        print(f"Server network interfaces: {interfaces}")
        
        # 2. Check speed for each interface
        for iface in interfaces:
            # Try sysfs speed file
            speed_val, _ = run(ssh, f"cat /sys/class/net/{iface}/speed 2>/dev/null")
            operstate, _ = run(ssh, f"cat /sys/class/net/{iface}/operstate 2>/dev/null")
            print(f"Interface {iface}: State = {operstate}, Speed = {speed_val} Mbps")
            
            # Try ethtool if ethtool is available
            ethtool_out, _ = run(ssh, f"echo '8008' | sudo -S ethtool {iface} 2>/dev/null")
            if ethtool_out:
                print(f"Ethtool details for {iface}:")
                for line in ethtool_out.split('\n'):
                    if "Speed:" in line or "Duplex:" in line or "Link detected:" in line:
                        print(f"  {line.strip()}")
                        
    except Exception as e:
        print("Error checking server link speed:", e)
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
