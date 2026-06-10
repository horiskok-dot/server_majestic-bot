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
      hBtnDash_(nullptr), hBtnGames_(nullptr), hBtnSettings_(nullptr), hBtnTasks_(nullptr),
      hDashPanel_(nullptr), hGamesPanel_(nullptr),
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

    hBtnDash_ = mkbtn(IDC_BTN_DASH, L"\u25C6  Dashboard", 120);
    hBtnGames_ = mkbtn(1104, L"\u25A0  Games", 168);
    hBtnTasks_ = mkbtn(IDC_BTN_TASKS, L"\u25B2  Tasks", 216);
    hBtnSettings_ = mkbtn(IDC_BTN_SETT, L"\u2699  Settings", 264);

    // Custom Minimize / Close Buttons in Title Bar
    hBtnMin_ = CreateWindowExW(0, L"BUTTON", L"\u2014",
        WS_CHILD | WS_VISIBLE | BS_OWNERDRAW,
        760 - 80, 0, 40, 32, hWnd_, (HMENU)1301, hInst_, NULL);
    sf(hBtnMin_, hFontWindowTitle_);

    hBtnClose_ = CreateWindowExW(0, L"BUTTON", L"\u2715",
        WS_CHILD | WS_VISIBLE | BS_OWNERDRAW,
        760 - 40, 0, 40, 32, hWnd_, (HMENU)1302, hInst_, NULL);
    sf(hBtnClose_, hFontWindowTitle_);

    hContent_ = CreateWindowExW(0, L"STATIC", L"", WS_CHILD | WS_VISIBLE,
        200, 32, 560, 488, hWnd_, NULL, hInst_, NULL);

    SetWindowTheme(hContent_, L"", L"");
    SetWindowSubclass(hContent_, SubclassPanelProc, 5, (DWORD_PTR)this);

    InvalidateRect(hWnd_, NULL, TRUE);
}

void AgentGUI::create_dashboard() {
    RECT rc;
    GetClientRect(hContent_, &rc);

    hDashPanel_ = CreateWindowExW(0, L"STATIC", L"", WS_CHILD | WS_VISIBLE,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);

    SetWindowSubclass(hDashPanel_, SubclassPanelProc, 1, (DWORD_PTR)this);
}

void AgentGUI::create_games() {
    RECT rc;
    GetClientRect(hContent_, &rc);

    hGamesPanel_ = CreateWindowExW(0, L"STATIC", L"", WS_CHILD,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);

    SetWindowSubclass(hGamesPanel_, SubclassPanelProc, 2, (DWORD_PTR)this);
}

void AgentGUI::create_settings() {
    RECT rc;
    GetClientRect(hContent_, &rc);
    int x = 30, y = 25, w = rc.right - 60;

    hSettingsPanel_ = CreateWindowExW(0, L"STATIC", L"", WS_CHILD,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);
    SetWindowTheme(hSettingsPanel_, L"", L"");

    HWND hT = CreateWindowExW(0, L"STATIC", L"Connection Configuration",
        WS_CHILD | WS_VISIBLE, x, y, w, 28, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hT, hFontTitle_);
    SetWindowTheme(hT, L"", L"");
    y += 45;

    std::wstring idStr = L"Agent ID: " + utf8_to_wstring(agent_id_);
    HWND hId = CreateWindowExW(0, L"STATIC", idStr.c_str(),
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hId, hFontSidebarBtn_);
    SetWindowTheme(hId, L"", L"");
    y += 28;

    HWND hVer = CreateWindowExW(0, L"STATIC", L"Version: C++ Agent 1.7.0",
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hVer, hFontSidebarBtn_);
    SetWindowTheme(hVer, L"", L"");
    y += 36;

    HWND hCodeLabel = CreateWindowExW(0, L"STATIC", L"Activation Key (TG-XXXX-XXXX) or Access Token:",
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hCodeLabel, hFontSidebarBtn_);
    SetWindowTheme(hCodeLabel, L"", L"");
    y += 24;

    hCodeEdit_ = CreateWindowExW(0, L"EDIT", L"",
        WS_CHILD | WS_VISIBLE | ES_LEFT | ES_AUTOHSCROLL,
        x, y, w - 40, 32, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hCodeEdit_, hFontSidebarBtn_);
    SetWindowTheme(hCodeEdit_, L"", L"");
    
    SendMessageW(hCodeEdit_, EM_SETCUEBANNER, TRUE, (LPARAM)L"Enter key from Telegram bot");

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
    SetWindowTheme(hSaveStatusLabel_, L"", L"");

    SetWindowSubclass(hSettingsPanel_, SubclassPanelProc, 3, (DWORD_PTR)this);
}

void AgentGUI::create_tasks() {
    RECT rc;
    GetClientRect(hContent_, &rc);

    hTasksPanel_ = CreateWindowExW(0, L"STATIC", L"", WS_CHILD,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);
    SetWindowTheme(hTasksPanel_, L"", L"");

    HWND hT = CreateWindowExW(0, L"STATIC", L"Task History Log",
        WS_CHILD | WS_VISIBLE, 30, 25, rc.right - 60, 28, hTasksPanel_, NULL, hInst_, NULL);
    sf(hT, hFontTitle_);
    SetWindowTheme(hT, L"", L"");

    hTaskList_ = CreateWindowExW(WS_EX_CLIENTEDGE, WC_LISTVIEWW, L"",
        WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | LVS_NOSORTHEADER,
        30, 70, rc.right - 60, rc.bottom - 100, hTasksPanel_, NULL, hInst_, NULL);

    SendMessageW(hTaskList_, LVM_SETBKCOLOR, 0, (LPARAM)CLR_PANEL);
    SendMessageW(hTaskList_, LVM_SETTEXTBKCOLOR, 0, (LPARAM)CLR_PANEL);
    SendMessageW(hTaskList_, LVM_SETTEXTCOLOR, 0, (LPARAM)CLR_TXT);

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

    SetWindowSubclass(hTasksPanel_, SubclassPanelProc, 4, (DWORD_PTR)this);
}

bool AgentGUI::create() {
    INITCOMMONCONTROLSEX ix = {sizeof(ix), ICC_PROGRESS_CLASS | ICC_LISTVIEW_CLASSES};
    InitCommonControlsEx(&ix);
    create_fonts();
    create_window(hInst_);
    if (!hWnd_) return false;

    create_sidebar();
    create_dashboard();
    create_games();
    create_settings();
    create_tasks();

    ShowWindow(hGamesPanel_, SW_HIDE);
    ShowWindow(hSettingsPanel_, SW_HIDE);
    ShowWindow(hTasksPanel_, SW_HIDE);
    return true;
}

void AgentGUI::show() { visible_ = true; ShowWindow(hWnd_, SW_SHOW); UpdateWindow(hWnd_); }
void AgentGUI::hide() { visible_ = false; ShowWindow(hWnd_, SW_HIDE); }

void AgentGUI::switch_page(int idx) {
    ShowWindow(hDashPanel_, idx == 0 ? SW_SHOW : SW_HIDE);
    ShowWindow(hGamesPanel_, idx == 1 ? SW_SHOW : SW_HIDE);
    ShowWindow(hSettingsPanel_, idx == 2 ? SW_SHOW : SW_HIDE);
    ShowWindow(hTasksPanel_, idx == 3 ? SW_SHOW : SW_HIDE);
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

bool file_exists(const std::wstring& path) {
    DWORD dwAttrib = GetFileAttributesW(path.c_str());
    return (dwAttrib != INVALID_FILE_ATTRIBUTES && !(dwAttrib & FILE_ATTRIBUTE_DIRECTORY));
}

std::wstring read_reg_string(HKEY hKeyParent, const std::wstring& subkey, const std::wstring& valueName) {
    HKEY hKey;
    std::wstring result = L"";
    if (RegOpenKeyExW(hKeyParent, subkey.c_str(), 0, KEY_READ | KEY_WOW64_64KEY, &hKey) == ERROR_SUCCESS) {
        wchar_t buf[MAX_PATH];
        DWORD dwType;
        DWORD dwSize = sizeof(buf);
        if (RegQueryValueExW(hKey, valueName.c_str(), NULL, &dwType, (LPBYTE)buf, &dwSize) == ERROR_SUCCESS) {
            if (dwType == REG_SZ || dwType == REG_EXPAND_SZ) {
                result = buf;
            }
        }
        RegCloseKey(hKey);
    }
    if (result.empty() && RegOpenKeyExW(hKeyParent, subkey.c_str(), 0, KEY_READ | KEY_WOW64_32KEY, &hKey) == ERROR_SUCCESS) {
        wchar_t buf[MAX_PATH];
        DWORD dwType;
        DWORD dwSize = sizeof(buf);
        if (RegQueryValueExW(hKey, valueName.c_str(), NULL, &dwType, (LPBYTE)buf, &dwSize) == ERROR_SUCCESS) {
            if (dwType == REG_SZ || dwType == REG_EXPAND_SZ) {
                result = buf;
            }
        }
        RegCloseKey(hKey);
    }
    return result;
}

std::wstring find_uninstall_path(const std::wstring& displayNamePart) {
    std::vector<std::pair<HKEY, std::wstring>> keys = {
        { HKEY_LOCAL_MACHINE, L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall" },
        { HKEY_LOCAL_MACHINE, L"SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall" },
        { HKEY_CURRENT_USER, L"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall" }
    };
    for (const auto& k : keys) {
        HKEY hKeyParent;
        if (RegOpenKeyExW(k.first, k.second.c_str(), 0, KEY_READ | KEY_WOW64_64KEY, &hKeyParent) == ERROR_SUCCESS) {
            DWORD dwSubKeys = 0;
            if (RegQueryInfoKeyW(hKeyParent, NULL, NULL, NULL, &dwSubKeys, NULL, NULL, NULL, NULL, NULL, NULL, NULL) == ERROR_SUCCESS) {
                for (DWORD i = 0; i < dwSubKeys; i++) {
                    wchar_t subkeyName[256];
                    DWORD dwNameLen = 256;
                    if (RegEnumKeyExW(hKeyParent, i, subkeyName, &dwNameLen, NULL, NULL, NULL, NULL) == ERROR_SUCCESS) {
                        HKEY hSubKey;
                        if (RegOpenKeyExW(hKeyParent, subkeyName, 0, KEY_READ | KEY_WOW64_64KEY, &hSubKey) == ERROR_SUCCESS) {
                            wchar_t dispName[256] = {0};
                            DWORD dwType;
                            DWORD dwSize = sizeof(dispName);
                            if (RegQueryValueExW(hSubKey, L"DisplayName", NULL, &dwType, (LPBYTE)dispName, &dwSize) == ERROR_SUCCESS) {
                                std::wstring dn(dispName);
                                if (dn.find(displayNamePart) != std::wstring::npos) {
                                    wchar_t installLoc[512] = {0};
                                    dwSize = sizeof(installLoc);
                                    if (RegQueryValueExW(hSubKey, L"InstallLocation", NULL, &dwType, (LPBYTE)installLoc, &dwSize) == ERROR_SUCCESS && installLoc[0] != 0) {
                                        RegCloseKey(hSubKey);
                                        RegCloseKey(hKeyParent);
                                        return installLoc;
                                    }
                                    wchar_t uninstallStr[512] = {0};
                                    dwSize = sizeof(uninstallStr);
                                    if (RegQueryValueExW(hSubKey, L"UninstallString", NULL, &dwType, (LPBYTE)uninstallStr, &dwSize) == ERROR_SUCCESS && uninstallStr[0] != 0) {
                                        std::wstring us(uninstallStr);
                                        if (us[0] == L'"') {
                                            size_t nextQuote = us.find(L'"', 1);
                                            if (nextQuote != std::wstring::npos) {
                                                us = us.substr(1, nextQuote - 1);
                                            }
                                        }
                                        size_t lastSlash = us.find_last_of(L"\\/");
                                        if (lastSlash != std::wstring::npos) {
                                            us = us.substr(0, lastSlash);
                                        }
                                        RegCloseKey(hSubKey);
                                        RegCloseKey(hKeyParent);
                                        return us;
                                    }
                                }
                            }
                            RegCloseKey(hSubKey);
                        }
                    }
                }
            }
            RegCloseKey(hKeyParent);
        }
    }
    return L"";
}

struct GameInfo {
    std::wstring key;
    std::wstring name;
    std::wstring emoji;
    std::wstring path;
    bool detected;
};

std::vector<GameInfo> detect_games() {
    std::vector<GameInfo> games = {
        { L"majestic_launcher", L"Majestic Launcher", L"\u25C6", L"", false },
        { L"gta5rp_launcher", L"GTA5RP Launcher", L"\u25C6", L"", false },
        { L"gta5", L"Grand Theft Auto V", L"\u25C6", L"", false },
        { L"steam", L"Steam Launcher", L"\u25C6", L"", false },
        { L"epic_games", L"Epic Games Launcher", L"\u25C6", L"", false },
        { L"minecraft", L"Minecraft", L"\u26CF", L"", false },
        { L"roblox", L"Roblox", L"\u25C6", L"", false },
        { L"riot_games", L"Riot Client", L"\u25C6", L"", false },
        { L"ea_desktop", L"EA Desktop", L"\u25C6", L"", false },
        { L"battle_net", L"Battle.net Launcher", L"\u2744", L"", false },
        { L"ubisoft_connect", L"Ubisoft Connect", L"\u25C6", L"", false }
    };

    wchar_t local_appdata[MAX_PATH] = {0};
    GetEnvironmentVariableW(L"LOCALAPPDATA", local_appdata, MAX_PATH);
    std::wstring local_appdata_str(local_appdata);

    wchar_t appdata[MAX_PATH] = {0};
    GetEnvironmentVariableW(L"APPDATA", appdata, MAX_PATH);
    std::wstring appdata_str(appdata);

    wchar_t pf[MAX_PATH] = {0};
    GetEnvironmentVariableW(L"ProgramFiles", pf, MAX_PATH);
    std::wstring pf_str(pf);

    wchar_t pfx86[MAX_PATH] = {0};
    GetEnvironmentVariableW(L"ProgramFiles(x86)", pfx86, MAX_PATH);
    std::wstring pfx86_str(pfx86);

    for (auto& game : games) {
        if (game.key == L"majestic_launcher") {
            std::wstring p1 = local_appdata_str + L"\\MajesticLauncher\\Majestic Launcher.exe";
            std::wstring p2 = local_appdata_str + L"\\MajesticLauncherGLOBAL\\Majestic Launcher.exe";
            if (file_exists(p1)) { game.path = p1; game.detected = true; }
            else if (file_exists(p2)) { game.path = p2; game.detected = true; }
            else {
                std::wstring uPath = find_uninstall_path(L"Majestic Launcher");
                if (uPath.empty()) uPath = find_uninstall_path(L"Majestic");
                if (!uPath.empty()) {
                    std::wstring p = uPath + L"\\Majestic Launcher.exe";
                    if (file_exists(p)) { game.path = p; game.detected = true; }
                }
            }
        }
        else if (game.key == L"gta5rp_launcher") {
            std::wstring p1 = pfx86_str + L"\\GTA5RP\\GTA5RPLauncher.exe";
            std::wstring p2 = pf_str + L"\\GTA5RP\\GTA5RPLauncher.exe";
            std::wstring p3 = local_appdata_str + L"\\Programs\\gta5rp-launcher\\GTA5RP Launcher.exe";
            if (file_exists(p1)) { game.path = p1; game.detected = true; }
            else if (file_exists(p2)) { game.path = p2; game.detected = true; }
            else if (file_exists(p3)) { game.path = p3; game.detected = true; }
            else {
                std::wstring uPath = find_uninstall_path(L"GTA5RP Launcher");
                if (!uPath.empty()) {
                    std::wstring p = uPath + L"\\GTA5RP Launcher.exe";
                    std::wstring p_alt = uPath + L"\\GTA5RPLauncher.exe";
                    if (file_exists(p)) { game.path = p; game.detected = true; }
                    else if (file_exists(p_alt)) { game.path = p_alt; game.detected = true; }
                }
            }
        }
        else if (game.key == L"gta5") {
            std::wstring p1 = L"C:\\Program Files\\Rockstar Games\\Grand Theft Auto V\\PlayGTAV.exe";
            std::wstring p2 = L"C:\\Program Files (x86)\\Rockstar Games\\Grand Theft Auto V\\PlayGTAV.exe";
            if (file_exists(p1)) { game.path = p1; game.detected = true; }
            else if (file_exists(p2)) { game.path = p2; game.detected = true; }
            else {
                std::wstring uPath = find_uninstall_path(L"Grand Theft Auto V");
                if (!uPath.empty()) {
                    std::wstring p = uPath + L"\\PlayGTAV.exe";
                    if (file_exists(p)) { game.path = p; game.detected = true; }
                }
            }
        }
        else if (game.key == L"steam") {
            std::wstring regPath = read_reg_string(HKEY_CURRENT_USER, L"Software\\Valve\\Steam", L"SteamPath");
            if (!regPath.empty()) {
                std::wstring p = regPath + L"\\steam.exe";
                std::replace(p.begin(), p.end(), L'/', L'\\');
                if (file_exists(p)) { game.path = p; game.detected = true; }
            }
            if (!game.detected) {
                std::wstring p1 = pfx86_str + L"\\Steam\\steam.exe";
                std::wstring p2 = pf_str + L"\\Steam\\steam.exe";
                if (file_exists(p1)) { game.path = p1; game.detected = true; }
                else if (file_exists(p2)) { game.path = p2; game.detected = true; }
            }
            if (!game.detected) {
                std::wstring uPath = find_uninstall_path(L"Steam");
                if (!uPath.empty()) {
                    std::wstring p = uPath + L"\\steam.exe";
                    if (file_exists(p)) { game.path = p; game.detected = true; }
                }
            }
        }
        else if (game.key == L"epic_games") {
            std::wstring regPath = read_reg_string(HKEY_LOCAL_MACHINE, L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\EpicGamesLauncher.exe", L"");
            if (!regPath.empty() && file_exists(regPath)) {
                game.path = regPath; game.detected = true;
            }
            if (!game.detected) {
                std::wstring p1 = pfx86_str + L"\\Epic Games\\Launcher\\Portal\\Binaries\\Win64\\EpicGamesLauncher.exe";
                if (file_exists(p1)) { game.path = p1; game.detected = true; }
            }
            if (!game.detected) {
                std::wstring uPath = find_uninstall_path(L"Epic Games Launcher");
                if (!uPath.empty()) {
                    std::wstring p = uPath + L"\\EpicGamesLauncher.exe";
                    if (file_exists(p)) { game.path = p; game.detected = true; }
                }
            }
        }
        else if (game.key == L"minecraft") {
            std::wstring p1 = L"C:\\XboxGames\\Minecraft Launcher\\Content\\Minecraft.exe";
            std::wstring p2 = appdata_str + L"\\.minecraft\\launcher.exe";
            if (file_exists(p1)) { game.path = p1; game.detected = true; }
            else if (file_exists(p2)) { game.path = p2; game.detected = true; }
            else {
                std::wstring uPath = find_uninstall_path(L"Minecraft Launcher");
                if (!uPath.empty()) {
                    std::wstring p = uPath + L"\\Minecraft.exe";
                    if (file_exists(p)) { game.path = p; game.detected = true; }
                }
            }
        }
        else if (game.key == L"roblox") {
            std::wstring rDir = local_appdata_str + L"\\Roblox\\Versions";
            std::wstring search = rDir + L"\\*";
            WIN32_FIND_DATAW fd;
            HANDLE hFind = FindFirstFileW(search.c_str(), &fd);
            if (hFind != INVALID_HANDLE_VALUE) {
                do {
                    if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
                        std::wstring sub = fd.cFileName;
                        if (sub != L"." && sub != L"..") {
                            std::wstring p = rDir + L"\\" + sub + L"\\RobloxPlayerLauncher.exe";
                            if (file_exists(p)) {
                                game.path = p; game.detected = true;
                                break;
                            }
                        }
                    }
                } while (FindNextFileW(hFind, &fd));
                FindClose(hFind);
            }
            if (!game.detected) {
                std::wstring uPath = find_uninstall_path(L"Roblox Player");
                if (!uPath.empty()) {
                    std::wstring p = uPath + L"\\RobloxPlayerLauncher.exe";
                    if (file_exists(p)) { game.path = p; game.detected = true; }
                }
            }
        }
        else if (game.key == L"riot_games") {
            std::wstring p = L"C:\\Riot Games\\Riot Client\\RiotClientServices.exe";
            if (file_exists(p)) { game.path = p; game.detected = true; }
            else {
                std::wstring uPath = find_uninstall_path(L"Riot Client");
                if (!uPath.empty()) {
                    std::wstring p2 = uPath + L"\\RiotClientServices.exe";
                    if (file_exists(p2)) { game.path = p2; game.detected = true; }
                }
            }
        }
        else if (game.key == L"ea_desktop") {
            std::wstring p = L"C:\\Program Files\\Electronic Arts\\EA Desktop\\EA Desktop\\EADesktop.exe";
            if (file_exists(p)) { game.path = p; game.detected = true; }
            else {
                std::wstring uPath = find_uninstall_path(L"EA app");
                if (!uPath.empty()) {
                    std::wstring p2 = uPath + L"\\EADesktop.exe";
                    if (file_exists(p2)) { game.path = p2; game.detected = true; }
                }
            }
        }
        else if (game.key == L"battle_net") {
            std::wstring p1 = pfx86_str + L"\\Battle.net\\Battle.net.exe";
            std::wstring p2 = pf_str + L"\\Battle.net\\Battle.net.exe";
            if (file_exists(p1)) { game.path = p1; game.detected = true; }
            else if (file_exists(p2)) { game.path = p2; game.detected = true; }
            else {
                std::wstring uPath = find_uninstall_path(L"Battle.net");
                if (!uPath.empty()) {
                    std::wstring p3 = uPath + L"\\Battle.net.exe";
                    if (file_exists(p3)) { game.path = p3; game.detected = true; }
                }
            }
        }
        else if (game.key == L"ubisoft_connect") {
            std::wstring p1 = pfx86_str + L"\\Ubisoft\\Ubisoft Game Launcher\\UbisoftConnect.exe";
            if (file_exists(p1)) { game.path = p1; game.detected = true; }
            else {
                std::wstring uPath = find_uninstall_path(L"Ubisoft Connect");
                if (!uPath.empty()) {
                    std::wstring p2 = uPath + L"\\UbisoftConnect.exe";
                    if (file_exists(p2)) { game.path = p2; game.detected = true; }
                }
            }
        }
    }
    return games;
}

void AgentGUI::draw_games_panel(HDC hdc) {
    RECT rc;
    GetClientRect(hGamesPanel_, &rc);
    
    // Fill background with CLR_APP (#0C0B10)
    FillRect(hdc, &rc, hBrushApp_);
    
    // Draw Title: "Detected Games & Launchers"
    HFONT hOldFont = (HFONT)SelectObject(hdc, hFontTitle_);
    SetBkMode(hdc, TRANSPARENT);
    SetTextColor(hdc, CLR_WHT);
    
    RECT titleRc = { 30, 20, rc.right - 30, 48 };
    DrawTextW(hdc, L"Detected Games & Launchers", -1, &titleRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);
    
    // Draw Subtitle
    SelectObject(hdc, hFont_);
    SetTextColor(hdc, CLR_TXT);
    RECT subtitleRc = { 30, 48, rc.right - 30, 68 };
    DrawTextW(hdc, L"These games and launchers are automatically detected on your PC and can be controlled remotely.", -1, &subtitleRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);
    
    // Detect games
    std::vector<GameInfo> games = detect_games();
    
    HPEN hOldPen = (HPEN)SelectObject(hdc, GetStockObject(NULL_PEN));
    HBRUSH hCardBrush = CreateSolidBrush(CLR_PANEL); // #161523
    HBRUSH hOldBrush = (HBRUSH)SelectObject(hdc, hCardBrush);
    
    int yStart = 75;
    int spacing = 36;
    int cardH = 30;
    
    for (size_t i = 0; i < games.size(); i++) {
        int y = yStart + i * spacing;
        RECT cardRc = { 30, y, rc.right - 30, y + cardH };
        
        SelectObject(hdc, hCardBrush);
        RoundRect(hdc, cardRc.left, cardRc.top, cardRc.right, cardRc.bottom, 12, 12);
        
        // Draw emoji + name
        SetTextColor(hdc, CLR_WHT);
        SelectObject(hdc, hFontCardTitle_);
        std::wstring nameText = games[i].emoji + L"  " + games[i].name;
        RECT nameRc = { cardRc.left + 12, cardRc.top, cardRc.left + 220, cardRc.bottom };
        DrawTextW(hdc, nameText.c_str(), -1, &nameRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);
        
        if (games[i].detected) {
            SetTextColor(hdc, CLR_TXT);
            SelectObject(hdc, hFont_);
            std::wstring displayPath = games[i].path;
            if (displayPath.length() > 28) {
                displayPath = L"..." + displayPath.substr(displayPath.length() - 25);
            }
            RECT pathRc = { cardRc.left + 200, cardRc.top, cardRc.right - 95, cardRc.bottom };
            DrawTextW(hdc, displayPath.c_str(), -1, &pathRc, DT_RIGHT | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);
            
            HBRUSH hBadgeBg = CreateSolidBrush(RGB(6, 78, 59));
            SelectObject(hdc, hBadgeBg);
            RECT badgeRc = { cardRc.right - 85, cardRc.top + 4, cardRc.right - 10, cardRc.bottom - 4 };
            RoundRect(hdc, badgeRc.left, badgeRc.top, badgeRc.right, badgeRc.bottom, 8, 8);
            DeleteObject(hBadgeBg);
            
            SetTextColor(hdc, RGB(52, 211, 153));
            SelectObject(hdc, hFontWindowTitle_);
            DrawTextW(hdc, L"Detected", -1, &badgeRc, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
        } else {
            HBRUSH hBadgeBg = CreateSolidBrush(RGB(31, 41, 55));
            SelectObject(hdc, hBadgeBg);
            RECT badgeRc = { cardRc.right - 85, cardRc.top + 4, cardRc.right - 10, cardRc.bottom - 4 };
            RoundRect(hdc, badgeRc.left, badgeRc.top, badgeRc.right, badgeRc.bottom, 8, 8);
            DeleteObject(hBadgeBg);
            
            SetTextColor(hdc, RGB(156, 163, 175));
            SelectObject(hdc, hFontWindowTitle_);
            DrawTextW(hdc, L"Not Found", -1, &badgeRc, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
        }
    }
    
    SelectObject(hdc, hOldBrush);
    SelectObject(hdc, hOldPen);
    SelectObject(hdc, hOldFont);
    DeleteObject(hCardBrush);
}

LRESULT CALLBACK AgentGUI::SubclassPanelProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam, UINT_PTR uIdSubclass, DWORD_PTR dwRefData) {
    AgentGUI* pGUI = (AgentGUI*)dwRefData;
    if (msg == WM_PAINT && (uIdSubclass == 1 || uIdSubclass == 2)) {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hWnd, &ps);
        RECT rc;
        GetClientRect(hWnd, &rc);
        
        HDC hdcMem = CreateCompatibleDC(hdc);
        HBITMAP hbmMem = CreateCompatibleBitmap(hdc, rc.right, rc.bottom);
        HBITMAP hOldBm = (HBITMAP)SelectObject(hdcMem, hbmMem);
        
        if (uIdSubclass == 1) {
            pGUI->draw_dashboard_panel(hdcMem);
        } else {
            pGUI->draw_games_panel(hdcMem);
        }
        
        BitBlt(hdc, 0, 0, rc.right, rc.bottom, hdcMem, 0, 0, SRCCOPY);
        
        SelectObject(hdcMem, hOldBm);
        DeleteObject(hbmMem);
        DeleteDC(hdcMem);
        
        EndPaint(hWnd, &ps);
        return 0;
    }
    
    if (msg == WM_CTLCOLORSTATIC || msg == WM_CTLCOLOREDIT || msg == WM_CTLCOLORBTN || msg == WM_CTLCOLORLISTBOX ||
        msg == WM_DRAWITEM || msg == WM_COMMAND || msg == WM_NOTIFY) {
        return SendMessageW(pGUI->hWnd_, msg, wParam, lParam);
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
                return HTCLIENT;
            }
            return HTCAPTION;
        }
        return HTCLIENT;
    }

    case WM_DRAWITEM: {
        DRAWITEMSTRUCT* pDIS = (DRAWITEMSTRUCT*)l;
        if (pDIS->CtlType == ODT_BUTTON) {
            HDC hdc = pDIS->hDC;
            RECT rc = pDIS->rcItem;
            HWND hwnd = pDIS->hwndItem;
            
            // Select control's font into DC
            HFONT hFont = (HFONT)SendMessageW(hwnd, WM_GETFONT, 0, 0);
            HFONT hOldFont = (HFONT)SelectObject(hdc, hFont);
            
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
                DrawTextW(hdc, text, -1, &rc, DT_CENTER | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);
                SelectObject(hdc, hOldFont);
                return TRUE;
            }
            
            if (!is_save_btn && self_) {
                int btn_idx = (pDIS->CtlID == IDC_BTN_DASH) ? 0 : 
                              (pDIS->CtlID == 1104) ? 1 : 
                              (pDIS->CtlID == IDC_BTN_SETT) ? 2 : 
                              (pDIS->CtlID == IDC_BTN_TASKS) ? 3 : -1;
                is_active_tab = (btn_idx == self_->current_page_);
            }
            
            bool is_pressed = (pDIS->itemState & ODS_SELECTED);
            HBRUSH hBgBrush = NULL;
            COLORREF textColor = CLR_TXT;
            
            if (is_save_btn) {
                if (is_pressed) {
                    hBgBrush = CreateSolidBrush(RGB(109, 40, 217));
                } else {
                    hBgBrush = CreateSolidBrush(CLR_ACCENT);
                }
                textColor = RGB(255, 255, 255);
            } else {
                if (is_active_tab) {
                    hBgBrush = CreateSolidBrush(CLR_ACCENT);
                    textColor = CLR_WHT;
                } else if (is_pressed) {
                    hBgBrush = CreateSolidBrush(RGB(30, 27, 48));
                    textColor = CLR_WHT;
                } else {
                    hBgBrush = CreateSolidBrush(CLR_SIDE);
                    textColor = CLR_TXT;
                }
            }
            
            FillRect(hdc, &rc, hBgBrush);
            DeleteObject(hBgBrush);
            
            SetBkMode(hdc, TRANSPARENT);
            SetTextColor(hdc, textColor);
            
            RECT textRc = rc;
            if (is_save_btn) {
                DrawTextW(hdc, text, -1, &textRc, DT_CENTER | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);
            } else {
                textRc.left += 20;
                DrawTextW(hdc, text, -1, &textRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE | DT_NOPREFIX);
            }
            
            SelectObject(hdc, hOldFont);
            return TRUE;
        }
        break;
    }

    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hWnd, &ps);
        
        RECT rc;
        GetClientRect(hWnd, &rc);
        
        // Draw title bar background
        RECT titleBarRc = { 0, 0, rc.right, 32 };
        FillRect(hdc, &titleBarRc, self_->hBrushApp_);
        
        // Draw sidebar background
        RECT sidebarRc = { 0, 32, SIDEBAR_W, rc.bottom };
        FillRect(hdc, &sidebarRc, self_->hBrushSide_);
        
        // Draw content area background
        RECT contentRc = { SIDEBAR_W, 32, rc.right, rc.bottom };
        FillRect(hdc, &contentRc, self_->hBrushApp_);
        
        // Draw sidebar logo and headers
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
        
        // Draw window title text
        SetTextColor(hdc, CLR_TXT);
        SelectObject(hdc, self_->hFontWindowTitle_);
        RECT titleTextRc = { 10, 0, 500, 32 };
        DrawTextW(hdc, L"PCManager Agent Dashboard", -1, &titleTextRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
        
        // Draw 1px purple border
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
        return 1;

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
        else if (id == 1104) self_->switch_page(1);
        else if (id == IDC_BTN_SETT) self_->switch_page(2);
        else if (id == IDC_BTN_TASKS) self_->switch_page(3);
        else if (id == 1301) {
            ShowWindow(hWnd, SW_MINIMIZE);
        }
        else if (id == 1302) {
            ShowWindow(hWnd, SW_HIDE);
        }
        else if (id == 1201) {
            wchar_t wbuf[512] = {0};
            GetWindowTextW(self_->hCodeEdit_, wbuf, 511);
            std::wstring wcode(wbuf);
            
            wcode.erase(0, wcode.find_first_not_of(L" \t\r\n"));
            wcode.erase(wcode.find_last_not_of(L" \t\r\n") + 1);

            if (wcode.empty()) {
                SetWindowTextW(self_->hSaveStatusLabel_, L"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043A\u043E\u0434 \u0438\u0437 Telegram");
                break;
            }

            int size_needed = WideCharToMultiByte(CP_UTF8, 0, wcode.c_str(), (int)wcode.size(), NULL, 0, NULL, NULL);
            std::string code(size_needed, 0);
            WideCharToMultiByte(CP_UTF8, 0, wcode.c_str(), (int)wcode.size(), &code[0], size_needed, NULL, NULL);

            std::string code_upper = code;
            std::transform(code_upper.begin(), code_upper.end(), code_upper.begin(), ::toupper);
            if (code_upper.rfind("TG-", 0) == 0) {
                activate_agent_async(code, self_->hSaveBtn_, self_->hSaveStatusLabel_, self_->hCodeEdit_);
            } else {
                if (save_config_key(code)) {
                    SetWindowTextW(self_->hSaveStatusLabel_, L"\u041A\u043E\u0434 \u0441\u043E\u0445\u0440\u0430\u043D\u0451\u043D! \u041F\u0435\u0440\u0435\u0437\u0430\u043F\u0443\u0441\u0442\u0438\u0442\u0435 \u0430\u0433\u0435\u043D\u0442\u0430");
                } else {
                    SetWindowTextW(self_->hSaveStatusLabel_, L"\u041E\u0448\u0438\u0431\u043A\u0430 \u0441\u043E\u0445\u0440\u0430\u043D\u0435\u043D\u0438\u044F");
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
        if (self_->hGamesPanel_) SetWindowPos(self_->hGamesPanel_, NULL, 0, 0, cr.right, cr.bottom, SWP_NOZORDER);
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
