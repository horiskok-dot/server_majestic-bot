# PC Control Personal - Project Handoff

## Current Focus

The current work finishes the Windows Agent so it can connect to the Ubuntu FastAPI backend, appear in the Web UI, send PC status, and execute only safe allowlisted tasks.

## Infrastructure

- Ubuntu Server: 24.04 LTS
- Server LAN API: `http://192.168.0.193:8765`
- WebSocket URL for the agent config: `ws://192.168.0.193:8765/ws/status`
- Server project path: `/home/pc/PCControlPersonal_Project`
- Runtime path: `/opt/pcmanager`
- Server config: `/etc/pcmanager/pcmanager.env`
- Backend service: `pcmanager-server.service`

Secrets such as `SERVER_ACCESS_KEY`, Telegram tokens, passwords, and access keys must never be printed or committed. Show them only as `[HIDDEN]`.

## Windows Agent

Important files:

- `pc-agent/agent.py` - Windows Agent runtime.
- `pc-agent/agent_config.example.json` - safe example config.
- `pc-agent/agent_config.json` - local real config, generated from the example and not safe to publish.
- `pc-agent/run_agent.bat` - creates/uses venv, installs requirements, starts the agent.
- `pc-agent/install_agent_windows.bat` - first-time setup helper.
- `pc-agent/requirements.txt` - Python dependencies.
- `pc-agent/logs/agent.log` - rotating local log.

The agent uses:

- `GET /api/ping`
- `POST /api/agents/{agent_id}/heartbeat`
- `POST /api/agents/{agent_id}/status`
- `GET /api/agents/{agent_id}/tasks/next`
- `POST /api/tasks/{task_id}/status`
- `POST /api/tasks/{task_id}/result`
- `POST /api/agents/{agent_id}/screenshot/upload`

The agent sends:

- `agent_id`, `agent_name`, hostname, username, OS/version
- local IP and MAC
- last seen, latency, current task, last error
- CPU/RAM/disk/process count
- battery status if available
- temperature as `null`/unavailable if Windows cannot expose it

Safe tasks:

- `ping`
- `system_info`
- `screenshot`
- `process_list`
- `disk_info`
- `temperature`
- `agent_logs`
- `restart_allowed_app`

The agent does not execute arbitrary shell, PowerShell, cmd, unknown programs, file deletion, hidden camera, or microphone tasks.

## Setup On Windows

```bat
cd pc-agent
install_agent_windows.bat
notepad agent_config.json
run_agent.bat
```

In `agent_config.json`, set:

```json
"access_key": "CHANGE_ME"
```

to the real server access key from `/etc/pcmanager/pcmanager.env`. Do not paste the real value into chat or logs.

## Verify Agent Online

On Windows:

```bat
pc-agent\run_agent.bat
type pc-agent\logs\agent.log
```

On the server:

```bash
curl http://127.0.0.1:8765/api/ping
sudo systemctl status pcmanager-server --no-pager
sudo journalctl -u pcmanager-server -n 80 --no-pager
```

In browser:

```text
http://192.168.0.193:8765/
```

Open the `PC Agent` page and check that the agent is online.

## If Agent Is Offline

Check:

- `pc-agent/agent_config.json`
- `server_base_url`
- `websocket_url`
- `access_key` is configured, but do not print it
- server responds to `/api/ping`
- `pc-agent/logs/agent.log`
- `pcmanager-server.service` is active

## Next Best Actions

1. Deploy the changed backend files to the Ubuntu server.
2. Restart `pcmanager-server`.
3. Copy or update `pc-agent/` on the Windows gaming laptop.
4. Put the real access key into `pc-agent/agent_config.json`.
5. Start `pc-agent/run_agent.bat`.
6. Create a test `ping` task from Web UI or API.
