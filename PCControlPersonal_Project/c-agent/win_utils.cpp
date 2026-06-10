#include "win_utils.h"
#include <windows.h>
#include <gdiplus.h>
#include <tlhelp32.h>
#include <psapi.h>
#include <mmdeviceapi.h>
#include <endpointvolume.h>
#include <iostream>
#include <sstream>
#include <vector>
#include <algorithm>
#include <cctype>
#include <iphlpapi.h>

#pragma comment(lib, "gdiplus.lib")
#pragma comment(lib, "psapi.lib")
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "ws2_32.lib")

namespace WinUtils {

// GDI+ global state (initialized once at startup)
static ULONG_PTR g_gdiplusToken = 0;

bool gdiplus_init() {
    Gdiplus::GdiplusStartupInput gdiplusStartupInput;
    Gdiplus::Status st = Gdiplus::GdiplusStartup(&g_gdiplusToken, &gdiplusStartupInput, NULL);
    return st == Gdiplus::Ok;
}

void gdiplus_shutdown() {
    if (g_gdiplusToken != 0) {
        Gdiplus::GdiplusShutdown(g_gdiplusToken);
        g_gdiplusToken = 0;
    }
}

static std::string to_string(const std::wstring& wstr) {
    if (wstr.empty()) return "";
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), NULL, 0, NULL, NULL);
    if (size_needed <= 0) return "";
    std::string strTo(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), &strTo[0], size_needed, NULL, NULL);
    return strTo;
}

// Helper to get CLSID of image encoder in GDI+
static int GetEncoderClsid(const WCHAR* format, CLSID* pClsid) {
    UINT num = 0;
    UINT size = 0;
    Gdiplus::GetImageEncodersSize(&num, &size);
    if (size == 0) return -1;
    Gdiplus::ImageCodecInfo* pImageCodecInfo = (Gdiplus::ImageCodecInfo*)(malloc(size));
    if (pImageCodecInfo == NULL) return -1;
    Gdiplus::GetImageEncoders(num, size, pImageCodecInfo);
    for (UINT j = 0; j < num; ++j) {
        if (wcscmp(pImageCodecInfo[j].MimeType, format) == 0) {
            *pClsid = pImageCodecInfo[j].Clsid;
            free(pImageCodecInfo);
            return j;
        }
    }
    free(pImageCodecInfo);
    return -1;
}

bool take_screenshot(const std::wstring& save_path, int quality) {
    if (g_gdiplusToken == 0) return false; // GDI+ not initialized

    int x = GetSystemMetrics(SM_XVIRTUALSCREEN);
    int y = GetSystemMetrics(SM_YVIRTUALSCREEN);
    int w = GetSystemMetrics(SM_CXVIRTUALSCREEN);
    int h = GetSystemMetrics(SM_CYVIRTUALSCREEN);

    if (w <= 0 || h <= 0) return false;

    HDC hScreenDC = GetDC(NULL);
    if (!hScreenDC) return false;
    HDC hMemoryDC = CreateCompatibleDC(hScreenDC);
    HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, w, h);
    HBITMAP hOldBitmap = (HBITMAP)SelectObject(hMemoryDC, hBitmap);

    BitBlt(hMemoryDC, 0, 0, w, h, hScreenDC, x, y, SRCCOPY | CAPTUREBLT);

    bool success = false;
    {
        Gdiplus::Bitmap bitmap(hBitmap, NULL);
        CLSID clsid;
        if (GetEncoderClsid(L"image/jpeg", &clsid) != -1) {
            Gdiplus::EncoderParameters encoderParameters;
            encoderParameters.Count = 1;
            encoderParameters.Parameter[0].Guid = Gdiplus::EncoderQuality;
            encoderParameters.Parameter[0].Type = Gdiplus::EncoderParameterValueTypeLong;
            encoderParameters.Parameter[0].NumberOfValues = 1;
            ULONG qualVal = (ULONG)quality;
            encoderParameters.Parameter[0].Value = &qualVal;

            Gdiplus::Status status = bitmap.Save(save_path.c_str(), &clsid, &encoderParameters);
            success = (status == Gdiplus::Ok);
        }
    } // Bitmap destructor called before GDI cleanup

    SelectObject(hMemoryDC, hOldBitmap);
    DeleteObject(hBitmap);
    DeleteDC(hMemoryDC);
    ReleaseDC(NULL, hScreenDC);
    return success;
}

json get_system_info() {
    json info;

    // Hostname
    char hostname[256] = { 0 };
    DWORD hostSize = sizeof(hostname);
    GetComputerNameA(hostname, &hostSize);
    info["hostname"] = hostname;

    // Username
    char username[256] = { 0 };
    DWORD userSize = sizeof(username);
    GetUserNameA(username, &userSize);
    info["username"] = username;

    // Platform
    info["platform"] = "Windows";
    info["os"] = "Windows 10/11";

    // Memory status
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    if (GlobalMemoryStatusEx(&memInfo)) {
        info["ram_total"] = memInfo.ullTotalPhys;
        info["ram_used"] = memInfo.ullTotalPhys - memInfo.ullAvailPhys;
        info["ram_percent"] = memInfo.dwMemoryLoad;
    } else {
        info["ram_total"] = 0;
        info["ram_used"] = 0;
        info["ram_percent"] = 0;
    }

    // Uptime
    ULONGLONG uptime_ms = GetTickCount64();
    info["uptime_seconds"] = uptime_ms / 1000;

    // Calculate real CPU usage percentage
    static FILETIME s_prev_idle_time = { 0 };
    static FILETIME s_prev_kernel_time = { 0 };
    static FILETIME s_prev_user_time = { 0 };

    FILETIME idle_time, kernel_time, user_time;
    double cpu_val = 5.0; // fallback
    if (GetSystemTimes(&idle_time, &kernel_time, &user_time)) {
        ULONGLONG idle = ((ULONGLONG)idle_time.dwHighDateTime << 32) | idle_time.dwLowDateTime;
        ULONGLONG kernel = ((ULONGLONG)kernel_time.dwHighDateTime << 32) | kernel_time.dwLowDateTime;
        ULONGLONG user = ((ULONGLONG)user_time.dwHighDateTime << 32) | user_time.dwLowDateTime;

        ULONGLONG prev_idle = ((ULONGLONG)s_prev_idle_time.dwHighDateTime << 32) | s_prev_idle_time.dwLowDateTime;
        ULONGLONG prev_kernel = ((ULONGLONG)s_prev_kernel_time.dwHighDateTime << 32) | s_prev_kernel_time.dwLowDateTime;
        ULONGLONG prev_user = ((ULONGLONG)s_prev_user_time.dwHighDateTime << 32) | s_prev_user_time.dwLowDateTime;

        ULONGLONG idle_diff = idle - prev_idle;
        ULONGLONG kernel_diff = kernel - prev_kernel;
        ULONGLONG user_diff = user - prev_user;

        ULONGLONG total_diff = kernel_diff + user_diff;

        s_prev_idle_time = idle_time;
        s_prev_kernel_time = kernel_time;
        s_prev_user_time = user_time;

        if (total_diff > 0) {
            if (total_diff >= idle_diff) {
                cpu_val = (double)(total_diff - idle_diff) / total_diff * 100.0;
            } else {
                cpu_val = 0.0;
            }
        } else {
            cpu_val = 0.0;
        }
    }
    info["cpu_percent"] = cpu_val;

    return info;
}

json get_disk_info() {
    json info = json::array();
    char drives[256] = { 0 };
    DWORD size = GetLogicalDriveStringsA(sizeof(drives), drives);
    if (size == 0) return info;

    char* drive = drives;
    while (*drive) {
        ULARGE_INTEGER freeBytes, totalBytes, totalFreeBytes;
        if (GetDiskFreeSpaceExA(drive, &freeBytes, &totalBytes, &totalFreeBytes)) {
            json d;
            d["device"] = drive;
            d["mountpoint"] = drive;
            d["total"] = totalBytes.QuadPart;
            d["free"] = totalFreeBytes.QuadPart;
            d["used"] = totalBytes.QuadPart - totalFreeBytes.QuadPart;
            double pct = (double)(totalBytes.QuadPart - totalFreeBytes.QuadPart) / totalBytes.QuadPart * 100.0;
            d["percent"] = (int)pct;
            info.push_back(d);
        }
        drive += strlen(drive) + 1;
    }

    json result;
    result["drives"] = info;
    return result;
}

struct ProcessItem {
    DWORD pid;
    std::string name;
    double memory_mb;
};

json get_process_list() {
    json info = json::array();
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE) return info;

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);

    std::vector<ProcessItem> procs;

    if (Process32First(hSnapshot, &pe32)) {
        do {
            double mem_mb = 0.0;
            HANDLE hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pe32.th32ProcessID);
            if (hProcess) {
                PROCESS_MEMORY_COUNTERS pmc = { 0 };
                pmc.cb = sizeof(PROCESS_MEMORY_COUNTERS);
                if (GetProcessMemoryInfo(hProcess, &pmc, sizeof(pmc))) {
                    mem_mb = (double)pmc.WorkingSetSize / (1024.0 * 1024.0);
                }
                CloseHandle(hProcess);
            }
            std::string proc_name = to_string(pe32.szExeFile);
            procs.push_back({ pe32.th32ProcessID, proc_name, mem_mb });
        } while (Process32Next(hSnapshot, &pe32));
    }
    CloseHandle(hSnapshot);

    // Sort by memory descending
    std::sort(procs.begin(), procs.end(), [](const ProcessItem& a, const ProcessItem& b) {
        return a.memory_mb > b.memory_mb;
    });

    for (const auto& p : procs) {
        json item;
        item["pid"] = p.pid;
        item["name"] = p.name;
        item["memory_mb"] = p.memory_mb;
        info.push_back(item);
    }

    json result;
    result["items"] = info;
    return result;
}

bool kill_process(DWORD pid) {
    HANDLE hProcess = OpenProcess(PROCESS_TERMINATE, FALSE, pid);
    if (!hProcess) return false;
    BOOL res = TerminateProcess(hProcess, 0);
    CloseHandle(hProcess);
    return res != 0;
}

bool adjust_volume(bool increase) {
    CoInitialize(NULL);
    IMMDeviceEnumerator *deviceEnumerator = NULL;
    HRESULT hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), NULL, CLSCTX_INPROC_SERVER, __uuidof(IMMDeviceEnumerator), (LPVOID *)&deviceEnumerator);
    if (FAILED(hr)) return false;

    IMMDevice *defaultDevice = NULL;
    hr = deviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &defaultDevice);
    if (FAILED(hr)) {
        deviceEnumerator->Release();
        return false;
    }

    IAudioEndpointVolume *endpointVolume = NULL;
    hr = defaultDevice->Activate(__uuidof(IAudioEndpointVolume), CLSCTX_INPROC_SERVER, NULL, (LPVOID *)&endpointVolume);
    if (FAILED(hr)) {
        defaultDevice->Release();
        deviceEnumerator->Release();
        return false;
    }

    float currentVolume = 0;
    endpointVolume->GetMasterVolumeLevelScalar(&currentVolume);
    if (increase) {
        currentVolume = min(1.0f, currentVolume + 0.1f);
    } else {
        currentVolume = max(0.0f, currentVolume - 0.1f);
    }
    endpointVolume->SetMasterVolumeLevelScalar(currentVolume, NULL);

    endpointVolume->Release();
    defaultDevice->Release();
    deviceEnumerator->Release();
    CoUninitialize();
    return true;
}

static WORD GetVirtualKey(const std::string& key) {
    std::string k = key;
    std::transform(k.begin(), k.end(), k.begin(), ::tolower);
    if (k == "space") return VK_SPACE;
    if (k == "enter") return VK_RETURN;
    if (k == "esc" || k == "escape") return VK_ESCAPE;
    if (k == "shift") return VK_SHIFT;
    if (k == "ctrl") return VK_CONTROL;
    if (k == "tab") return VK_TAB;
    if (k == "up") return VK_UP;
    if (k == "down") return VK_DOWN;
    if (k == "left") return VK_LEFT;
    if (k == "right") return VK_RIGHT;
    if (k.length() == 1) {
        SHORT vk = VkKeyScanA(k[0]);
        if (vk != -1) return vk & 0xFF;
    }
    return 0;
}

bool press_key(const std::string& key, int duration_ms) {
    WORD vk = GetVirtualKey(key);
    if (vk == 0) return false;

    // Map virtual key to scan code for DirectX compatibility (e.g. GTA 5 RP)
    WORD scan = (WORD)MapVirtualKeyA(vk, MAPVK_VK_TO_VSC);

    INPUT input = { 0 };
    input.type = INPUT_KEYBOARD;
    input.ki.wVk = vk;
    input.ki.wScan = scan;
    input.ki.dwFlags = 0;
    if (vk == VK_LEFT || vk == VK_RIGHT || vk == VK_UP || vk == VK_DOWN ||
        vk == VK_INSERT || vk == VK_DELETE || vk == VK_HOME || vk == VK_END ||
        vk == VK_PRIOR || vk == VK_NEXT) {
        input.ki.dwFlags |= KEYEVENTF_EXTENDEDKEY;
    }
    SendInput(1, &input, sizeof(INPUT));

    Sleep(duration_ms);

    input.ki.dwFlags |= KEYEVENTF_KEYUP;
    SendInput(1, &input, sizeof(INPUT));
    return true;
}

bool click_at(int x, int y) {
    SetCursorPos(x, y);
    Sleep(50);
    INPUT input = { 0 };
    input.type = INPUT_MOUSE;
    input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
    SendInput(1, &input, sizeof(INPUT));
    Sleep(80);
    input.mi.dwFlags = MOUSEEVENTF_LEFTUP;
    SendInput(1, &input, sizeof(INPUT));
    return true;
}

bool double_click_at(int x, int y) {
    click_at(x, y);
    Sleep(80);
    click_at(x, y);
    return true;
}

bool move_mouse(int dx, int dy) {
    POINT p;
    if (GetCursorPos(&p)) {
        SetCursorPos(p.x + dx, p.y + dy);
        return true;
    }
    return false;
}

// Run a command silently without showing a window
static bool run_hidden_cmd(const std::string& cmd) {
    std::string full_cmd = "cmd.exe /c " + cmd;
    STARTUPINFOA si = { 0 };
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    PROCESS_INFORMATION pi = { 0 };
    BOOL ok = CreateProcessA(
        NULL, (LPSTR)full_cmd.c_str(),
        NULL, NULL, FALSE,
        CREATE_NO_WINDOW,
        NULL, NULL, &si, &pi
    );
    if (ok) {
        WaitForSingleObject(pi.hProcess, 5000);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    }
    return ok != 0;
}

bool trigger_shutdown(int minutes) {
    std::stringstream cmd;
    cmd << "shutdown /s /t " << (minutes * 60);
    return run_hidden_cmd(cmd.str());
}

bool trigger_restart(int seconds) {
    std::stringstream cmd;
    cmd << "shutdown /r /t " << seconds;
    return run_hidden_cmd(cmd.str());
}

bool cancel_shutdown() {
    return run_hidden_cmd("shutdown /a");
}

void anti_afk_tick() {
    // Slighly shake the cursor
    POINT p;
    if (GetCursorPos(&p)) {
        SetCursorPos(p.x + 2, p.y);
        Sleep(50);
        SetCursorPos(p.x - 2, p.y);
    }
}

bool is_steam_running() {
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE) return false;

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);
    bool running = false;

    if (Process32First(hSnapshot, &pe32)) {
        do {
            std::string name = to_string(pe32.szExeFile);
            std::transform(name.begin(), name.end(), name.begin(), ::tolower);
            if (name == "steam.exe") {
                running = true;
                break;
            }
        } while (Process32Next(hSnapshot, &pe32));
    }
    CloseHandle(hSnapshot);
    return running;
}

bool get_battery_percent(int& percent, bool& charging) {
    SYSTEM_POWER_STATUS sps;
    if (!GetSystemPowerStatus(&sps)) return false;
    if (sps.BatteryLifePercent > 100) return false;
    percent = sps.BatteryLifePercent;
    charging = (sps.ACLineStatus == 1);
    return true;
}

json get_battery_info() {
    json info;
    SYSTEM_POWER_STATUS sps;
    if (GetSystemPowerStatus(&sps)) {
        if (sps.BatteryLifePercent <= 100) {
            info["percent"] = (int)sps.BatteryLifePercent;
        }
        info["ac_status"] = (sps.ACLineStatus == 1) ? "plugged" : (sps.ACLineStatus == 0) ? "unplugged" : "unknown";
        info["charging"] = (sps.ACLineStatus == 1);
        info["status"] = (sps.BatteryFlag == 1) ? "high" : 
                         (sps.BatteryFlag == 2) ? "low" : 
                         (sps.BatteryFlag == 4) ? "critical" : 
                         (sps.BatteryFlag == 8) ? "charging" : 
                         (sps.BatteryFlag == 128) ? "no_battery" : "unknown";
    } else {
        info["status"] = "no_battery";
    }
    return info;
}

json get_network_info() {
    json info;
    info["hostname"] = "";
    info["ip_address"] = "";
    info["gateway"] = "";
    info["mac_address"] = "";

    char hostname[256] = { 0 };
    DWORD hostSize = sizeof(hostname);
    if (GetComputerNameA(hostname, &hostSize)) {
        info["hostname"] = std::string(hostname);
    }

    // Get IP and MAC via GetAdaptersInfo
    IP_ADAPTER_INFO adapter_info[16];
    DWORD dwBufLen = sizeof(adapter_info);
    if (GetAdaptersInfo(adapter_info, &dwBufLen) == NO_ERROR) {
        PIP_ADAPTER_INFO pAdapter = adapter_info;
        while (pAdapter) {
            if (pAdapter->Type == MIB_IF_TYPE_ETHERNET || pAdapter->Type == 71) {
                std::string ip = pAdapter->IpAddressList.IpAddress.String;
                if (!ip.empty() && ip != "0.0.0.0") {
                    info["ip_address"] = ip;
                    info["gateway"] = std::string(pAdapter->GatewayList.IpAddress.String);
                    // Format MAC
                    char mac[18];
                    snprintf(mac, sizeof(mac), "%02X:%02X:%02X:%02X:%02X:%02X",
                        pAdapter->Address[0], pAdapter->Address[1],
                        pAdapter->Address[2], pAdapter->Address[3],
                        pAdapter->Address[4], pAdapter->Address[5]);
                    info["mac_address"] = std::string(mac);
                    break;
                }
            }
            pAdapter = pAdapter->Next;
        }
    }

    return info;
}

std::string get_system_uptime_str() {
    DWORD ticks = GetTickCount();
    DWORD secs = ticks / 1000;
    DWORD mins = secs / 60;
    DWORD hours = mins / 60;
    DWORD days = hours / 24;
    
    char buf[64];
    if (days > 0) {
        snprintf(buf, sizeof(buf), "%dd %dh %dm", days, hours % 24, mins % 60);
    } else {
        snprintf(buf, sizeof(buf), "%dh %dm", hours, mins % 60);
    }
    return std::string(buf);
}

}
