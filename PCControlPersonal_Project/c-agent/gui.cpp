#include "gui.h"
#include <uxtheme.h>
#include <windowsx.h>
#include <commctrl.h>
#include <string>
#include <fstream>
#include <shlobj.h>
#include <thread>
#include <algorithm>
#include "json.hpp"
#include "http_client.h"
#include "win_utils.h"
#include "websocket_client.h"

#pragma comment(lib, "uxtheme.lib")
#pragma comment(lib, "msimg32.lib")

using json = nlohmann::json;

// Extern globals from main.cpp
extern std::string SERVER_BASE_URL;
extern std::string ACCESS_KEY;
extern std::string AGENT_ID;
extern std::string AGENT_NAME;
extern int HEARTBEAT_INTERVAL;
extern int TASK_POLL_INTERVAL;
extern WebSocketClient* g_ws;
extern std::string g_current_task;

AgentGUI* AgentGUI::self_ = nullptr;

static std::string get_appdata_config_path() {
    char path[MAX_PATH];
    if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, path))) {
        return std::string(path) + "\\PCManager_Agent\\agent_config.json";
    }
    return "";
}

static bool save_config_key(const std::string& new_key) {
    std::string cfg_path = get_appdata_config_path();
    if (cfg_path.empty()) return false;

    // Ensure parent directory exists
    size_t last_slash = cfg_path.find_last_of("\\/");
    if (last_slash != std::string::npos) {
        std::string parent_dir = cfg_path.substr(0, last_slash);
        CreateDirectoryA(parent_dir.c_str(), NULL);
    }

    json cfg;
    bool parsed = false;

    // 1. Try reading AppData config
    std::ifstream f(cfg_path);
    if (f.is_open()) {
        try {
            f >> cfg;
            parsed = true;
        } catch (...) {}
        f.close();
    }

    // 2. Try local agent_config.json fallback
    if (!parsed) {
        std::ifstream local_f("agent_config.json");
        if (local_f.is_open()) {
            try {
                local_f >> cfg;
                parsed = true;
            } catch (...) {}
            local_f.close();
        }
    }

    // Set config values
    cfg["access_key"] = new_key;
    if (!cfg.contains("server_base_url") || cfg["server_base_url"].get<std::string>().empty()) {
        cfg["server_base_url"] = SERVER_BASE_URL;
    }
    if (!cfg.contains("agent_id") || cfg["agent_id"].get<std::string>().empty()) {
        cfg["agent_id"] = AGENT_ID;
    }
    if (!cfg.contains("agent_name") || cfg["agent_name"].get<std::string>().empty()) {
        cfg["agent_name"] = AGENT_NAME;
    }
    if (!cfg.contains("heartbeat_interval_seconds")) {
        cfg["heartbeat_interval_seconds"] = HEARTBEAT_INTERVAL;
    }
    if (!cfg.contains("task_poll_interval_seconds")) {
        cfg["task_poll_interval_seconds"] = TASK_POLL_INTERVAL;
    }

    // Save to AppData
    std::ofstream out(cfg_path, std::ios::trunc);
    if (!out.is_open()) return false;
    out << cfg.dump(4);
    out.close();

    // Save local copy
    std::ofstream local("agent_config.json", std::ios::trunc);
    if (local.is_open()) {
        local << cfg.dump(4);
        local.close();
    }

    return true;
}

static bool save_config_key_and_id(const std::string& new_key, const std::string& new_id) {
    std::string cfg_path = get_appdata_config_path();
    if (cfg_path.empty()) return false;

    // Ensure parent directory exists
    size_t last_slash = cfg_path.find_last_of("\\/");
    if (last_slash != std::string::npos) {
        std::string parent_dir = cfg_path.substr(0, last_slash);
        CreateDirectoryA(parent_dir.c_str(), NULL);
    }

    json cfg;
    bool parsed = false;

    // 1. Try reading AppData config
    std::ifstream f(cfg_path);
    if (f.is_open()) {
        try {
            f >> cfg;
            parsed = true;
        } catch (...) {}
        f.close();
    }

    // 2. Try local agent_config.json fallback
    if (!parsed) {
        std::ifstream local_f("agent_config.json");
        if (local_f.is_open()) {
            try {
                local_f >> cfg;
                parsed = true;
            } catch (...) {}
            local_f.close();
        }
    }

    // Set config values
    cfg["access_key"] = new_key;
    cfg["agent_id"] = new_id;
    cfg["agent_name"] = "PC " + new_id;
    if (!cfg.contains("server_base_url") || cfg["server_base_url"].get<std::string>().empty()) {
        cfg["server_base_url"] = SERVER_BASE_URL;
    }
    if (!cfg.contains("heartbeat_interval_seconds")) {
        cfg["heartbeat_interval_seconds"] = HEARTBEAT_INTERVAL;
    }
    if (!cfg.contains("task_poll_interval_seconds")) {
        cfg["task_poll_interval_seconds"] = TASK_POLL_INTERVAL;
    }

    // Save to AppData
    std::ofstream out(cfg_path, std::ios::trunc);
    if (!out.is_open()) return false;
    out << cfg.dump(4);
    out.close();

    // Save local copy
    std::ofstream local("agent_config.json", std::ios::trunc);
    if (local.is_open()) {
        local << cfg.dump(4);
        local.close();
    }

    return true;
}

static std::wstring utf8_to_wstring(const std::string& str) {
    if (str.empty()) return L"";
    int size_needed = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), NULL, 0);
    if (size_needed <= 0) return L"";
    std::wstring wstrTo(size_needed, 0);
    MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), &wstrTo[0], size_needed);
    return wstrTo;
}

static void activate_agent_async(std::string code, HWND hSaveBtn, HWND hStatusLabel, HWND hCodeEdit) {
    EnableWindow(hSaveBtn, FALSE);
    SetWindowTextW(hStatusLabel, L"\u0410\u043A\u0442\u0438\u0432\u0430\u0446\u0438\u044F..."); // "Активация..."

    std::thread([code, hSaveBtn, hStatusLabel, hCodeEdit]() {
        try {
            json sys = WinUtils::get_system_info();
            json net = WinUtils::get_network_info();

            json payload;
            payload["activation_key"] = code;
            payload["hostname"] = sys.value("hostname", "WindowsPC");
            payload["username"] = sys.value("username", "");
            payload["platform"] = "Windows";
            payload["os_name"] = sys.value("os", "Windows 10/11");
            payload["local_ip"] = net.value("ip_address", "127.0.0.1");

            HttpClient client(SERVER_BASE_URL, "", "");
            HttpResponse resp = client.request("POST", "/api/agents/activate", payload.dump());

            if (resp.status_code == 200) {
                json res = json::parse(resp.body);
                if (res.contains("agent_id") && res.contains("agent_token")) {
                    std::string new_id = res["agent_id"].get<std::string>();
                    std::string new_token = res["agent_token"].get<std::string>();

                    if (save_config_key_and_id(new_token, new_id)) {
                        // Update globals
                        AGENT_ID = new_id;
                        ACCESS_KEY = new_token;
                        AGENT_NAME = "PC " + sys.value("hostname", "");

                        SetWindowTextW(hStatusLabel, L"\u0423\u0441\u043F\u0435\u0448\u043D\u043E! \u041F\u0435\u0440\u0435\u0437\u0430\u043F\u0443\u0441\u0442\u0438\u0442\u0435 \u043F\u0440\u0438\u043B\u043E\u0436\u0435\u043D\u0438\u0435."); // "Успешно! Перезапустите приложение."
                    } else {
                        SetWindowTextW(hStatusLabel, L"\u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u043F\u0438\u0441\u0438 \u043A\u043E\u043D\u0444\u0438\u0433\u0430"); // "Ошибка записи конфига"
                    }
                } else {
                    SetWindowTextW(hStatusLabel, L"\u041D\u0435\u0432\u0435\u0440\u043D\u044B\u0439 \u043E\u0442\u0432\u0435\u0442 \u0441\u0435\u0440\u0432\u0435\u0440\u0430"); // "Неверный ответ сервера"
                }
            } else {
                std::string err_detail = "Ошибка активации";
                try {
                    json err = json::parse(resp.body);
                    if (err.contains("detail")) {
                        err_detail = err["detail"].get<std::string>();
                    }
                } catch (...) {}
                SetWindowTextW(hStatusLabel, utf8_to_wstring(err_detail).c_str());
            }
        } catch (const std::exception& e) {
            std::string msg = "Error: ";
            msg += e.what();
            SetWindowTextW(hStatusLabel, utf8_to_wstring(msg).c_str());
        } catch (...) {
            SetWindowTextW(hStatusLabel, L"\u041D\u0435\u0438\u0437\u0432\u0435\u0441\u0442\u043D\u0430\u044F \u043E\u0448\u0438\u0431\u043A\u0430"); // "Неизвестная ошибка"
        }
        EnableWindow(hSaveBtn, TRUE);
    }).detach();
}

static const COLORREF CLR_APP    = RGB(12, 11, 16);   // #0C0B10
static const COLORREF CLR_SIDE   = RGB(19, 18, 28);   // #13121C
static const COLORREF CLR_PANEL  = RGB(22, 21, 35);   // #161523
static const COLORREF CLR_ACCENT = RGB(124, 58, 237); // #7C3AED
static const COLORREF CLR_TXT    = RGB(124, 120, 146); // #7C7892
static const COLORREF CLR_WHT    = RGB(255, 255, 255); // #FFFFFF
static const COLORREF CLR_PROG   = RGB(35, 33, 53);   // #232135

#define IDC_BTN_DASH   1101
#define IDC_BTN_SETT   1102
#define IDC_BTN_TASKS  1103
#define IDC_BOTTOM_BAR 1200

static void sf(HWND h, HFONT f) { SendMessageW(h, WM_SETFONT, (WPARAM)f, TRUE); }
static HFONT mf(int h, int w, const char* n) {
    LOGFONTA l = {}; l.lfHeight = h; l.lfWeight = w; strcpy_s(l.lfFaceName, n);
    return CreateFontIndirectA(&l);
}

AgentGUI::AgentGUI(HINSTANCE hInst, const std::string& aid)
    : hInst_(hInst), hWnd_(nullptr), hContent_(nullptr),
      hStatusLabelBottom_(nullptr), visible_(false), agent_id_(aid), current_page_(0),
      hBtnMin_(nullptr), hBtnClose_(nullptr),
      hBtnDash_(nullptr), hBtnSettings_(nullptr), hBtnTasks_(nullptr),
      hDashPanel_(nullptr),
      cpu_val_(L"0.0%"), ram_val_(L"0.0%"), disk_val_(L"0.0%"),
      cpu_pct_(0), ram_pct_(0), disk_pct_(0),
      battery_(L"N/A"), network_(L"N/A"), uptime_(L"N/A"),
      status_text_(L"Connecting to server..."), is_online_(false),
      hSettingsPanel_(nullptr), hCodeEdit_(nullptr), hSaveBtn_(nullptr), hSaveStatusLabel_(nullptr),
      hTasksPanel_(nullptr), hTaskList_(nullptr),
      hFont_(nullptr), hFontTitle_(nullptr), hFontBig_(nullptr),
      hFontWindowTitle_(nullptr), hFontSidebarHeader_(nullptr), hFontSidebarBtn_(nullptr),
      hFontCardTitle_(nullptr), hFontCardValue_(nullptr), hIcon_(nullptr),
      hBrushSide_(CreateSolidBrush(CLR_SIDE)),
      hBrushPanel_(CreateSolidBrush(CLR_PANEL)),
      hBrushProg_(CreateSolidBrush(CLR_PROG)),
      hBrushApp_(CreateSolidBrush(CLR_APP)) {
    self_ = this;
}

AgentGUI::~AgentGUI() {
    if (hFont_) DeleteObject(hFont_);
    if (hFontTitle_) DeleteObject(hFontTitle_);
    if (hFontBig_) DeleteObject(hFontBig_);
    if (hFontWindowTitle_) DeleteObject(hFontWindowTitle_);
    if (hFontSidebarHeader_) DeleteObject(hFontSidebarHeader_);
    if (hFontSidebarBtn_) DeleteObject(hFontSidebarBtn_);
    if (hFontCardTitle_) DeleteObject(hFontCardTitle_);
    if (hFontCardValue_) DeleteObject(hFontCardValue_);
    if (hBrushSide_) DeleteObject(hBrushSide_);
    if (hBrushPanel_) DeleteObject(hBrushPanel_);
    if (hBrushProg_) DeleteObject(hBrushProg_);
    if (hBrushApp_) DeleteObject(hBrushApp_);
    self_ = nullptr;
}

void AgentGUI::create_fonts() {
    hFont_ = mf(-13, FW_NORMAL, "Segoe UI");
    hFontTitle_ = mf(-15, FW_SEMIBOLD, "Segoe UI");
    hFontBig_ = mf(-22, FW_BOLD, "Segoe UI");

    hFontWindowTitle_ = mf(-12, FW_BOLD, "Segoe UI");
    hFontSidebarHeader_ = mf(-19, FW_BOLD, "Segoe UI");
    hFontSidebarBtn_ = mf(-15, FW_NORMAL, "Segoe UI");
    hFontCardTitle_ = mf(-13, FW_BOLD, "Segoe UI");
    hFontCardValue_ = mf(-37, FW_BOLD, "Segoe UI");
}

void AgentGUI::create_window(HINSTANCE hInstance) {
    WNDCLASSEXW wc = {};
    wc.cbSize = sizeof(wc);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = NULL;
    wc.lpszClassName = L"PCManagerAgentMainClass";
    RegisterClassExW(&wc);

    hIcon_ = (HICON)LoadImageW(hInstance, MAKEINTRESOURCEW(100), IMAGE_ICON, 32, 32, LR_DEFAULTCOLOR);
    if (!hIcon_) hIcon_ = LoadIcon(NULL, IDI_APPLICATION);

    int screen_w = GetSystemMetrics(SM_CXSCREEN);
    int screen_h = GetSystemMetrics(SM_CYSCREEN);
    int w = 760;
    int h = 520;
    int x = (screen_w - w) / 2;
    int y = (screen_h - h) / 2;

    hWnd_ = CreateWindowExW(0, L"PCManagerAgentMainClass", L"PCManager Agent Dashboard",
        WS_POPUP | WS_SYSMENU,
        x, y, w, h,
        NULL, NULL, hInstance, NULL);

    if (hWnd_) {
        SendMessageW(hWnd_, WM_SETICON, ICON_BIG, (LPARAM)hIcon_);
        SendMessageW(hWnd_, WM_SETICON, ICON_SMALL, (LPARAM)hIcon_);
    }
}

void AgentGUI::create_sidebar() {
    auto mkbtn = [&](int id, const wchar_t* t, int yy) -> HWND {
        HWND h = CreateWindowExW(0, L"BUTTON", t,
            WS_CHILD | WS_VISIBLE | BS_OWNERDRAW,
            8, yy, 184, 40, hWnd_, (HMENU)(INT_PTR)id, hInst_, NULL);
        sf(h, hFontSidebarBtn_);
        return h;
    };

    hBtnDash_ = mkbtn(IDC_BTN_DASH, L"\U0001F3E0  Dashboard", 120);
    hBtnTasks_ = mkbtn(IDC_BTN_TASKS, L"\U0001F4CB  Tasks", 168);
    hBtnSettings_ = mkbtn(IDC_BTN_SETT, L"\u2699  Settings", 216);

    // Custom Minimize / Close Buttons in Title Bar
    hBtnMin_ = CreateWindowExW(0, L"BUTTON", L"—",
        WS_CHILD | WS_VISIBLE | BS_OWNERDRAW,
        760 - 80, 0, 40, 32, hWnd_, (HMENU)1301, hInst_, NULL);
    sf(hBtnMin_, hFontWindowTitle_);

    hBtnClose_ = CreateWindowExW(0, L"BUTTON", L"✕",
        WS_CHILD | WS_VISIBLE | BS_OWNERDRAW,
        760 - 40, 0, 40, 32, hWnd_, (HMENU)1302, hInst_, NULL);
    sf(hBtnClose_, hFontWindowTitle_);

    hContent_ = CreateWindowExW(0, L"STATIC", L"", WS_CHILD | WS_VISIBLE,
        200, 32, 560, 488, hWnd_, NULL, hInst_, NULL);

    InvalidateRect(hWnd_, NULL, TRUE);
}

void AgentGUI::create_dashboard() {
    RECT rc;
    GetClientRect(hContent_, &rc);

    hDashPanel_ = CreateWindowExW(0, L"STATIC", L"", WS_CHILD | WS_VISIBLE,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);

    // Subclass the dashboard panel to handle GDI owner drawing
    SetWindowSubclass(hDashPanel_, SubclassPanelProc, 1, (DWORD_PTR)this);
}

void AgentGUI::create_settings() {
    RECT rc;
    GetClientRect(hContent_, &rc);
    int x = 30, y = 25, w = rc.right - 60;

    hSettingsPanel_ = CreateWindowExW(0, L"STATIC", L"", WS_CHILD,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);

    HWND hT = CreateWindowExW(0, L"STATIC", L"Connection Configuration",
        WS_CHILD | WS_VISIBLE, x, y, w, 28, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hT, hFontTitle_);
    y += 45;

    std::wstring idStr = L"Agent ID: " + utf8_to_wstring(agent_id_);
    HWND hId = CreateWindowExW(0, L"STATIC", idStr.c_str(),
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hId, hFontSidebarBtn_);
    y += 28;

    HWND hVer = CreateWindowExW(0, L"STATIC", L"Version: C++ Agent 1.7.0",
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hVer, hFontSidebarBtn_);
    y += 36;

    HWND hCodeLabel = CreateWindowExW(0, L"STATIC", L"Activation Key (TG-XXXX-XXXX) or Access Token:",
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hCodeLabel, hFontSidebarBtn_);
    y += 24;

    hCodeEdit_ = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"",
        WS_CHILD | WS_VISIBLE | ES_LEFT | ES_AUTOHSCROLL,
        x, y, w - 40, 32, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hCodeEdit_, hFontSidebarBtn_);
    
    SendMessageW(hCodeEdit_, EM_SETCUEBANNER, TRUE, (LPARAM)L"Enter key from Telegram bot");

    // Fill with current key
    std::wstring currentKey = utf8_to_wstring(ACCESS_KEY);
    SetWindowTextW(hCodeEdit_, currentKey.c_str());

    y += 45;

    hSaveBtn_ = CreateWindowExW(0, L"BUTTON", L"Save & Reconnect",
        WS_CHILD | WS_VISIBLE | BS_OWNERDRAW,
        x, y, 180, 40, hSettingsPanel_, (HMENU)(INT_PTR)1201, hInst_, NULL);
    sf(hSaveBtn_, hFontSidebarBtn_);
    y += 55;

    hSaveStatusLabel_ = CreateWindowExW(0, L"STATIC", L"",
        WS_CHILD | WS_VISIBLE, x, y, w, 24, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hSaveStatusLabel_, hFontSidebarBtn_);
}

void AgentGUI::create_tasks() {
    RECT rc;
    GetClientRect(hContent_, &rc);

    hTasksPanel_ = CreateWindowExW(0, L"STATIC", L"", WS_CHILD,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);

    HWND hT = CreateWindowExW(0, L"STATIC", L"Task History Log",
        WS_CHILD | WS_VISIBLE, 30, 25, rc.right - 60, 28, hTasksPanel_, NULL, hInst_, NULL);
    sf(hT, hFontTitle_);

    hTaskList_ = CreateWindowExW(WS_EX_CLIENTEDGE, WC_LISTVIEWW, L"",
        WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | LVS_NOSORTHEADER,
        30, 70, rc.right - 60, rc.bottom - 100, hTasksPanel_, NULL, hInst_, NULL);

    SendMessageW(hTaskList_, LVM_SETBKCOLOR, 0, (LPARAM)CLR_PANEL);
    SendMessageW(hTaskList_, LVM_SETTEXTBKCOLOR, 0, (LPARAM)CLR_PANEL);
    SendMessageW(hTaskList_, LVM_SETTEXTCOLOR, 0, (LPARAM)CLR_TXT);

    // Apply Explorer theme to the ListView
    SetWindowTheme(hTaskList_, L"Explorer", NULL);

    LVCOLUMNW lc = {};
    lc.mask = LVCF_TEXT | LVCF_WIDTH | LVCF_FMT;
    lc.fmt = LVCFMT_LEFT;
    
    lc.cx = 100; lc.pszText = (wchar_t*)L"Time";
    SendMessageW(hTaskList_, LVM_INSERTCOLUMNW, 0, (LPARAM)&lc);
    lc.cx = 150; lc.pszText = (wchar_t*)L"Task ID";
    SendMessageW(hTaskList_, LVM_INSERTCOLUMNW, 1, (LPARAM)&lc);
    lc.cx = 130; lc.pszText = (wchar_t*)L"Action";
    SendMessageW(hTaskList_, LVM_INSERTCOLUMNW, 2, (LPARAM)&lc);
    lc.cx = 100; lc.pszText = (wchar_t*)L"Status";
    SendMessageW(hTaskList_, LVM_INSERTCOLUMNW, 3, (LPARAM)&lc);

    SendMessageW(hTaskList_, LVM_SETEXTENDEDLISTVIEWSTYLE, 0, (LPARAM)LVS_EX_FULLROWSELECT);
}

bool AgentGUI::create() {
    INITCOMMONCONTROLSEX ix = {sizeof(ix), ICC_PROGRESS_CLASS | ICC_LISTVIEW_CLASSES};
    InitCommonControlsEx(&ix);
    create_fonts();
    create_window(hInst_);
    if (!hWnd_) return false;

    create_sidebar();
    create_dashboard();
    create_settings();
    create_tasks();

    ShowWindow(hSettingsPanel_, SW_HIDE);
    ShowWindow(hTasksPanel_, SW_HIDE);
    return true;
}

void AgentGUI::show() { visible_ = true; ShowWindow(hWnd_, SW_SHOW); UpdateWindow(hWnd_); }
void AgentGUI::hide() { visible_ = false; ShowWindow(hWnd_, SW_HIDE); }

void AgentGUI::switch_page(int idx) {
    ShowWindow(hDashPanel_, idx == 0 ? SW_SHOW : SW_HIDE);
    ShowWindow(hSettingsPanel_, idx == 1 ? SW_SHOW : SW_HIDE);
    ShowWindow(hTasksPanel_, idx == 2 ? SW_SHOW : SW_HIDE);
    current_page_ = idx;
    InvalidateRect(hWnd_, NULL, TRUE);
}

void AgentGUI::update_task_list() {
    if (!hTaskList_) return;
    SendMessageA(hTaskList_, LVM_DELETEALLITEMS, 0, 0);
    for (size_t i = 0; i < tasks_.size(); i++) {
        LVITEMA lv = {};
        lv.mask = LVIF_TEXT;
        lv.iItem = (int)i;
        lv.pszText = (char*)tasks_[i].time.c_str();
        SendMessageA(hTaskList_, LVM_INSERTITEMA, 0, (LPARAM)&lv);
        LVITEMA ls = {};
        ls.iItem = (int)i;
        ls.iSubItem = 1; ls.pszText = (char*)tasks_[i].task_id.c_str();
        SendMessageA(hTaskList_, LVM_SETITEMA, 0, (LPARAM)&ls);
        ls.iSubItem = 2; ls.pszText = (char*)tasks_[i].action.c_str();
        SendMessageA(hTaskList_, LVM_SETITEMA, 0, (LPARAM)&ls);
        ls.iSubItem = 3; ls.pszText = (char*)tasks_[i].status.c_str();
        SendMessageA(hTaskList_, LVM_SETITEMA, 0, (LPARAM)&ls);
    }
}

void AgentGUI::update_bottom_bar() {
    // No bottom bar anymore in this UI layout
}

void AgentGUI::update_stats(const std::string& cpu, const std::string& ram,
                            const std::string& disk, const std::string& battery,
                            const std::string& network, const std::string& uptime) {
    try { cpu_pct_ = std::stoi(cpu); } catch (...) { cpu_pct_ = 0; }
    try { ram_pct_ = std::stoi(ram); } catch (...) { ram_pct_ = 0; }
    try { disk_pct_ = std::stoi(disk); } catch (...) { disk_pct_ = 0; }
    
    cpu_val_ = utf8_to_wstring(cpu) + L"%";
    ram_val_ = utf8_to_wstring(ram) + L"%";
    disk_val_ = utf8_to_wstring(disk) + L"%";
    
    battery_ = utf8_to_wstring(battery);
    network_ = utf8_to_wstring(network);
    uptime_ = utf8_to_wstring(uptime);

    if (hDashPanel_) {
        InvalidateRect(hDashPanel_, NULL, TRUE);
    }
}

void AgentGUI::update_status(const std::string& status, const std::string&) {
    is_online_ = (status == "Online");
    status_text_ = utf8_to_wstring(status);
    if (hDashPanel_) {
        InvalidateRect(hDashPanel_, NULL, TRUE);
    }
}

void AgentGUI::add_task(const TaskEntry& entry) {
    tasks_.push_back(entry);
    if (tasks_.size() > 100) tasks_.erase(tasks_.begin());
    update_task_list();
}

void AgentGUI::draw_dashboard_panel(HDC hdc) {
    RECT rc;
    GetClientRect(hDashPanel_, &rc);
    
    // Fill background with CLR_APP (#0C0B10)
    FillRect(hdc, &rc, hBrushApp_);
    
    // Draw Title: "System Status Overview"
    HFONT hOldFont = (HFONT)SelectObject(hdc, hFontTitle_);
    SetBkMode(hdc, TRANSPARENT);
    SetTextColor(hdc, CLR_WHT);
    
    RECT titleRc = { 30, 25, rc.right - 30, 60 };
    DrawTextW(hdc, L"System Status Overview", -1, &titleRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    
    // Check global WS connection state
    bool ws_connected = (g_ws && g_ws->is_connected());
    bool currently_online = ws_connected || is_online_;

    // Draw Connection Card
    RECT connRc = { 30, 70, rc.right - 30, 120 };
    
    HPEN hOldPen = (HPEN)SelectObject(hdc, GetStockObject(NULL_PEN));
    HBRUSH hCardBrush = CreateSolidBrush(CLR_PANEL); // #161523
    HBRUSH hOldBrush = (HBRUSH)SelectObject(hdc, hCardBrush);
    
    RoundRect(hdc, connRc.left, connRc.top, connRc.right, connRc.bottom, 20, 20); // 10px radius
    
    // Draw connection indicator (Dot)
    COLORREF dotColor = currently_online ? RGB(16, 185, 129) : RGB(239, 68, 68);
    HBRUSH hDotBrush = CreateSolidBrush(dotColor);
    SelectObject(hdc, hDotBrush);
    
    Ellipse(hdc, connRc.left + 20, connRc.top + 18, connRc.left + 32, connRc.top + 30); // 12x12 dot
    DeleteObject(hDotBrush);
    
    // Draw connection text
    COLORREF connTextColor = currently_online ? RGB(16, 185, 129) : CLR_TXT;
    SetTextColor(hdc, connTextColor);
    
    SelectObject(hdc, hFontCardTitle_);
    RECT connTextRc = { connRc.left + 45, connRc.top, connRc.right - 10, connRc.bottom };
    std::wstring connText = currently_online ? L"Connected to server successfully" : L"Connecting to server...";
    DrawTextW(hdc, connText.c_str(), -1, &connTextRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    
    // Draw Resource Cards (CPU & RAM)
    int midX = rc.right / 2;
    RECT cpuRc = { 30, 135, midX - 10, 285 };
    RECT ramRc = { midX + 10, 135, rc.right - 30, 285 };
    
    SelectObject(hdc, hCardBrush);
    RoundRect(hdc, cpuRc.left, cpuRc.top, cpuRc.right, cpuRc.bottom, 24, 24); // 12px radius
    RoundRect(hdc, ramRc.left, ramRc.top, ramRc.right, ramRc.bottom, 24, 24);
    
    // 1. CPU Card Details
    SetTextColor(hdc, CLR_TXT);
    SelectObject(hdc, hFontCardTitle_);
    RECT cpuTitleRc = { cpuRc.left + 20, cpuRc.top + 20, cpuRc.right - 20, cpuRc.top + 40 };
    DrawTextW(hdc, L"CPU Usage", -1, &cpuTitleRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    
    SetTextColor(hdc, CLR_WHT);
    SelectObject(hdc, hFontCardValue_);
    RECT cpuValRc = { cpuRc.left + 20, cpuRc.top + 45, cpuRc.right - 20, cpuRc.top + 95 };
    DrawTextW(hdc, cpu_val_.c_str(), -1, &cpuValRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    
    HBRUSH hProgBgBrush = CreateSolidBrush(CLR_PROG); // #232135
    SelectObject(hdc, hProgBgBrush);
    RECT cpuBarBg = { cpuRc.left + 20, cpuRc.top + 110, cpuRc.right - 20, cpuRc.top + 122 };
    RoundRect(hdc, cpuBarBg.left, cpuBarBg.top, cpuBarBg.right, cpuBarBg.bottom, 12, 12);
    
    HBRUSH hProgFillBrush = CreateSolidBrush(CLR_ACCENT); // #7C3AED
    SelectObject(hdc, hProgFillBrush);
    int cpuFillWidth = (cpuBarBg.right - cpuBarBg.left) * cpu_pct_ / 100;
    if (cpuFillWidth > 0) {
        if (cpuFillWidth < 12) cpuFillWidth = 12;
        RECT cpuBarFill = { cpuBarBg.left, cpuBarBg.top, cpuBarBg.left + cpuFillWidth, cpuBarBg.bottom };
        RoundRect(hdc, cpuBarFill.left, cpuBarFill.top, cpuBarFill.right, cpuBarFill.bottom, 12, 12);
    }
    
    // 2. RAM Card Details
    SetTextColor(hdc, CLR_TXT);
    SelectObject(hdc, hFontCardTitle_);
    RECT ramTitleRc = { ramRc.left + 20, ramRc.top + 20, ramRc.right - 20, ramRc.top + 40 };
    DrawTextW(hdc, L"RAM Usage", -1, &ramTitleRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    
    SetTextColor(hdc, CLR_WHT);
    SelectObject(hdc, hFontCardValue_);
    RECT ramValRc = { ramRc.left + 20, ramRc.top + 45, ramRc.right - 20, ramRc.top + 95 };
    DrawTextW(hdc, ram_val_.c_str(), -1, &ramValRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    
    SelectObject(hdc, hProgBgBrush);
    RECT ramBarBg = { ramRc.left + 20, ramRc.top + 110, ramRc.right - 20, ramRc.top + 122 };
    RoundRect(hdc, ramBarBg.left, ramBarBg.top, ramBarBg.right, ramBarBg.bottom, 12, 12);
    
    SelectObject(hdc, hProgFillBrush);
    int ramFillWidth = (ramBarBg.right - ramBarBg.left) * ram_pct_ / 100;
    if (ramFillWidth > 0) {
        if (ramFillWidth < 12) ramFillWidth = 12;
        RECT ramBarFill = { ramBarBg.left, ramBarBg.top, ramBarBg.left + ramFillWidth, ramBarBg.bottom };
        RoundRect(hdc, ramBarFill.left, ramBarFill.top, ramBarFill.right, ramBarFill.bottom, 12, 12);
    }
    
    DeleteObject(hProgBgBrush);
    DeleteObject(hProgFillBrush);
    
    // Draw Last Active Task Card
    RECT taskRc = { 30, 300, rc.right - 30, 350 };
    SelectObject(hdc, hCardBrush);
    RoundRect(hdc, taskRc.left, taskRc.top, taskRc.right, taskRc.bottom, 20, 20);
    
    SetTextColor(hdc, CLR_TXT);
    SelectObject(hdc, hFontCardTitle_);
    RECT taskTitleRc = { taskRc.left + 20, taskRc.top, taskRc.left + 150, taskRc.bottom };
    DrawTextW(hdc, L"Last Active Task:", -1, &taskTitleRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    
    SetTextColor(hdc, CLR_ACCENT);
    std::wstring taskVal = utf8_to_wstring(g_current_task);
    if (taskVal == L"-") taskVal = L"None";
    RECT taskValRc = { taskRc.left + 155, taskRc.top, taskRc.right - 10, taskRc.bottom };
    DrawTextW(hdc, taskVal.c_str(), -1, &taskValRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
    
    // Draw Bottom OS & Disk Info Badges
    RECT osRc = { 30, 365, midX - 10, 415 };
    RECT diskRc = { midX + 10, 365, rc.right - 30, 415 };
    
    SelectObject(hdc, hCardBrush);
    RoundRect(hdc, osRc.left, osRc.top, osRc.right, osRc.bottom, 16, 16);
    RoundRect(hdc, diskRc.left, diskRc.top, diskRc.right, diskRc.bottom, 16, 16);
    
    SetTextColor(hdc, CLR_TXT);
    SelectObject(hdc, hFontWindowTitle_);
    
    json sysInfo = WinUtils::get_system_info();
    std::string osName = sysInfo.contains("os") ? sysInfo["os"].get<std::string>() : "Windows 11";
    std::wstring osText = L"\U0001F5A5  OS: " + utf8_to_wstring(osName);
    RECT osTextRc = { osRc.left + 10, osRc.top, osRc.right - 10, osRc.bottom };
    DrawTextW(hdc, osText.c_str(), -1, &osTextRc, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
    
    std::wstring diskText = L"\U0001F4BE  Disk C: " + disk_val_;
    RECT diskTextRc = { diskRc.left + 10, diskRc.top, diskRc.right - 10, diskRc.bottom };
    DrawTextW(hdc, diskText.c_str(), -1, &diskTextRc, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
    
    SelectObject(hdc, hOldBrush);
    SelectObject(hdc, hOldPen);
    SelectObject(hdc, hOldFont);
    DeleteObject(hCardBrush);
}

LRESULT CALLBACK AgentGUI::SubclassPanelProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam, UINT_PTR uIdSubclass, DWORD_PTR dwRefData) {
    AgentGUI* pGUI = (AgentGUI*)dwRefData;
    if (msg == WM_PAINT) {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hWnd, &ps);
        
        RECT rc;
        GetClientRect(hWnd, &rc);
        
        // Double buffering to prevent flickering
        HDC hdcMem = CreateCompatibleDC(hdc);
        HBITMAP hbmMem = CreateCompatibleBitmap(hdc, rc.right, rc.bottom);
        HBITMAP hOldBm = (HBITMAP)SelectObject(hdcMem, hbmMem);
        
        pGUI->draw_dashboard_panel(hdcMem);
        
        BitBlt(hdc, 0, 0, rc.right, rc.bottom, hdcMem, 0, 0, SRCCOPY);
        
        SelectObject(hdcMem, hOldBm);
        DeleteObject(hbmMem);
        DeleteDC(hdcMem);
        
        EndPaint(hWnd, &ps);
        return 0;
    }
    return DefSubclassProc(hWnd, msg, wParam, lParam);
}

LRESULT CALLBACK AgentGUI::WndProc(HWND hWnd, UINT msg, WPARAM w, LPARAM l) {
    if (!self_) return DefWindowProcW(hWnd, msg, w, l);

    switch (msg) {
    case WM_NCHITTEST: {
        POINT pt = { GET_X_LPARAM(l), GET_Y_LPARAM(l) };
        ScreenToClient(hWnd, &pt);
        if (pt.y >= 0 && pt.y < 32) {
            if (pt.x >= 760 - 80) {
                return HTCLIENT; // let minimize and close buttons receive input
            }
            return HTCAPTION; // drag window
        }
        return HTCLIENT;
    }

    case WM_DRAWITEM: {
        DRAWITEMSTRUCT* pDIS = (DRAWITEMSTRUCT*)l;
        if (pDIS->CtlType == ODT_BUTTON) {
            HDC hdc = pDIS->hDC;
            RECT rc = pDIS->rcItem;
            HWND hwnd = pDIS->hwndItem;
            
            wchar_t text[256] = {0};
            GetWindowTextW(hwnd, text, 255);
            
            bool is_active_tab = false;
            bool is_save_btn = (pDIS->CtlID == 1201);
            bool is_sys_btn = (pDIS->CtlID == 1301 || pDIS->CtlID == 1302);
            
            if (is_sys_btn) {
                bool is_close = (pDIS->CtlID == 1302);
                bool is_pressed = (pDIS->itemState & ODS_SELECTED);
                COLORREF bg = CLR_APP;
                if (is_pressed) {
                    bg = is_close ? RGB(0xEF, 0x44, 0x44) : RGB(30, 27, 48);
                }
                HBRUSH hBr = CreateSolidBrush(bg);
                FillRect(hdc, &rc, hBr);
                DeleteObject(hBr);
                
                SetBkMode(hdc, TRANSPARENT);
                SetTextColor(hdc, CLR_TXT);
                DrawTextW(hdc, text, -1, &rc, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
                return TRUE;
            }
            
            if (!is_save_btn && self_) {
                int btn_idx = (hwnd == self_->hBtnDash_) ? 0 : 
                              (hwnd == self_->hBtnSettings_) ? 1 : 
                              (hwnd == self_->hBtnTasks_) ? 2 : -1;
                is_active_tab = (btn_idx == self_->current_page_);
            }
            
            bool is_pressed = (pDIS->itemState & ODS_SELECTED);
            HBRUSH hBgBrush = NULL;
            COLORREF textColor = CLR_TXT;
            
            if (is_save_btn) {
                if (is_pressed) {
                    hBgBrush = CreateSolidBrush(RGB(109, 40, 217)); // Darker purple
                } else {
                    hBgBrush = CreateSolidBrush(CLR_ACCENT); // Accent purple
                }
                textColor = RGB(255, 255, 255);
            } else {
                if (is_active_tab) {
                    hBgBrush = CreateSolidBrush(CLR_ACCENT); // Selected tab matching Python agent
                    textColor = CLR_WHT;
                } else if (is_pressed) {
                    hBgBrush = CreateSolidBrush(RGB(30, 27, 48));
                    textColor = CLR_WHT;
                } else {
                    hBgBrush = CreateSolidBrush(CLR_SIDE); // Sidebar bg
                    textColor = CLR_TXT;
                }
            }
            
            FillRect(hdc, &rc, hBgBrush);
            DeleteObject(hBgBrush);
            
            SetBkMode(hdc, TRANSPARENT);
            SetTextColor(hdc, textColor);
            
            RECT textRc = rc;
            if (is_save_btn) {
                DrawTextW(hdc, text, -1, &textRc, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
            } else {
                textRc.left += 20; // Indent sidebar button text
                DrawTextW(hdc, text, -1, &textRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
            }
            return TRUE;
        }
        break;
    }

    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hWnd, &ps);
        
        RECT rc;
        GetClientRect(hWnd, &rc);
        
        // Draw title bar background (0,0 to 760,32)
        RECT titleBarRc = { 0, 0, rc.right, 32 };
        FillRect(hdc, &titleBarRc, self_->hBrushApp_);
        
        // Draw sidebar background (0,32 to 200,520)
        RECT sidebarRc = { 0, 32, SIDEBAR_W, rc.bottom };
        FillRect(hdc, &sidebarRc, self_->hBrushSide_);
        
        // Draw content area background (200,32 to 760,520)
        RECT contentRc = { SIDEBAR_W, 32, rc.right, rc.bottom };
        FillRect(hdc, &contentRc, self_->hBrushApp_);
        
        // Draw sidebar logo and headers in sidebar
        if (self_->hIcon_) {
            DrawIconEx(hdc, 20, 50, self_->hIcon_, 32, 32, 0, NULL, DI_NORMAL);
        }
        
        SetBkMode(hdc, TRANSPARENT);
        SetTextColor(hdc, CLR_ACCENT);
        HFONT hOldFont = (HFONT)SelectObject(hdc, self_->hFontSidebarHeader_);
        RECT logoTextRc = { 60, 48, 190, 80 };
        DrawTextW(hdc, L"PCManager", -1, &logoTextRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
        
        SetTextColor(hdc, CLR_TXT);
        SelectObject(hdc, self_->hFont_);
        RECT subtitleRc = { 60, 74, 190, 95 };
        DrawTextW(hdc, L"Windows Agent", -1, &subtitleRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
        
        // Draw window title text in title bar
        SetTextColor(hdc, CLR_TXT);
        SelectObject(hdc, self_->hFontWindowTitle_);
        RECT titleTextRc = { 10, 0, 500, 32 };
        DrawTextW(hdc, L"PCManager Agent Dashboard", -1, &titleTextRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
        
        // Draw 1px purple border around the entire window
        HPEN hBorderPen = CreatePen(PS_SOLID, 1, CLR_ACCENT);
        HPEN hOldPen = (HPEN)SelectObject(hdc, hBorderPen);
        HBRUSH hOldBrush = (HBRUSH)SelectObject(hdc, GetStockObject(NULL_BRUSH));
        Rectangle(hdc, 0, 0, rc.right, rc.bottom);
        SelectObject(hdc, hOldBrush);
        SelectObject(hdc, hOldPen);
        DeleteObject(hBorderPen);
        
        SelectObject(hdc, hOldFont);
        EndPaint(hWnd, &ps);
        return 0;
    }

    case WM_ERASEBKGND:
        return 1; // Prevent background erasing to stop flicker

    case WM_CTLCOLORSTATIC: {
        HDC hdc = (HDC)w;
        HWND hc = (HWND)l;
        SetBkMode(hdc, TRANSPARENT);
        
        HFONT hf = (HFONT)SendMessageW(hc, WM_GETFONT, 0, 0);
        if (hf == self_->hFontTitle_ || hf == self_->hFontBig_) {
            SetTextColor(hdc, CLR_WHT);
        } else {
            SetTextColor(hdc, CLR_TXT);
        }
        
        // Return brush matching the app background color
        return (LRESULT)self_->hBrushApp_;
    }

    case WM_CTLCOLORBTN: {
        return (LRESULT)self_->hBrushApp_;
    }

    case WM_CTLCOLOREDIT: {
        HDC hdc = (HDC)w;
        SetTextColor(hdc, CLR_WHT);
        SetBkColor(hdc, CLR_PANEL);
        return (LRESULT)self_->hBrushPanel_;
    }

    case WM_COMMAND: {
        int id = LOWORD(w);
        if (id == IDC_BTN_DASH) self_->switch_page(0);
        else if (id == IDC_BTN_SETT) self_->switch_page(1);
        else if (id == IDC_BTN_TASKS) self_->switch_page(2);
        else if (id == 1301) { // Minimize
            ShowWindow(hWnd, SW_MINIMIZE);
        }
        else if (id == 1302) { // Close
            ShowWindow(hWnd, SW_HIDE);
        }
        else if (id == 1201) {
            // Save button clicked
            wchar_t wbuf[512] = {0};
            GetWindowTextW(self_->hCodeEdit_, wbuf, 511);
            std::wstring wcode(wbuf);
            
            // Trim whitespace
            wcode.erase(0, wcode.find_first_not_of(L" \t\r\n"));
            wcode.erase(wcode.find_last_not_of(L" \t\r\n") + 1);

            if (wcode.empty()) {
                SetWindowTextW(self_->hSaveStatusLabel_, L"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043A\u043E\u0434 \u0438\u0437 Telegram"); // "Введите код из Telegram"
                break;
            }

            // Convert back to string
            int size_needed = WideCharToMultiByte(CP_UTF8, 0, wcode.c_str(), (int)wcode.size(), NULL, 0, NULL, NULL);
            std::string code(size_needed, 0);
            WideCharToMultiByte(CP_UTF8, 0, wcode.c_str(), (int)wcode.size(), &code[0], size_needed, NULL, NULL);

            std::string code_upper = code;
            std::transform(code_upper.begin(), code_upper.end(), code_upper.begin(), ::toupper);
            if (code_upper.rfind("TG-", 0) == 0) {
                activate_agent_async(code, self_->hSaveBtn_, self_->hSaveStatusLabel_, self_->hCodeEdit_);
            } else {
                if (save_config_key(code)) {
                    SetWindowTextW(self_->hSaveStatusLabel_, L"\u041A\u043E\u0434 \u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D! \u041F\u0435\u0440\u0435\u0437\u0430\u043F\u0443\u0441\u0442\u0438\u0442\u0435 \u0430\u0433\u0435\u043D\u0442\u0430"); // "Код сохранён! Перезапустите агента"
                } else {
                    SetWindowTextW(self_->hSaveStatusLabel_, L"\u041E\u0448\u0438\u0431\u043A\u0430 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u0438\u044F"); // "Ошибка сохранения"
                }
            }
        }
        return 0;
    }

    case WM_SIZE: {
        RECT rc;
        GetClientRect(hWnd, &rc);
        int cw = rc.right - SIDEBAR_W;
        int ch = rc.bottom - 32;
        if (self_->hContent_)
            SetWindowPos(self_->hContent_, NULL, SIDEBAR_W, 32, cw, ch, SWP_NOZORDER);

        RECT cr;
        if (self_->hContent_) GetClientRect(self_->hContent_, &cr);
        if (self_->hDashPanel_) SetWindowPos(self_->hDashPanel_, NULL, 0, 0, cr.right, cr.bottom, SWP_NOZORDER);
        if (self_->hSettingsPanel_) SetWindowPos(self_->hSettingsPanel_, NULL, 0, 0, cr.right, cr.bottom, SWP_NOZORDER);
        if (self_->hTasksPanel_) SetWindowPos(self_->hTasksPanel_, NULL, 0, 0, cr.right, cr.bottom, SWP_NOZORDER);
        if (self_->hTaskList_)
            SetWindowPos(self_->hTaskList_, NULL, 30, 70, cr.right - 60, cr.bottom - 100, SWP_NOZORDER);
        return 0;
    }

    case WM_CLOSE:
        ShowWindow(hWnd, SW_HIDE);
        return 0;

    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    }

    return DefWindowProcW(hWnd, msg, w, l);
}
