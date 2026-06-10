#include "http_client.h"
#include <windows.h>
#include <winhttp.h>
#include <iostream>
#include <sstream>
#include <fstream>

#pragma comment(lib, "winhttp.lib")

static std::wstring to_wstring(const std::string& str) {
    if (str.empty()) return L"";
    int size_needed = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), NULL, 0);
    if (size_needed <= 0) return L"";
    std::wstring wstrTo(size_needed, 0);
    MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), &wstrTo[0], size_needed);
    return wstrTo;
}

static std::string to_string(const std::wstring& wstr) {
    if (wstr.empty()) return "";
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), NULL, 0, NULL, NULL);
    if (size_needed <= 0) return "";
    std::string strTo(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), &strTo[0], size_needed, NULL, NULL);
    return strTo;
}

HttpClient::HttpClient(const std::string& base_url, const std::string& access_key, const std::string& agent_id)
    : base_url_(base_url), access_key_(access_key), agent_id_(agent_id) {
    parse_url();
}

HttpClient::~HttpClient() {}

void HttpClient::parse_url() {
    // Basic URL parser for http://host:port or http://host
    std::string protocol_sep = "://";
    size_t protocol_pos = base_url_.find(protocol_sep);
    std::string host_port;
    if (protocol_pos != std::string::npos) {
        std::string prot = base_url_.substr(0, protocol_pos);
        is_https_ = (prot == "https");
        host_port = base_url_.substr(protocol_pos + protocol_sep.length());
    } else {
        is_https_ = false;
        host_port = base_url_;
    }

    size_t path_pos = host_port.find('/');
    if (path_pos != std::string::npos) {
        host_port = host_port.substr(0, path_pos);
    }

    size_t colon_pos = host_port.find(':');
    if (colon_pos != std::string::npos) {
        std::string host = host_port.substr(0, colon_pos);
        std::string port_str = host_port.substr(colon_pos + 1);
        server_host_ = to_wstring(host);
        server_port_ = std::stoi(port_str);
    } else {
        server_host_ = to_wstring(host_port);
        server_port_ = is_https_ ? 443 : 80;
    }
}

std::map<std::string, std::string> HttpClient::get_auth_headers() {
    std::map<std::string, std::string> headers;
    headers["X-Server-Access-Key"] = access_key_;
    headers["X-PCManager-Key"] = access_key_;
    headers["User-Agent"] = "PCControlWindowsAgent/1.7.0-CPP";
    
    // Check if activated mode (pc- prefix and token len > 20)
    bool is_activated = (agent_id_.rfind("pc-", 0) == 0 && access_key_.length() > 20);
    if (is_activated) {
        headers["X-Agent-Token"] = access_key_;
    }
    return headers;
}

HttpResponse HttpClient::request(const std::string& method, const std::string& path, const std::string& json_body, const std::map<std::string, std::string>& custom_headers) {
    HttpResponse response = { 0, "" };

    HINTERNET hSession = WinHttpOpen(L"PCManagerAgentCPP/1.0",
                                    WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                                    WINHTTP_NO_PROXY_NAME,
                                    WINHTTP_NO_PROXY_BYPASS, 0);
    if (!hSession) return response;

    HINTERNET hConnect = WinHttpConnect(hSession, server_host_.c_str(), server_port_, 0);
    if (!hConnect) {
        WinHttpCloseHandle(hSession);
        return response;
    }

    // Set timeouts: resolve=5s, connect=5s, send=8s, receive=8s
    WinHttpSetTimeouts(hSession, 5000, 5000, 8000, 8000);

    std::wstring wpath = to_wstring(path);
    std::wstring wmethod = to_wstring(method);

    DWORD flags = is_https_ ? WINHTTP_FLAG_SECURE : 0;
    HINTERNET hRequest = WinHttpOpenRequest(hConnect, wmethod.c_str(), wpath.c_str(),
                                           NULL, WINHTTP_NO_REFERER,
                                           WINHTTP_DEFAULT_ACCEPT_TYPES, flags);
    if (!hRequest) {
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);
        return response;
    }

    // Set headers
    std::map<std::string, std::string> headers = get_auth_headers();
    for (const auto& pair : custom_headers) {
        headers[pair.first] = pair.second;
    }

    if (!json_body.empty() && headers.find("Content-Type") == headers.end()) {
        headers["Content-Type"] = "application/json; charset=utf-8";
    }

    std::wstringstream header_ss;
    for (const auto& pair : headers) {
        header_ss << to_wstring(pair.first) << L": " << to_wstring(pair.second) << L"\r\n";
    }
    std::wstring header_str = header_ss.str();

    BOOL bResults = WinHttpSendRequest(hRequest,
                                       header_str.c_str(), (DWORD)header_str.length(),
                                       (LPVOID)json_body.c_str(), (DWORD)json_body.length(),
                                       (DWORD)json_body.length(), 0);

    if (bResults) {
        bResults = WinHttpReceiveResponse(hRequest, NULL);
    }

    if (bResults) {
        DWORD dwStatusCode = 0;
        DWORD dwSize = sizeof(dwStatusCode);
        WinHttpQueryHeaders(hRequest,
                            WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
                            WINHTTP_HEADER_NAME_BY_INDEX,
                            &dwStatusCode, &dwSize, WINHTTP_NO_HEADER_INDEX);
        response.status_code = dwStatusCode;

        DWORD dwSizeAvailable = 0;
        do {
            dwSizeAvailable = 0;
            if (!WinHttpQueryDataAvailable(hRequest, &dwSizeAvailable)) break;
            if (dwSizeAvailable == 0) break;

            std::vector<char> buffer(dwSizeAvailable + 1);
            DWORD dwBytesRead = 0;
            if (WinHttpReadData(hRequest, &buffer[0], dwSizeAvailable, &dwBytesRead)) {
                buffer[dwBytesRead] = '\0';
                response.body.append(&buffer[0], dwBytesRead);
            }
        } while (dwSizeAvailable > 0);
    }

    WinHttpCloseHandle(hRequest);
    WinHttpCloseHandle(hConnect);
    WinHttpCloseHandle(hSession);

    return response;
}

HttpResponse HttpClient::upload_file(const std::string& path, const std::wstring& file_path, const std::string& public_type, const std::string& mime_type) {
    HttpResponse response = { 0, "" };

    // Read file binary
    std::ifstream file(file_path, std::ios::binary);
    if (!file.is_open()) return response;

    std::stringstream file_data_ss;
    file_data_ss << file.rdbuf();
    std::string file_content = file_data_ss.str();
    file.close();

    // Extract filename from file_path
    std::wstring filename = file_path;
    size_t last_slash = filename.find_last_of(L"\\/");
    if (last_slash != std::wstring::npos) {
        filename = filename.substr(last_slash + 1);
    }
    std::string filename_str = to_string(filename);

    // Construct multipart form data
    std::string boundary = "----WebKitFormBoundaryCPPCPPPCManagerAgent";
    std::string body_start;
    body_start += "--" + boundary + "\r\n";
    body_start += "Content-Disposition: form-data; name=\"upload\"; filename=\"" + filename_str + "\"\r\n";
    body_start += "Content-Type: " + mime_type + "\r\n\r\n";

    std::string body_end = "\r\n--" + boundary + "--\r\n";

    std::string multipart_body = body_start + file_content + body_end;

    std::map<std::string, std::string> headers;
    headers["Content-Type"] = "multipart/form-data; boundary=" + boundary;

    return request("POST", path, multipart_body, headers);
}
