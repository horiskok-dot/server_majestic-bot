#pragma once
#include <string>
#include <windows.h>
#include "json.hpp"

using json = nlohmann::json;

namespace WinUtils {
    bool gdiplus_init();
    void gdiplus_shutdown();
    bool take_screenshot(const std::wstring& save_path, int quality = 80);
    json get_system_info();
    json get_disk_info();
    json get_process_list();
    bool kill_process(DWORD pid);
    bool adjust_volume(bool increase);
    bool press_key(const std::string& key, int duration_ms = 100);
    bool click_at(int x, int y);
    bool double_click_at(int x, int y);
    bool move_mouse(int dx, int dy);
    bool trigger_shutdown(int minutes);
    bool trigger_restart(int seconds);
    bool cancel_shutdown();
    void anti_afk_tick();
    bool is_steam_running();
    json get_battery_info();
    json get_network_info();
    std::string get_system_uptime_str();
    bool get_battery_percent(int& percent, bool& charging);
}
