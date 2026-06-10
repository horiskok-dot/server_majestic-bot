#include "websocket_client.h"
#include <vector>
#include <sstream>

WebSocketClient::WebSocketClient()
    : hSession_(nullptr), hConnect_(nullptr), hRequest_(nullptr),
      connected_(false), server_port_(80), is_https_(false) {
}

WebSocketClient::~WebSocketClient() {
    disconnect();
}

std::string WebSocketClient::generate_key() {
    const char* chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    std::string key;
    key.reserve(16);
    for (int i = 0; i < 16; i++) {
        key += chars[rand() % 62];
    }
    return key;
}

void WebSocketClient::parse_url(const std::string& url) {
    std::string temp = url;
    std::string protocol;

    size_t pos = temp.find("://");
    if (pos != std::string::npos) {
        protocol = temp.substr(0, pos);
        temp = temp.substr(pos + 3);
    }

    is_https_ = (protocol == "wss" || protocol == "https");
    server_port_ = is_https_ ? 443 : 80;

    pos = temp.find('/');
    if (pos != std::string::npos) {
        path_ = temp.substr(pos);
        temp = temp.substr(0, pos);
    } else {
        path_ = "/";
    }

    pos = temp.find(':');
    if (pos != std::string::npos) {
        server_host_ = std::wstring(temp.begin(), temp.begin() + pos);
        server_port_ = std::stoi(temp.substr(pos + 1));
    } else {
        server_host_ = std::wstring(temp.begin(), temp.end());
    }
}

bool WebSocketClient::do_ws_upgrade(const std::string& access_key, const std::string& agent_id) {
    std::wstring wmethod = L"GET";
    std::wstring wpath = std::wstring(path_.begin(), path_.end());

    hRequest_ = WinHttpOpenRequest(hConnect_, wmethod.c_str(), wpath.c_str(),
                                   NULL, WINHTTP_NO_REFERER,
                                   WINHTTP_DEFAULT_ACCEPT_TYPES,
                                   is_https_ ? WINHTTP_FLAG_SECURE : 0);
    if (!hRequest_) return false;

    // WebSocket upgrade headers
    std::string ws_key = generate_key();
    std::wstring upgrade_hdr = L"Upgrade: websocket\r\n";
    std::wstring conn_hdr = L"Connection: Upgrade\r\n";
    std::wstring ws_ver = L"Sec-WebSocket-Version: 13\r\n";
    std::wstring ws_key_hdr = L"Sec-WebSocket-Key: " + std::wstring(ws_key.begin(), ws_key.end()) + L"\r\n";
    std::wstring auth_hdr1 = L"X-Server-Access-Key: " + std::wstring(access_key.begin(), access_key.end()) + L"\r\n";
    std::wstring auth_hdr2 = L"X-PCManager-Key: " + std::wstring(access_key.begin(), access_key.end()) + L"\r\n";
    std::wstring agent_hdr = L"X-Agent-Id: " + std::wstring(agent_id.begin(), agent_id.end()) + L"\r\n";

    WinHttpAddRequestHeaders(hRequest_, upgrade_hdr.c_str(), (DWORD)upgrade_hdr.length(), WINHTTP_ADDREQ_FLAG_ADD);
    WinHttpAddRequestHeaders(hRequest_, conn_hdr.c_str(), (DWORD)conn_hdr.length(), WINHTTP_ADDREQ_FLAG_ADD);
    WinHttpAddRequestHeaders(hRequest_, ws_ver.c_str(), (DWORD)ws_ver.length(), WINHTTP_ADDREQ_FLAG_ADD);
    WinHttpAddRequestHeaders(hRequest_, ws_key_hdr.c_str(), (DWORD)ws_key_hdr.length(), WINHTTP_ADDREQ_FLAG_ADD);
    WinHttpAddRequestHeaders(hRequest_, auth_hdr1.c_str(), (DWORD)auth_hdr1.length(), WINHTTP_ADDREQ_FLAG_ADD);
    WinHttpAddRequestHeaders(hRequest_, auth_hdr2.c_str(), (DWORD)auth_hdr2.length(), WINHTTP_ADDREQ_FLAG_ADD);
    WinHttpAddRequestHeaders(hRequest_, agent_hdr.c_str(), (DWORD)agent_hdr.length(), WINHTTP_ADDREQ_FLAG_ADD);

    BOOL bResults = WinHttpSendRequest(hRequest_, WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                                       WINHTTP_NO_REQUEST_DATA, 0, 0, 0);
    if (!bResults) return false;

    bResults = WinHttpReceiveResponse(hRequest_, NULL);
    if (!bResults) return false;

    DWORD status = 0;
    DWORD size = sizeof(status);
    WinHttpQueryHeaders(hRequest_, WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
                        WINHTTP_HEADER_NAME_BY_INDEX, &status, &size, WINHTTP_NO_HEADER_INDEX);
    if (status != 101) return false;

    connected_ = true;
    return true;
}

bool WebSocketClient::connect(const std::string& url, const std::string& access_key, const std::string& agent_id) {
    disconnect();
    parse_url(url);

    hSession_ = WinHttpOpen(L"PCManagerAgentCPP/1.0",
                            WINHTTP_ACCESS_TYPE_NO_PROXY,
                            WINHTTP_NO_PROXY_NAME,
                            WINHTTP_NO_PROXY_BYPASS, 0);
    if (!hSession_) return false;

    WinHttpSetTimeouts(hSession_, 5000, 5000, 30000, 30000);

    hConnect_ = WinHttpConnect(hSession_, server_host_.c_str(), server_port_, 0);
    if (!hConnect_) {
        WinHttpCloseHandle(hSession_);
        hSession_ = nullptr;
        return false;
    }

    if (!do_ws_upgrade(access_key, agent_id)) {
        if (hRequest_) { WinHttpCloseHandle(hRequest_); hRequest_ = nullptr; }
        WinHttpCloseHandle(hConnect_); hConnect_ = nullptr;
        WinHttpCloseHandle(hSession_); hSession_ = nullptr;
        return false;
    }

    return true;
}

void WebSocketClient::disconnect() {
    connected_ = false;
    if (hRequest_) {
        WinHttpWebSocketClose(hRequest_, WINHTTP_WEB_SOCKET_SUCCESS_CLOSE_STATUS, NULL, 0);
        WinHttpCloseHandle(hRequest_);
        hRequest_ = nullptr;
    }
    if (hConnect_) { WinHttpCloseHandle(hConnect_); hConnect_ = nullptr; }
    if (hSession_) { WinHttpCloseHandle(hSession_); hSession_ = nullptr; }
}

bool WebSocketClient::send(const std::string& message) {
    if (!connected_ || !hRequest_) return false;

    DWORD result = WinHttpWebSocketSend(hRequest_,
                                         WINHTTP_WEB_SOCKET_UTF8_MESSAGE_BUFFER_TYPE,
                                         (PVOID)message.c_str(),
                                         (DWORD)message.length());
    return (result == NO_ERROR);
}

bool WebSocketClient::receive(std::string& out, int timeout_ms) {
    if (!connected_ || !hRequest_) return false;

    BYTE buffer[4096];
    DWORD dwBytesRead = 0;
    WINHTTP_WEB_SOCKET_BUFFER_TYPE eType;

    DWORD result = WinHttpWebSocketReceive(hRequest_, buffer, sizeof(buffer) - 1, &dwBytesRead, &eType);
    if (result != NO_ERROR) return false;

    if (dwBytesRead > 0) {
        buffer[dwBytesRead] = 0;
        out.assign((char*)buffer, dwBytesRead);
    }
    return true;
}
