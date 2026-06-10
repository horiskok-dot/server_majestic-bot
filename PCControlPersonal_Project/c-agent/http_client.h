#pragma once
#include <string>
#include <vector>
#include <map>

struct HttpResponse {
    int status_code;
    std::string body;
};

class HttpClient {
public:
    HttpClient(const std::string& base_url, const std::string& access_key, const std::string& agent_id);
    ~HttpClient();

    HttpResponse request(const std::string& method, const std::string& path, const std::string& json_body = "", const std::map<std::string, std::string>& custom_headers = {});
    HttpResponse upload_file(const std::string& path, const std::wstring& file_path, const std::string& public_type, const std::string& mime_type);

private:
    std::string base_url_;
    std::string access_key_;
    std::string agent_id_;
    std::wstring server_host_;
    int server_port_;
    bool is_https_;

    void parse_url();
    std::map<std::string, std::string> get_auth_headers();
};
