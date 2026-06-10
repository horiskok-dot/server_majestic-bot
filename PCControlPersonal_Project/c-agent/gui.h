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

private:
    HINSTANCE hInst_;
    HWND hWnd_;
    HWND hContent_;
    HWND hStatusLabelBottom_;
    bool visible_;
    std::string agent_id_;

    // Sidebar buttons
    HWND hBtnDash_, hBtnSettings_, hBtnTasks_;
    int current_page_;

    // Dashboard controls
    HWND hDashPanel_;
    HWND hCpuBar_, hRamBar_, hDiskBar_;
    HWND hCpuPct_, hRamPct_, hDiskPct_;
    HWND hBatteryLabel_, hNetLabel_, hUpLabel_, hIdLabel_, hStatusLabel_;

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
    HICON hIcon_;
    HBRUSH hBrushSide_, hBrushPanel_, hBrushProg_;

    void create_fonts();
    void create_window(HINSTANCE hInstance);
    void create_sidebar();
    void create_dashboard();
    void create_settings();
    void create_tasks();
    void switch_page(int idx);
    void update_task_list();
    void update_bottom_bar();
    void draw_gradient(HDC hdc, RECT& r, COLORREF top, COLORREF bot);

    static AgentGUI* self_;
    static const int SIDEBAR_W = 180;
};
