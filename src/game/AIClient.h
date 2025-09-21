#pragma once

#include <string>

class AIClient {
public:
    AIClient();
    ~AIClient();
    bool connect(const std::string& host, int port);
    bool send_state(const std::string& json);
    std::string recv_action();

private:
    int sock;
    bool connected;
};