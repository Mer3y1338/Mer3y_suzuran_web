#!/usr/bin/env python3
"""AstrBot 状态检测 API - 轻量级 HTTP 服务"""

import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 9527
ALLOWED_ORIGINS = [
    "https://suzuran.mer3y.xyz",
    "https://love.mer3y.xyz",
    "http://localhost",
    "http://127.0.0.1",
]

def check_astrbot():
    """检测 astrbot Docker 容器是否运行中"""
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Running}}", "astrbot"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and "true" in result.stdout.lower():
            # 额外检查容器健康状态
            uptime_result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.StartedAt}}", "astrbot"],
                capture_output=True, text=True, timeout=5
            )
            started_at = uptime_result.stdout.strip() if uptime_result.returncode == 0 else None
            return {"status": "online", "started_at": started_at}
        return {"status": "offline"}
    except FileNotFoundError:
        # docker 命令不存在
        return {"status": "unknown", "error": "docker not found"}
    except subprocess.TimeoutExpired:
        return {"status": "unknown", "error": "timeout"}
    except Exception as e:
        return {"status": "unknown", "error": str(e)}


class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/astrbot-status":
            data = check_astrbot()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            # CORS
            origin = self.headers.get("Origin", "")
            if origin in ALLOWED_ORIGINS or origin.startswith("http://localhost"):
                self.send_header("Access-Control-Allow-Origin", origin)
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # 静默日志，减少噪音
        pass


def main():
    server = HTTPServer(("127.0.0.1", PORT), StatusHandler)
    print(f"[AstrBot Status API] Listening on 127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
