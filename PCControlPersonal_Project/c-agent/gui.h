#pragma once
#include <windows.h>
#include <commctrl.h>
#include <string>
#include <vector>

#pragma comment(lib, "comctl32.lib")

struct TaskEntry {
    std::string time;
    std::string task_id;
    std::string action;
    std::string status;
};

class AgentGUI {
public:
    AgentGUI(HINSTANCE hInstance, const std::string& agent_id);
    ~AgentGUI();

    bool create();
    void show();
    void hide();
    bool is_visible() const { return visible_; }

    void update_stats(const std::string& cpu, const std::string& ram,
                      const std::string& disk, const std::string& battery,
                      const std::string& network, const std::string& uptime);
    void update_status(const std::string& status, const std::string& last_seen);
    void add_task(const TaskEntry& entry);

    HWND get_handle() const { return hWnd_; }

    static LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam);
    static LRESULT CALLBACK SubclassPanelProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam, UINT_PTR uIdSubclass, DWORD_PTR dwRefData);

private:
    HINSTANCE hInst_;
    HWND hWnd_;
    HWND hContent_;
    HWND hStatusLabelBottom_;
    bool visible_;
    std::string agent_id_;

    // Title bar buttons
    HWND hBtnMin_, hBtnClose_;

    // Sidebar buttons
    HWND hBtnDash_, hBtnGames_, hBtnSettings_, hBtnTasks_;
    int current_page_;

    // Dashboard controls
    HWND hDashPanel_;
    HWND hGamesPanel_;

    // Dashboard dynamic state values for custom GDI painting
    std::wstring cpu_val_;
    std::wstring ram_val_;
    std::wstring disk_val_;
    int cpu_pct_;
    int ram_pct_;
    int disk_pct_;
    std::wstring battery_;
    std::wstring network_;
    std::wstring uptime_;
    std::wstring status_text_;
    bool is_online_;

    // Settings controls
    HWND hSettingsPanel_;
    HWND hCodeEdit_;
    HWND hSaveBtn_;
    HWND hSaveStatusLabel_;

    // Tasks list
    HWND hTasksPanel_;
    HWND hTaskList_;
    std::vector<TaskEntry> tasks_;

    HFONT hFont_, hFontTitle_, hFontBig_;
    HFONT hFontWindowTitle_, hFontSidebarHeader_, hFontSidebarBtn_, hFontCardTitle_, hFontCardValue_;
    HICON hIcon_;
    HBRUSH hBrushSide_, hBrushPanel_, hBrushProg_, hBrushApp_;

    void create_fonts();
    void create_window(HINSTANCE hInstance);
    void create_sidebar();
    void create_dashboard();
    void create_games();
    void create_settings();
    void create_tasks();
    void switch_page(int idx);
    void update_task_list();
    void update_bottom_bar();
    void draw_dashboard_panel(HDC hdc);
    void draw_games_panel(HDC hdc);

    static AgentGUI* self_;
    static const int SIDEBAR_W = 200; // Sidebar is 200px wide matching Python agent
};

