
#include <curl/curl.h>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>
#include <chrono>
#include <thread>

static size_t WriteCb(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

std::string env(const char* k, const char* defv) {
    const char* v = std::getenv(k);
    return v ? std::string(v) : std::string(defv);
}

long http_post(const std::string& url, const std::string& payload, std::string& out) {
    CURL* curl = curl_easy_init();
    if(!curl) return -1;
    struct curl_slist* headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCb);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &out);
    long code = 0;
    CURLcode res = curl_easy_perform(curl);
    if(res == CURLE_OK) curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &code);
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    return code;
}

long http_get(const std::string& url, std::string& out) {
    CURL* curl = curl_easy_init();
    if(!curl) return -1;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCb);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &out);
    long code = 0;
    CURLcode res = curl_easy_perform(curl);
    if(res == CURLE_OK) curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &code);
    curl_easy_cleanup(curl);
    return code;
}

// very naive string helpers (avoid bundling a full JSON lib)
std::string extract_cmd(const std::string& json) {
    auto key = std::string("\"cmd\"");
    auto pos = json.find(key);
    if (pos == std::string::npos) return "";
    auto q1 = json.find('"', json.find(':', pos) + 1);
    if (q1 == std::string::npos) return "";
    auto q2 = json.find('"', q1 + 1);
    if (q2 == std::string::npos) return "";
    return json.substr(q1 + 1, q2 - q1 - 1);
}

int main() {
    std::string orch = env("ORCHESTRATOR_URL", "http://localhost:8080");
    std::string workerId = env("WORKER_ID", "worker-1");

    // Register once
    {
        std::string out;
        long code = http_post(orch + "/api/v1/workers/register", "{\"id\":\"" + workerId + "\"}", out);
        std::cout << "[worker] register code=" << code << " body=" << out << std::endl;
    }

    int idleStreak = 0;
    while (true) {
        // heartbeat
        {
            std::string out;
            http_post(orch + "/api/v1/workers/" + workerId + "/heartbeat", "{}", out);
        }

        // claim next
        std::string claimed;
        long code = http_post(orch + "/api/v1/tasks/next?worker_id=" + workerId, "{}", claimed);
        if (code == 200) {
            idleStreak = 0;
            std::cout << "[worker] claimed: " << claimed << std::endl;

            // quick & dirty: parse task id and cmd
            // id
            int id = -1;
            auto idpos = claimed.find("\"id\":");
            if (idpos != std::string::npos) {
                auto comma = claimed.find(",", idpos);
                std::string val = claimed.substr(idpos + 5, comma - (idpos + 5));
                id = std::atoi(val.c_str());
            }
            // cmd
            std::string cmd = extract_cmd(claimed);
            if (cmd.empty()) cmd = "echo task-" + std::to_string(id);

            // execute
            std::string result = "ran: " + cmd;
            int rc = std::system(cmd.c_str());
            if (rc != 0) {
                std::string out;
                http_post(orch + "/api/v1/tasks/" + std::to_string(id) + "/fail",
                          std::string("{\"result_text\":\"exit ") + std::to_string(rc) + "\"}", out);
            } else {
                std::string out;
                http_post(orch + "/api/v1/tasks/" + std::to_string(id) + "/complete",
                          std::string("{\"result_text\":\"") + result + "\"}", out);
            }
        } else {
            idleStreak++;
            int sleepMs = std::min(5000, 200 * idleStreak);
            std::this_thread::sleep_for(std::chrono::milliseconds(sleepMs));
        }
    }
    return 0;
}
