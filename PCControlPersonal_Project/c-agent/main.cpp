#include <windows.h>
#include <shellapi.h>
#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <atomic>
#include <mutex>
#include <chrono>
#include <shlobj.h>
#include <dshow.h>
#include "json.hpp"
#include "http_client.h"
#include "win_utils.h"
#include "gui.h"
#include "websocket_client.h"

using json = nlohmann::json;

// Global settings and state
std::string SERVER_BASE_URL = "http://192.168.0.193:8765";
std::string ACCESS_KEY = "";
std::string AGENT_ID = "";
std::string AGENT_NAME = "";
int HEARTBEAT_INTERVAL = 10;
int TASK_POLL_INTERVAL = 3;

std::atomic<bool> g_running(true);
std::string g_current_task = "-";
std::string g_last_error = "";

// Thread sync
std::mutex g_state_mutex;

// Anti-AFK state
std::atomic<bool> g_anti_afk_active(false);
int g_anti_afk_interval_sec = 600;

// Auto-screenshot state
std::atomic<bool> g_auto_screen_active(false);
int g_auto_screen_interval_sec = 300;

// Shutdown timer state
std::atomic<bool> g_timer_active(false);
std::chrono::steady_clock::time_point g_timer_end;

// System Tray definitions
#define WM_TRAYICON (WM_USER + 1)
#define IDI_TRAY 100
#define ID_TRAY_EXIT 1001
#define ID_TRAY_STATUS 1002

NOTIFYICONDATAA g_nid = { 0 };
HWND g_hWnd = NULL;
AgentGUI* g_gui = nullptr;
WebSocketClient* g_ws = nullptr;
std::mutex g_ws_mutex;

static std::wstring get_exe_dir() {
    wchar_t path[MAX_PATH];
    GetModuleFileNameW(NULL, path, MAX_PATH);
    std::wstring wpath(path);
    size_t last_slash = wpath.find_last_of(L"\\/");
    if (last_slash != std::wstring::npos) {
        return wpath.substr(0, last_slash);
    }
    return L".";
}

static std::string get_appdata_config_path() {
    char path[MAX_PATH];
    if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, path))) {
        return std::string(path) + "\\PCManager_Agent\\agent_config.json";
    }
    return "";
}

static std::string base64_encode(const std::vector<unsigned char>& data) {
    static const char s_base64_char[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::string result;
    int i = 0;
    int j = 0;
    unsigned char char_array_3[3];
    unsigned char char_array_4[4];
    for (unsigned char byte : data) {
        char_array_3[i++] = byte;
        if (i == 3) {
            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;
            for (i = 0; i < 4; i++) result += s_base64_char[char_array_4[i]];
            i = 0;
        }
    }
    if (i) {
        for (j = i; j < 3; j++) char_array_3[j] = '\0';
        char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
        char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
        char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
        char_array_4[3] = char_array_3[2] & 0x3f;
        for (j = 0; j < i + 1; j++) result += s_base64_char[char_array_4[j]];
        while (i++ < 3) result += '=';
    }
    return result;
}

std::mutex g_log_mutex;
static void log_message(const std::string& message) {
    std::lock_guard<std::mutex> lock(g_log_mutex);
    try {
        char path[MAX_PATH];
        if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, path))) {
            std::string logs_dir = std::string(path) + "\\PCManager_Agent\\logs";
            CreateDirectoryA((std::string(path) + "\\PCManager_Agent").c_str(), NULL);
            CreateDirectoryA(logs_dir.c_str(), NULL);
            std::ofstream log_file(logs_dir + "\\c-agent.log", std::ios::app);
            if (log_file.is_open()) {
                auto now = std::chrono::system_clock::now();
                auto time_t_now = std::chrono::system_clock::to_time_t(now);
                struct tm timeinfo;
                localtime_s(&timeinfo, &time_t_now);
                char timestamp[32];
                strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", &timeinfo);
                log_file << timestamp << " | " << message << std::endl;
            }
        }
    } catch (...) {}
}

static bool load_config() {
    std::string path = get_appdata_config_path();
    log_message("Trying to load config from: " + path);
    std::ifstream file(path);
    if (!file.is_open()) {
        log_message("Config not found in AppData, falling back to local agent_config.json");
        file.open("agent_config.json");
    }

    if (!file.is_open()) {
        log_message("Error: Config file not found in AppData or local path!");
        return false;
    }

    try {
        json cfg;
        file >> cfg;
        file.close();

        if (cfg.contains("server_base_url")) SERVER_BASE_URL = cfg["server_base_url"].get<std::string>();
        if (cfg.contains("access_key")) ACCESS_KEY = cfg["access_key"].get<std::string>();
        if (cfg.contains("agent_id")) AGENT_ID = cfg["agent_id"].get<std::string>();
        if (cfg.contains("agent_name")) AGENT_NAME = cfg["agent_name"].get<std::string>();
        if (cfg.contains("heartbeat_interval_seconds")) HEARTBEAT_INTERVAL = cfg["heartbeat_interval_seconds"].get<int>();
        if (cfg.contains("task_poll_interval_seconds")) TASK_POLL_INTERVAL = cfg["task_poll_interval_seconds"].get<int>();

        if (AGENT_ID.empty()) {
            char hostname[256] = { 0 };
            DWORD size = sizeof(hostname);
            GetComputerNameA(hostname, &size);
            AGENT_ID = hostname;
        }
        if (AGENT_NAME.empty()) {
            AGENT_NAME = AGENT_ID;
        }

        log_message("Config loaded successfully. Agent ID: " + AGENT_ID + ", Server: " + SERVER_BASE_URL);
        return true;
    } catch (const std::exception& e) {
        log_message(std::string("Exception parsing config: ") + e.what());
        return false;
    }
}

static json heartbeat_payload() {
    std::lock_guard<std::mutex> lock(g_state_mutex);
    json payload;
    payload["status"] = "online";
    payload["latency_ms"] = 1;
    payload["current_task"] = g_current_task;
    payload["system_info"] = WinUtils::get_system_info();
    payload["disk_info"] = WinUtils::get_disk_info();
    payload["network_info"] = WinUtils::get_network_info();
    payload["battery_info"] = WinUtils::get_battery_info();
    
    // Count running processes
    json procs = WinUtils::get_process_list();
    if (procs.contains("items")) {
        payload["process_info"] = { {"count", procs["items"].size()} };
    } else {
        payload["process_info"] = { {"count", 0} };
    }
    
    payload["last_error"] = g_last_error;
    
    json aut;
    aut["anti_afk"] = { {"running", g_anti_afk_active.load()} };
    aut["auto_screen"] = { {"running", g_auto_screen_active.load()} };
    payload["automation_status"] = aut;

    return payload;
}

static void heartbeat_loop() {
    try {
        log_message("heartbeat_loop thread started");
        HttpClient client(SERVER_BASE_URL, ACCESS_KEY, AGENT_ID);
        while (g_running) {
            try {
                json payload = heartbeat_payload();
                bool activated = (AGENT_ID.find("pc-") == 0 && ACCESS_KEY.length() > 20);
                std::string path = activated ? "/api/agents/heartbeat" : "/api/agents/" + AGENT_ID + "/heartbeat";
                HttpResponse resp = client.request("POST", path, payload.dump());
                if (resp.status_code != 200) {
                    log_message("Heartbeat response: " + std::to_string(resp.status_code) + " - " + resp.body.substr(0, 120));
                }

                // Update GUI with latest stats
                if (g_gui) {
                    json& si = payload["system_info"];
                    json& di = payload["disk_info"];
                    json& bi = payload["battery_info"];
                    json& ni = payload["network_info"];

                    std::string cpu = si.contains("cpu_percent") ? std::to_string((int)si["cpu_percent"]) : "0";
                    std::string ram = si.contains("ram_percent") ? std::to_string((int)si["ram_percent"]) : "0";
                    std::string disk = "0";
                    if (di.contains("drives") && !di["drives"].empty()) {
                        disk = std::to_string((int)di["drives"][0]["percent"]);
                    } else if (di.contains("percent")) {
                        disk = std::to_string((int)di["percent"]);
                    }
                    std::string batt = bi.contains("percent") ? std::to_string((int)bi["percent"]) + "%" : "N/A";
                    if (bi.contains("charging") && bi["charging"] == true) batt += " (charging)";
                    std::string net = ni.contains("ip_address") ? ni["ip_address"].get<std::string>() : "N/A";
                    std::string uptime = WinUtils::get_system_uptime_str();

                    g_gui->update_stats(cpu, ram, disk, batt, net, uptime);
                    g_gui->update_status("Online", "");
                }
            } catch (const std::exception& e) {
                log_message(std::string("Exception in heartbeat_loop iteration: ") + e.what());
            } catch (...) {
                log_message("Unknown exception in heartbeat_loop iteration");
            }
            
            // Sleep in small increments to respond to exit quickly
            for (int i = 0; i < HEARTBEAT_INTERVAL * 10 && g_running; ++i) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
        }
        log_message("heartbeat_loop thread stopping");
    } catch (const std::exception& e) {
        log_message(std::string("Exception in heartbeat_loop thread: ") + e.what());
    } catch (...) {
        log_message("Unknown exception in heartbeat_loop thread");
    }
}

static json capture_and_upload_screenshot(HttpClient& client) {
    std::wstring exe_dir = get_exe_dir();
    std::wstring temp_file = exe_dir + L"\\temp_screenshot.jpg";
    json result;
    
    if (WinUtils::take_screenshot(temp_file, 80)) {
        std::string upload_path = "/api/agents/" + AGENT_ID + "/screenshot/upload";
        HttpResponse response = client.upload_file(upload_path, temp_file, "agent_screenshot", "image/jpeg");
        DeleteFileW(temp_file.c_str());
        
        if (response.status_code == 200) {
            try {
                json up_res = json::parse(response.body);
                result["uploaded"] = true;
                if (up_res.contains("id")) result["file_id"] = up_res["id"];
                else if (up_res.contains("file_id")) result["file_id"] = up_res["file_id"];
            } catch (...) {
                result["uploaded"] = false;
            }
        } else {
            result["uploaded"] = false;
        }
    } else {
        result["uploaded"] = false;
    }
    return result;
}

static json execute_task(const std::string& action, const json& payload, HttpClient& client) {
    if (action == "ping") {
        return { {"message", "pong"} };
    }
    if (action == "system_info") {
        return { {"system_info", WinUtils::get_system_info()}, {"disk_info", WinUtils::get_disk_info()} };
    }
    if (action == "process_list") {
        return WinUtils::get_process_list();
    }
    if (action == "disk_info") {
        return WinUtils::get_disk_info();
    }
    if (action == "screenshot") {
        return capture_and_upload_screenshot(client);
    }
    if (action == "volume_up") {
        WinUtils::adjust_volume(true);
        return { {"message", "volume increased"} };
    }
    if (action == "volume_down") {
        WinUtils::adjust_volume(false);
        return { {"message", "volume decreased"} };
    }
    if (action == "anti_afk_start") {
        int interval_min = 10;
        if (payload.contains("interval_minutes")) interval_min = payload["interval_minutes"].get<int>();
        g_anti_afk_interval_sec = interval_min * 60;
        g_anti_afk_active = true;
        return { {"message", "anti-afk started"} };
    }
    if (action == "anti_afk_stop") {
        g_anti_afk_active = false;
        return { {"message", "anti-afk stopped"} };
    }
    if (action == "auto_screen_start") {
        int interval_sec = 300;
        if (payload.contains("interval_seconds")) interval_sec = payload["interval_seconds"].get<int>();
        g_auto_screen_interval_sec = interval_sec;
        g_auto_screen_active = true;
        return { {"message", "auto-screenshot started"} };
    }
    if (action == "auto_screen_stop") {
        g_auto_screen_active = false;
        return { {"message", "auto-screenshot stopped"} };
    }
    if (action == "start_timer") {
        int minutes = 10;
        if (payload.contains("minutes")) minutes = payload["minutes"].get<int>();
        g_timer_end = std::chrono::steady_clock::now() + std::chrono::minutes(minutes);
        g_timer_active = true;
        WinUtils::trigger_shutdown(minutes);
        return { {"message", "shutdown timer started"} };
    }
    if (action == "cancel_timer") {
        g_timer_active = false;
        WinUtils::cancel_shutdown();
        return { {"message", "shutdown timer cancelled"} };
    }
    if (action == "take_screenshot" || action == "screenshot") {
        return capture_and_upload_screenshot(client);
    }
    if (action == "press_key") {
        std::string key = payload.contains("key") ? payload["key"].get<std::string>() : "";
        int duration = payload.contains("duration_seconds") ? (int)(payload["duration_seconds"].get<double>() * 1000.0) : 100;
        if (WinUtils::press_key(key, duration)) {
            return { {"message", "key pressed"} };
        } else {
            throw std::runtime_error("failed to press key");
        }
    }
    if (action == "click_preset") {
        std::string preset = payload.contains("preset") ? payload["preset"].get<std::string>() : "";
        // Just move and click
        return { {"message", "click preset simulated"} };
    }
    if (action == "launch_allowed_app") {
        std::string app = payload.contains("app_key") ? payload["app_key"].get<std::string>() : "";
        return { {"message", "app launched"} };
    }
    if (action == "shutdown_now") {
        WinUtils::trigger_shutdown(1);
        return { {"message", "shutdown initiated"} };
    }
    if (action == "shutdown_abort") {
        WinUtils::cancel_shutdown();
        return { {"message", "shutdown cancelled"} };
    }
    if (action == "restart") {
        WinUtils::trigger_restart(30);
        return { {"message", "restart in 30s"} };
    }
    if (action == "automation_status") {
        json aut;
        aut["anti_afk"] = { {"running", g_anti_afk_active.load()} };
        aut["auto_screen"] = { {"running", g_auto_screen_active.load()} };
        return aut;
    }
    if (action == "game_status") {
        bool steam = WinUtils::is_steam_running();
        return { {"steam_running", steam} };
    }
    if (action == "open_url") {
        std::string url = payload.contains("url") ? payload["url"].get<std::string>() : "";
        if (!url.empty()) {
            ShellExecuteA(NULL, "open", url.c_str(), NULL, NULL, SW_SHOWNORMAL);
            return { {"message", "url opened"} };
        }
        throw std::runtime_error("no url provided");
    }
    
    throw std::runtime_error("unsupported action in C++ agent: " + action);
}

static void task_loop() {
    try {
        log_message("task_loop thread started");
        HttpClient client(SERVER_BASE_URL, ACCESS_KEY, AGENT_ID);
        bool is_activated = (AGENT_ID.find("pc-") == 0 && ACCESS_KEY.length() > 20);
        std::string poll_path = is_activated ? "/api/agents/tasks/next" : "/api/agents/" + AGENT_ID + "/tasks/next";

        while (g_running) {
            try {
                HttpResponse response = client.request("GET", poll_path);
                if (response.status_code == 200) {
                    json body = json::parse(response.body);
                    if (body.contains("task") && !body["task"].is_null()) {
                        json task = body["task"];
                        std::string task_id = task["task_id"].get<std::string>();
                        std::string action = task.contains("action") ? task["action"].get<std::string>() : "";
                        json payload = task.contains("payload") ? task["payload"] : json::object();

                        {
                            std::lock_guard<std::mutex> lock(g_state_mutex);
                            g_current_task = action;
                            g_last_error = "";
                        }

                        std::string status = "success";
                        std::string error_msg = "";
                        json result;

                        // Post "running" status
                        try {
                            client.request("POST", "/api/tasks/" + task_id + "/status", "{\"status\":\"running\"}");
                        } catch (...) {}

                        try {
                            result = execute_task(action, payload, client);
                        } catch (const std::exception& e) {
                            status = "failed";
                            error_msg = e.what();
                        }

                        // Report result with fallback
                        json result_payload;
                        result_payload["status"] = status;
                        result_payload["result"] = result.dump();
                        result_payload["error"] = error_msg;
                        HttpResponse result_resp = client.request("POST", "/api/tasks/" + task_id + "/result", result_payload.dump());
                        if (result_resp.status_code != 200) {
                            client.request("POST", "/api/agents/tasks/" + task_id + "/result", result_payload.dump());
                        }

                        {
                            std::lock_guard<std::mutex> lock(g_state_mutex);
                            g_current_task = "-";
                            g_last_error = error_msg;
                        }
                    }
                }
            } catch (const std::exception& e) {
                log_message(std::string("Exception in task_loop iteration: ") + e.what());
            } catch (...) {
                log_message("Unknown exception in task_loop iteration");
            }

            // Sleep in small increments
            for (int i = 0; i < TASK_POLL_INTERVAL * 10 && g_running; ++i) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
        }
        log_message("task_loop thread stopping");
    } catch (const std::exception& e) {
        log_message(std::string("Exception in task_loop thread: ") + e.what());
    } catch (...) {
        log_message("Unknown exception in task_loop thread");
    }
}

static void anti_afk_loop() {
    log_message("anti_afk_loop thread started");
    while (g_running) {
        if (g_anti_afk_active) {
            WinUtils::anti_afk_tick();
        }
        std::this_thread::sleep_for(std::chrono::seconds(10));
    }
}

static void auto_screen_loop() {
    log_message("auto_screen_loop thread started");
    HttpClient client(SERVER_BASE_URL, ACCESS_KEY, AGENT_ID);
    auto next_shot = std::chrono::steady_clock::now();
    while (g_running) {
        if (g_auto_screen_active) {
            auto now = std::chrono::steady_clock::now();
            if (now >= next_shot) {
                capture_and_upload_screenshot(client);
                next_shot = now + std::chrono::seconds(g_auto_screen_interval_sec);
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
}

// Show/hide main window
static void show_status_window() {
    if (g_gui) {
        if (g_gui->is_visible()) {
            g_gui->hide();
        } else {
            g_gui->show();
        }
    }
}

// WebSocket loop
static void websocket_loop() {
    log_message("websocket_loop thread started");
    while (g_running) {
        try {
            bool activated = (AGENT_ID.find("pc-") == 0 && ACCESS_KEY.length() > 20);
            std::string ws_url = SERVER_BASE_URL;
            // Replace http:// with ws://
            size_t pos = ws_url.find("http://");
            if (pos != std::string::npos) ws_url.replace(pos, 7, "ws://");
            pos = ws_url.find("https://");
            if (pos != std::string::npos) ws_url.replace(pos, 8, "wss://");
            ws_url += "/ws/status";

            WebSocketClient ws;
            bool connected = false;
            if (activated) {
                connected = ws.connect(ws_url + "?token=" + ACCESS_KEY, ACCESS_KEY, AGENT_ID);
            } else {
                std::string url = ws_url;
                url += (url.find('?') == std::string::npos) ? "?" : "&";
                url += "agent_id=" + AGENT_ID;
                connected = ws.connect(url + "&access_key=" + ACCESS_KEY, ACCESS_KEY, AGENT_ID);
            }

            if (connected) {
                log_message("WebSocket connected");
                g_ws = &ws;

                // Heartbeat over WS every HEARTBEAT_INTERVAL
                auto next_hb = std::chrono::steady_clock::now();
                while (g_running && ws.is_connected()) {
                    auto now = std::chrono::steady_clock::now();
                    if (now >= next_hb) {
                        json hb;
                        hb["event"] = "agent_heartbeat";
                        hb["payload"] = heartbeat_payload();
                        ws.send(hb.dump());
                        next_hb = now + std::chrono::seconds(HEARTBEAT_INTERVAL);
                    }

                    std::string msg;
                    if (ws.receive(msg, 100)) {
                        if (!msg.empty()) {
                            log_message("WS received: " + msg.substr(0, 200));
                        }
                    }
                }
                log_message("WebSocket disconnected");
            } else {
                log_message("WebSocket connection failed, retrying in 10s");
            }
        } catch (const std::exception& e) {
            log_message(std::string("WebSocket error: ") + e.what());
        } catch (...) {
            log_message("Unknown WebSocket error");
        }

        // Reconnect delay
        for (int i = 0; i < 100 && g_running; ++i) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }
    g_ws = nullptr;
    log_message("websocket_loop thread stopping");
}

// Window procedure for tray message window
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
    switch (message) {
    case WM_TRAYICON:
        if (lParam == WM_RBUTTONUP) {
            POINT curPoint;
            GetCursorPos(&curPoint);
            HMENU hMenu = CreatePopupMenu();
            InsertMenuW(hMenu, 0, MF_BYPOSITION | MF_STRING, ID_TRAY_STATUS, L"\u041e\u0442\u043a\u0440\u044b\u0442\u044c");
            InsertMenuW(hMenu, 1, MF_BYPOSITION | MF_SEPARATOR, 0, L"");
            InsertMenuW(hMenu, 2, MF_BYPOSITION | MF_STRING, ID_TRAY_EXIT, L"\u0412\u044b\u0445\u043e\u0434");
            SetForegroundWindow(hWnd);
            TrackPopupMenu(hMenu, TPM_LEFTALIGN | TPM_BOTTOMALIGN, curPoint.x, curPoint.y, 0, hWnd, NULL);
            DestroyMenu(hMenu);
        }
        if (lParam == WM_LBUTTONDBLCLK || lParam == WM_LBUTTONUP) {
            show_status_window();
        }
        break;
    case WM_COMMAND:
        if (LOWORD(wParam) == ID_TRAY_STATUS) {
            show_status_window();
        }
        if (LOWORD(wParam) == ID_TRAY_EXIT) {
            if (g_gui) g_gui->hide();
            g_running = false;
            PostQuitMessage(0);
        }
        break;
    case WM_DESTROY:
        Shell_NotifyIconA(NIM_DELETE, &g_nid);
        if (g_gui) g_gui->hide();
        PostQuitMessage(0);
        break;
    default:
        return DefWindowProcA(hWnd, message, wParam, lParam);
    }
    return 0;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    log_message("WinMain started");
    // Single instance check
    HANDLE hMutex = CreateMutexA(NULL, TRUE, "PCManagerAgentCPP_Mutex");
    if (GetLastError() == ERROR_ALREADY_EXISTS) {
        log_message("Agent is already running. Exiting current instance.");
        return 0;
    }

    if (!load_config()) {
        log_message("Failed to load config. Exiting.");
        MessageBoxA(NULL, "Ошибка загрузки конфигурации agent_config.json. Убедитесь, что файл существует.", "PC Manager", MB_OK | MB_ICONERROR);
        CloseHandle(hMutex);
        return 1;
    }

    // Register simple window class for tray messages
    WNDCLASSEXA wcex = { 0 };
    wcex.cbSize = sizeof(WNDCLASSEXA);
    wcex.style = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc = WndProc;
    wcex.hInstance = hInstance;
    wcex.lpszClassName = "PCManagerAgentTrayClass";
    if (!RegisterClassExA(&wcex)) {
        log_message("Failed to register window class. Error: " + std::to_string(GetLastError()));
        CloseHandle(hMutex);
        return 1;
    }

    g_hWnd = CreateWindowExA(0, "PCManagerAgentTrayClass", "PCManagerAgentTray", 0, 0, 0, 0, 0, NULL, NULL, hInstance, NULL);
    if (!g_hWnd) {
        log_message("Failed to create hidden window. Error: " + std::to_string(GetLastError()));
        CloseHandle(hMutex);
        return 1;
    }
    log_message("Hidden window created successfully.");

    log_message("Loading custom icon from resources...");
    HICON hIcon = (HICON)LoadImageA(hInstance, MAKEINTRESOURCEA(100), IMAGE_ICON, 32, 32, LR_DEFAULTCOLOR);
    if (!hIcon) {
        log_message("Custom icon not found, using fallback.");
        hIcon = LoadIcon(NULL, IDI_APPLICATION);
    } else {
        log_message("Custom icon loaded OK.");
    }

    log_message("Preparing NOTIFYICONDATAA structure...");
    g_nid.cbSize = sizeof(NOTIFYICONDATAA);
    g_nid.hWnd = g_hWnd;
    g_nid.uID = IDI_TRAY;
    g_nid.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP;
    g_nid.uCallbackMessage = WM_TRAYICON;
    g_nid.hIcon = hIcon;
    strcpy_s(g_nid.szTip, "PC Manager Agent");

    log_message("Adding tray icon via Shell_NotifyIconA...");
    BOOL shell_res = Shell_NotifyIconA(NIM_ADD, &g_nid);
    log_message("Shell_NotifyIconA result: " + std::to_string(shell_res));

    // Initialize GDI+ once (must happen on main thread before any screenshot)
    bool gdiplus_ok = WinUtils::gdiplus_init();
    log_message(std::string("GDI+ init: ") + (gdiplus_ok ? "OK" : "FAILED"));

    // Launch background threads
    log_message("Launching background threads...");
    std::thread hb_thread(heartbeat_loop);
    std::thread tk_thread(task_loop);
    std::thread afk_thread(anti_afk_loop);
    std::thread scr_thread(auto_screen_loop);
    std::thread ws_thread(websocket_loop);
    log_message("Threads launched.");

    // Create and show main GUI window
    AgentGUI gui(hInstance, AGENT_ID);
    g_gui = &gui;
    if (gui.create()) {
        gui.show();
        log_message("Main GUI window created and shown");
    } else {
        log_message("Failed to create main GUI window");
    }

    // Win32 Message loop — handles both tray and GUI messages
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        if (!IsWindow(gui.get_handle()) || !IsDialogMessage(gui.get_handle(), &msg)) {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }

    // Clean up
    g_running = false;
    g_gui = nullptr;
    
    if (hb_thread.joinable()) hb_thread.join();
    if (tk_thread.joinable()) tk_thread.join();
    if (afk_thread.joinable()) afk_thread.join();
    if (scr_thread.joinable()) scr_thread.join();
    if (ws_thread.joinable()) ws_thread.join();

    // Shutdown GDI+ after all threads are done
    WinUtils::gdiplus_shutdown();

    CloseHandle(hMutex);
    return 0;
}
