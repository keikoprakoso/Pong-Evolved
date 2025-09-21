#include "AIClient.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <cstring>
#include <iostream>

AIClient::AIClient() : sock(-1), connected(false) {}

AIClient::~AIClient() {
    if (sock != -1) close(sock);
}

bool AIClient::connect(const std::string& host, int port) {
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) return false;

    sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, host.c_str(), &addr.sin_addr);

    if (::connect(sock, (sockaddr*)&addr, sizeof(addr)) == -1) {
        close(sock);
        sock = -1;
        return false;
    }

    // Set non-blocking
    int flags = fcntl(sock, F_GETFL, 0);
    fcntl(sock, F_SETFL, flags | O_NONBLOCK);

    connected = true;
    return true;
}

bool AIClient::send_state(const std::string& json) {
    if (!connected) return false;
    std::string msg = json + "\n";
    ssize_t sent = send(sock, msg.c_str(), msg.size(), 0);
    return sent != -1;
}

std::string AIClient::recv_action() {
    if (!connected) return "";
    char buffer[4096];
    ssize_t len = recv(sock, buffer, sizeof(buffer) - 1, 0);
    if (len > 0) {
        buffer[len] = '\0';
        return std::string(buffer);
    } else if (len == 0) {
        connected = false;
    }
    return "";
}