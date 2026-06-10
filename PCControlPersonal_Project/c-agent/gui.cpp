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

static const COLORREF CLR_TOP    = RGB(0x1E, 0x06, 0x3A);
static const COLORREF CLR_BOT    = RGB(0x06, 0x0C, 0x3C);
static const COLORREF CLR_SIDE   = RGB(0x05, 0x01, 0x10);
static const COLORREF CLR_ACCENT = RGB(0x8B, 0x5C, 0xF6);
static const COLORREF CLR_PANEL  = RGB(0x12, 0x08, 0x28);
static const COLORREF CLR_TXT    = RGB(0xB0, 0xB0, 0xCC);
static const COLORREF CLR_WHT    = RGB(0xE0, 0xD8, 0xF0);
static const COLORREF CLR_PROG   = RGB(0x10, 0x06, 0x24);

#define IDC_BTN_DASH   1101
#define IDC_BTN_SETT   1102
#define IDC_BTN_TASKS  1103
#define IDC_BOTTOM_BAR 1200

static void sf(HWND h, HFONT f) { SendMessage(h, WM_SETFONT, (WPARAM)f, TRUE); }
static HFONT mf(int h, int w, const char* n) {
    LOGFONTA l = {}; l.lfHeight = h; l.lfWeight = w; strcpy_s(l.lfFaceName, n);
    return CreateFontIndirectA(&l);
}

AgentGUI::AgentGUI(HINSTANCE hInst, const std::string& aid)
    : hInst_(hInst), hWnd_(nullptr), hContent_(nullptr),
      hStatusLabelBottom_(nullptr), visible_(false), agent_id_(aid), current_page_(0),
      hBtnDash_(nullptr), hBtnSettings_(nullptr), hBtnTasks_(nullptr),
      hDashPanel_(nullptr), hSettingsPanel_(nullptr), hTasksPanel_(nullptr),
      hCpuBar_(nullptr), hRamBar_(nullptr), hDiskBar_(nullptr),
      hCpuPct_(nullptr), hRamPct_(nullptr), hDiskPct_(nullptr),
      hBatteryLabel_(nullptr), hNetLabel_(nullptr), hUpLabel_(nullptr),
      hIdLabel_(nullptr), hStatusLabel_(nullptr), hTaskList_(nullptr),
      hFont_(nullptr), hFontTitle_(nullptr), hFontBig_(nullptr), hIcon_(nullptr),
      hBrushSide_(CreateSolidBrush(CLR_SIDE)),
      hBrushPanel_(CreateSolidBrush(CLR_PANEL)),
      hBrushProg_(CreateSolidBrush(CLR_PROG)) {
    self_ = this;
}

AgentGUI::~AgentGUI() {
    if (hFont_) DeleteObject(hFont_);
    if (hFontTitle_) DeleteObject(hFontTitle_);
    if (hFontBig_) DeleteObject(hFontBig_);
    if (hBrushSide_) DeleteObject(hBrushSide_);
    if (hBrushPanel_) DeleteObject(hBrushPanel_);
    if (hBrushProg_) DeleteObject(hBrushProg_);
    self_ = nullptr;
}

void AgentGUI::create_fonts() {
    hFont_ = mf(-13, FW_NORMAL, "Segoe UI");
    hFontTitle_ = mf(-15, FW_SEMIBOLD, "Segoe UI");
    hFontBig_ = mf(-22, FW_BOLD, "Segoe UI");
}

void AgentGUI::draw_gradient(HDC hdc, RECT& r, COLORREF top, COLORREF bot) {
    GRADIENT_RECT gr = {0, 1};
    TRIVERTEX tv[2] = {
        {r.left, r.top,      (COLOR16)(GetRValue(top) * 256), (COLOR16)(GetGValue(top) * 256), (COLOR16)(GetBValue(top) * 256), 0},
        {r.right, r.bottom,  (COLOR16)(GetRValue(bot) * 256), (COLOR16)(GetGValue(bot) * 256), (COLOR16)(GetBValue(bot) * 256), 0}
    };
    GradientFill(hdc, tv, 2, &gr, 1, GRADIENT_FILL_RECT_V);
}

void AgentGUI::create_window(HINSTANCE hInstance) {
    WNDCLASSEXA wc = {};
    wc.cbSize = sizeof(wc);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = NULL;
    wc.lpszClassName = "PCManagerAgentMainClass";
    RegisterClassExA(&wc);

    hIcon_ = (HICON)LoadImageA(hInstance, MAKEINTRESOURCEA(100), IMAGE_ICON, 32, 32, LR_DEFAULTCOLOR);
    if (!hIcon_) hIcon_ = LoadIcon(NULL, IDI_APPLICATION);

    RECT r = {0, 0, 820, 560};
    AdjustWindowRect(&r, WS_OVERLAPPEDWINDOW & ~WS_MAXIMIZEBOX & ~WS_THICKFRAME, FALSE);
    hWnd_ = CreateWindowExA(0, "PCManagerAgentMainClass", "PC Control Agent",
        WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, r.right - r.left, r.bottom - r.top,
        NULL, NULL, hInstance, NULL);
    if (hWnd_) {
        SendMessage(hWnd_, WM_SETICON, ICON_BIG, (LPARAM)hIcon_);
        SendMessage(hWnd_, WM_SETICON, ICON_SMALL, (LPARAM)hIcon_);

        // Apply modern Immersive Dark Mode to title bar (Windows 10/11)
        BOOL useDarkMode = TRUE;
        HMODULE hDwmapi = LoadLibraryA("dwmapi.dll");
        if (hDwmapi) {
            typedef HRESULT(WINAPI* fnDwmSetWindowAttribute)(HWND, DWORD, LPCVOID, DWORD);
            fnDwmSetWindowAttribute pDwmSetWindowAttribute = (fnDwmSetWindowAttribute)GetProcAddress(hDwmapi, "DwmSetWindowAttribute");
            if (pDwmSetWindowAttribute) {
                pDwmSetWindowAttribute(hWnd_, 20, &useDarkMode, sizeof(useDarkMode)); // DWMWA_USE_IMMERSIVE_DARK_MODE (W11/W10 20H1+)
                pDwmSetWindowAttribute(hWnd_, 19, &useDarkMode, sizeof(useDarkMode)); // Fallback
            }
            FreeLibrary(hDwmapi);
        }
    }
}

void AgentGUI::create_sidebar() {
    int y = 14;
    HWND hTitle = CreateWindowExA(0, "STATIC", "PC",
        WS_CHILD | WS_VISIBLE | SS_CENTER, 0, y, SIDEBAR_W, 30, hWnd_, NULL, hInst_, NULL);
    sf(hTitle, hFontBig_);
    y += 30;
    HWND hSub = CreateWindowExA(0, "STATIC", "Control Agent",
        WS_CHILD | WS_VISIBLE | SS_CENTER, 0, y, SIDEBAR_W, 16, hWnd_, NULL, hInst_, NULL);
    sf(hSub, hFont_);
    y += 20;

    // accent line
    CreateWindowExA(0, "STATIC", "", WS_CHILD | WS_VISIBLE,
        20, y, SIDEBAR_W - 40, 1, hWnd_, NULL, hInst_, NULL);
    y += 16;

    auto mkbtn = [&](int id, const char* t, int yy) -> HWND {
        HWND h = CreateWindowExA(0, "BUTTON", t,
            WS_CHILD | WS_VISIBLE | BS_OWNERDRAW,
            8, yy, SIDEBAR_W - 8, 36, hWnd_, (HMENU)(INT_PTR)id, hInst_, NULL);
        sf(h, hFont_);
        return h;
    };

    hBtnDash_ = mkbtn(IDC_BTN_DASH, "   \u0414\u0430\u0448\u0431\u043E\u0440\u0434", y);
    y += 40;
    hBtnSettings_ = mkbtn(IDC_BTN_SETT, "   \u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438", y);
    y += 40;
    hBtnTasks_ = mkbtn(IDC_BTN_TASKS, "   \u0417\u0430\u0434\u0430\u0447\u0438", y);

    RECT rc;
    GetClientRect(hWnd_, &rc);
    hContent_ = CreateWindowExA(0, "STATIC", "", WS_CHILD | WS_VISIBLE | SS_OWNERDRAW,
        SIDEBAR_W + 1, 0, rc.right - SIDEBAR_W - 2, rc.bottom - 28, hWnd_, NULL, hInst_, NULL);

    hStatusLabelBottom_ = CreateWindowExA(0, "STATIC", "", WS_CHILD | WS_VISIBLE,
        0, rc.bottom - 28, rc.right, 28, hWnd_, (HMENU)(INT_PTR)IDC_BOTTOM_BAR, hInst_, NULL);
    sf(hStatusLabelBottom_, hFont_);

    InvalidateRect(hWnd_, NULL, TRUE);
}

void AgentGUI::create_dashboard() {
    RECT rc;
    GetClientRect(hContent_, &rc);
    int x = 16, y = 16, w = rc.right - 32;

    hDashPanel_ = CreateWindowExA(0, "STATIC", "", WS_CHILD | WS_VISIBLE,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);

    HWND hT = CreateWindowExA(0, "STATIC",
        "\u0421\u043E\u0441\u0442\u043E\u044F\u043D\u0438\u0435 \u0441\u0438\u0441\u0442\u0435\u043C\u044B",
        WS_CHILD | WS_VISIBLE, x, y, w, 22, hDashPanel_, NULL, hInst_, NULL);
    sf(hT, hFontTitle_);
    y += 36;

    auto add_bar = [&](const char* name, int& yy) -> HWND {
        HWND hn = CreateWindowExA(0, "STATIC", name,
            WS_CHILD | WS_VISIBLE, x, yy, 55, 18, hDashPanel_, NULL, hInst_, NULL);
        sf(hn, hFont_);
        HWND hb = CreateWindowExA(0, PROGRESS_CLASSA, "",
            WS_CHILD | WS_VISIBLE | PBS_SMOOTH,
            x + 60, yy + 1, w - 130, 16, hDashPanel_, NULL, hInst_, NULL);
        SetWindowTheme(hb, L"", L""); // Enable custom colors
        SendMessage(hb, PBM_SETRANGE, 0, MAKELPARAM(0, 100));
        SendMessage(hb, PBM_SETBARCOLOR, 0, (LPARAM)CLR_ACCENT);
        SendMessage(hb, PBM_SETBKCOLOR, 0, (LPARAM)CLR_PROG);
        yy += 28;
        return hb;
    };

    int by = y;
    hCpuBar_ = add_bar("CPU", by); by += 2;
    hRamBar_ = add_bar("RAM", by); by += 2;
    hDiskBar_ = add_bar("Disk C:", by);

    hCpuPct_ = CreateWindowExA(0, "STATIC", "0%",
        WS_CHILD | WS_VISIBLE, x + 60 + w - 130 + 10, y + 1, 45, 16, hDashPanel_, NULL, hInst_, NULL);
    sf(hCpuPct_, hFont_);
    hRamPct_ = CreateWindowExA(0, "STATIC", "0%",
        WS_CHILD | WS_VISIBLE, x + 60 + w - 130 + 10, y + 29, 45, 16, hDashPanel_, NULL, hInst_, NULL);
    sf(hRamPct_, hFont_);
    hDiskPct_ = CreateWindowExA(0, "STATIC", "0%",
        WS_CHILD | WS_VISIBLE, x + 60 + w - 130 + 10, y + 56, 45, 16, hDashPanel_, NULL, hInst_, NULL);
    sf(hDiskPct_, hFont_);

    by += 18;
    auto add_i = [&](const char* t) -> HWND {
        HWND h = CreateWindowExA(0, "STATIC", t,
            WS_CHILD | WS_VISIBLE, x, by, w, 20, hDashPanel_, NULL, hInst_, NULL);
        sf(h, hFont_);
        by += 24;
        return h;
    };

    hBatteryLabel_ = add_i("\u0411\u0430\u0442\u0430\u0440\u0435\u044F: N/A");
    hNetLabel_ = add_i("\u0421\u0435\u0442\u044C: N/A");
    hUpLabel_ = add_i("\u0410\u043F\u0442\u0430\u0439\u043C: N/A");
    hIdLabel_ = add_i(("\u0410\u0433\u0435\u043D\u0442: " + agent_id_).c_str());
    hStatusLabel_ = add_i("\u0421\u0442\u0430\u0442\u0443\u0441: \u0417\u0430\u043F\u0443\u0441\u043A...");
}

void AgentGUI::create_settings() {
    RECT rc;
    GetClientRect(hContent_, &rc);
    int x = 16, y = 16, w = rc.right - 32;

    hSettingsPanel_ = CreateWindowExA(0, "STATIC", "", WS_CHILD,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);

    HWND hT = CreateWindowExA(0, "STATIC",
        "\u041D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438",
        WS_CHILD | WS_VISIBLE, x, y, w, 22, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hT, hFontTitle_);
    y += 36;

    HWND hName = CreateWindowExA(0, "STATIC",
        ("\u0418\u043C\u044F \u0430\u0433\u0435\u043D\u0442\u0430:  PC " + agent_id_).c_str(),
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hName, hFont_);
    y += 28;

    HWND hVer = CreateWindowExA(0, "STATIC",
        "\u0412\u0435\u0440\u0441\u0438\u044F: C++ Agent 1.7.0",
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hVer, hFont_);
    y += 36;

    // Telegram code input
    HWND hCodeLabel = CreateWindowExA(0, "STATIC",
        "\u041A\u043E\u0434 \u043F\u043E\u0434\u043A\u043B\u044E\u0447\u0435\u043D\u0438\u044F \u0438\u0437 TG:",
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hCodeLabel, hFont_);
    y += 24;

    hCodeEdit_ = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "",
        WS_CHILD | WS_VISIBLE | ES_LEFT | ES_AUTOHSCROLL,
        x, y, w, 24, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hCodeEdit_, hFont_);
    SendMessage(hCodeEdit_, EM_SETCUEBANNER, TRUE, (LPARAM)L"");
    y += 32;

    hSaveBtn_ = CreateWindowExA(0, "BUTTON",
        "\u0421\u043E\u0445\u0440\u0430\u043D\u0438\u0442\u044C",
        WS_CHILD | WS_VISIBLE | BS_OWNERDRAW,
        x, y, 120, 30, hSettingsPanel_, (HMENU)(INT_PTR)1201, hInst_, NULL);
    sf(hSaveBtn_, hFont_);
    y += 38;

    hSaveStatusLabel_ = CreateWindowExA(0, "STATIC", "",
        WS_CHILD | WS_VISIBLE, x, y, w, 20, hSettingsPanel_, NULL, hInst_, NULL);
    sf(hSaveStatusLabel_, hFont_);
}

void AgentGUI::create_tasks() {
    RECT rc;
    GetClientRect(hContent_, &rc);

    hTasksPanel_ = CreateWindowExA(0, "STATIC", "", WS_CHILD,
        0, 0, rc.right, rc.bottom, hContent_, NULL, hInst_, NULL);

    HWND hT = CreateWindowExA(0, "STATIC",
        "\u0416\u0443\u0440\u043D\u0430\u043B \u0437\u0430\u0434\u0430\u0447",
        WS_CHILD | WS_VISIBLE, 16, 16, rc.right - 32, 22, hTasksPanel_, NULL, hInst_, NULL);
    sf(hT, hFontTitle_);

    hTaskList_ = CreateWindowExA(WS_EX_CLIENTEDGE, WC_LISTVIEWA, "",
        WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | LVS_NOSORTHEADER,
        12, 48, rc.right - 24, rc.bottom - 58, hTasksPanel_, NULL, hInst_, NULL);

    SendMessage(hTaskList_, LVM_SETBKCOLOR, 0, (LPARAM)CLR_PANEL);
    SendMessage(hTaskList_, LVM_SETTEXTBKCOLOR, 0, (LPARAM)CLR_PANEL);
    SendMessage(hTaskList_, LVM_SETTEXTCOLOR, 0, (LPARAM)CLR_TXT);

    LVCOLUMNA lc = {};
    lc.mask = LVCF_TEXT | LVCF_WIDTH | LVCF_FMT;
    lc.fmt = LVCFMT_LEFT;
    lc.cx = 90;  lc.pszText = (char*)"\u0412\u0440\u0435\u043C\u044F";
    SendMessageA(hTaskList_, LVM_INSERTCOLUMNA, 0, (LPARAM)&lc);
    lc.cx = 170; lc.pszText = (char*)"ID";
    SendMessageA(hTaskList_, LVM_INSERTCOLUMNA, 1, (LPARAM)&lc);
    lc.cx = 130; lc.pszText = (char*)"\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435";
    SendMessageA(hTaskList_, LVM_INSERTCOLUMNA, 2, (LPARAM)&lc);
    lc.cx = 80;  lc.pszText = (char*)"\u0421\u0442\u0430\u0442\u0443\u0441";
    SendMessageA(hTaskList_, LVM_INSERTCOLUMNA, 3, (LPARAM)&lc);
    SendMessageA(hTaskList_, LVM_SETEXTENDEDLISTVIEWSTYLE, 0, (LPARAM)LVS_EX_FULLROWSELECT);
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
    update_bottom_bar();
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
    if (!hStatusLabelBottom_) return;
    SetWindowTextA(hStatusLabelBottom_, ("  " + agent_id_ + "  |  Online").c_str());
}

void AgentGUI::update_stats(const std::string& cpu, const std::string& ram,
                            const std::string& disk, const std::string& battery,
                            const std::string& network, const std::string& uptime) {
    try { SendMessage(hCpuBar_, PBM_SETPOS, std::stoi(cpu), 0); } catch (...) {}
    try { SendMessage(hRamBar_, PBM_SETPOS, std::stoi(ram), 0); } catch (...) {}
    try { SendMessage(hDiskBar_, PBM_SETPOS, std::stoi(disk), 0); } catch (...) {}
    SetWindowTextA(hCpuPct_, (cpu + "%").c_str());
    SetWindowTextA(hRamPct_, (ram + "%").c_str());
    SetWindowTextA(hDiskPct_, (disk + "%").c_str());
    SetWindowTextA(hBatteryLabel_, ("\u0411\u0430\u0442\u0430\u0440\u0435\u044F: " + battery).c_str());
    SetWindowTextA(hNetLabel_, ("\u0421\u0435\u0442\u044C: " + network).c_str());
    SetWindowTextA(hUpLabel_, ("\u0410\u043F\u0442\u0430\u0439\u043C: " + uptime).c_str());
}

void AgentGUI::update_status(const std::string& status, const std::string&) {
    SetWindowTextA(hStatusLabel_, ("\u0421\u0442\u0430\u0442\u0443\u0441: " + status).c_str());
    update_bottom_bar();
}

void AgentGUI::add_task(const TaskEntry& entry) {
    tasks_.push_back(entry);
    if (tasks_.size() > 100) tasks_.erase(tasks_.begin());
    update_task_list();
}

LRESULT CALLBACK AgentGUI::WndProc(HWND hWnd, UINT msg, WPARAM w, LPARAM l) {
    if (!self_) return DefWindowProcA(hWnd, msg, w, l);

    switch (msg) {
    case WM_DRAWITEM: {
        DRAWITEMSTRUCT* pDIS = (DRAWITEMSTRUCT*)l;
        if (pDIS->CtlType == ODT_BUTTON) {
            HDC hdc = pDIS->hDC;
            RECT rc = pDIS->rcItem;
            HWND hwnd = pDIS->hwndItem;
            
            char text[256] = {0};
            GetWindowTextA(hwnd, text, sizeof(text) - 1);
            
            bool is_active_tab = false;
            bool is_save_btn = (pDIS->CtlID == 1201);
            
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
                    hBgBrush = CreateSolidBrush(RGB(0x6D, 0x28, 0xD9)); // Darker purple
                } else {
                    hBgBrush = CreateSolidBrush(CLR_ACCENT); // Accent purple
                }
                textColor = RGB(0xFF, 0xFF, 0xFF);
            } else {
                if (is_active_tab) {
                    hBgBrush = CreateSolidBrush(CLR_PANEL); // Matches active content bg
                    textColor = CLR_WHT;
                } else if (is_pressed) {
                    hBgBrush = CreateSolidBrush(RGB(0x15, 0x0A, 0x30));
                    textColor = CLR_WHT;
                } else {
                    hBgBrush = CreateSolidBrush(CLR_SIDE); // Matches sidebar bg
                    textColor = CLR_TXT;
                }
            }
            
            FillRect(hdc, &rc, hBgBrush);
            DeleteObject(hBgBrush);
            
            if (is_active_tab && !is_save_btn) {
                RECT strip = { rc.left, rc.top + 2, rc.left + 4, rc.bottom - 2 };
                HBRUSH hStripBrush = CreateSolidBrush(CLR_ACCENT);
                FillRect(hdc, &strip, hStripBrush);
                DeleteObject(hStripBrush);
            }
            
            SetBkMode(hdc, TRANSPARENT);
            SetTextColor(hdc, textColor);
            
            RECT textRc = rc;
            if (is_save_btn) {
                DrawTextA(hdc, text, -1, &textRc, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
            } else {
                textRc.left += 20; // Indent sidebar button text
                DrawTextA(hdc, text, -1, &textRc, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
            }
            return TRUE;
        }
        break;
    }
    case WM_ERASEBKGND: {
        HDC hdc = (HDC)w;
        RECT rc;
        GetClientRect(hWnd, &rc);
        // sidebar — solid dark
        RECT sr = {0, 0, SIDEBAR_W, rc.bottom};
        HBRUSH hb = CreateSolidBrush(CLR_SIDE);
        FillRect(hdc, &sr, hb);
        DeleteObject(hb);
        // content — gradient
        RECT gr = {SIDEBAR_W, 0, rc.right, rc.bottom};
        self_->draw_gradient(hdc, gr, CLR_TOP, CLR_BOT);
        return 1;
    }

    case WM_CTLCOLORSTATIC: {
        HDC hdc = (HDC)w;
        HWND hc = (HWND)l;
        SetBkMode(hdc, TRANSPARENT);
        if (hc == self_->hStatusLabelBottom_)
            SetTextColor(hdc, RGB(0x66, 0x66, 0x88));
        else
            SetTextColor(hdc, CLR_TXT);
        LONG style = GetWindowLongA(hc, GWL_STYLE);
        if (style & SS_CENTER)
            SetTextColor(hdc, CLR_ACCENT);
        // check if control is in sidebar area
        RECT cr;
        GetWindowRect(hc, &cr);
        HWND parent = GetParent(hc);
        if (parent == self_->hWnd_) {
            MapWindowPoints(HWND_DESKTOP, self_->hWnd_, (POINT*)&cr, 1);
            if (cr.left < SIDEBAR_W)
                return (LRESULT)self_->hBrushSide_;
        }
        return (LRESULT)self_->hBrushPanel_;
    }

    case WM_CTLCOLORBTN: {
        HDC hdc = (HDC)w;
        HWND hc = (HWND)l;
        if (hc == self_->hBtnDash_ || hc == self_->hBtnSettings_ || hc == self_->hBtnTasks_) {
            int idx = hc == self_->hBtnDash_ ? 0 : hc == self_->hBtnSettings_ ? 1 : 2;
            bool active = (idx == self_->current_page_);
            SetTextColor(hdc, active ? CLR_WHT : CLR_TXT);
            SetBkColor(hdc, active ? CLR_PANEL : CLR_SIDE);
            return (LRESULT)(active ? self_->hBrushPanel_ : self_->hBrushSide_);
        }
        return DefWindowProcA(hWnd, msg, w, l);
    }

    case WM_CTLCOLOREDIT: {
        HDC hdc = (HDC)w;
        SetTextColor(hdc, CLR_WHT);
        SetBkColor(hdc, CLR_PROG);
        return (LRESULT)self_->hBrushProg_;
    }

    case WM_COMMAND: {
        int id = LOWORD(w);
        if (id == IDC_BTN_DASH) self_->switch_page(0);
        else if (id == IDC_BTN_SETT) self_->switch_page(1);
        else if (id == IDC_BTN_TASKS) self_->switch_page(2);
        else if (id == 1201) {
            // Save button clicked
            char buf[512] = {0};
            GetWindowTextA(self_->hCodeEdit_, buf, sizeof(buf) - 1);
            std::string code(buf);
            // Trim whitespace
            code.erase(0, code.find_first_not_of(" \t\r\n"));
            code.erase(code.find_last_not_of(" \t\r\n") + 1);

            if (code.empty()) {
                SetWindowTextW(self_->hSaveStatusLabel_, L"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043A\u043E\u0434 \u0438\u0437 Telegram"); // "Введите код из Telegram"
                break;
            }

            std::string code_upper = code;
            std::transform(code_upper.begin(), code_upper.end(), code_upper.begin(), ::toupper);
            if (code_upper.rfind("TG-", 0) == 0) {
                // Perform activation via API
                activate_agent_async(code, self_->hSaveBtn_, self_->hSaveStatusLabel_, self_->hCodeEdit_);
            } else {
                // Save key directly (legacy mode / manual activation)
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
        int cw = rc.right - SIDEBAR_W - 2;
        int ch = rc.bottom - 28;
        if (self_->hContent_)
            SetWindowPos(self_->hContent_, NULL, SIDEBAR_W + 1, 0, cw, ch, SWP_NOZORDER);
        if (self_->hStatusLabelBottom_)
            SetWindowPos(self_->hStatusLabelBottom_, NULL, 0, rc.bottom - 28, rc.right, 28, SWP_NOZORDER);

        RECT cr;
        if (self_->hContent_) GetClientRect(self_->hContent_, &cr);
        if (self_->hDashPanel_) SetWindowPos(self_->hDashPanel_, NULL, 0, 0, cr.right, cr.bottom, SWP_NOZORDER);
        if (self_->hSettingsPanel_) SetWindowPos(self_->hSettingsPanel_, NULL, 0, 0, cr.right, cr.bottom, SWP_NOZORDER);
        if (self_->hTasksPanel_) SetWindowPos(self_->hTasksPanel_, NULL, 0, 0, cr.right, cr.bottom, SWP_NOZORDER);
        if (self_->hTaskList_)
            SetWindowPos(self_->hTaskList_, NULL, 12, 48, cr.right - 24, cr.bottom - 58, SWP_NOZORDER);
        return 0;
    }

    case WM_CLOSE:
        ShowWindow(hWnd, SW_HIDE);
        return 0;

    case WM_DESTROY:
        PostQuitMessage(0);
        break;

    case WM_NCDESTROY:
        // cleanup brushes we created in WM_CTLCOLORBTN (they leak otherwise)
        break;
    }

    return DefWindowProcA(hWnd, msg, w, l);
}
