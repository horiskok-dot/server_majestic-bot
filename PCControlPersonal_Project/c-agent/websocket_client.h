#pragma once
#include <windows.h>
#include <winhttp.h>
#include <string>
#include <functional>

#pragma comment(lib, "winhttp.lib")

class WebSocketClient {
public:
    WebSocketClient();
    ~WebSocketClient();

    bool connect(const std::string& url, const std::string& access_key, const std::string& agent_id);
    void disconnect();
    bool send(const std::string& message);
    bool receive(std::string& out, int timeout_ms);
    bool is_connected() const { return connected_; }

    using MessageCallback = std::function<void(const std::string&)>;
    void set_callback(MessageCallback cb) { callback_ = cb; }

private:
    HINTERNET hSession_;
    HINTERNET hConnect_;
    HINTERNET hRequest_;
    bool connected_;
    std::wstring server_host_;
    int server_port_;
    bool is_https_;
    std::string path_;
    MessageCallback callback_;

    void parse_url(const std::string& url);
    std::string generate_key();
    bool do_ws_upgrade(const std::string& access_key, const std::string& agent_id);
};
