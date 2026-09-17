"""自动生成 Web 演示截图，用于 README 展示。"""
import os
import time
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright


SCRIPT_DIR = Path(__file__).parent.resolve()
SCREENSHOTS_DIR = SCRIPT_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)


def take_screenshots():
    server = subprocess.Popen(
        ["python", str(SCRIPT_DIR / "web_server.py")],
        cwd=SCRIPT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto("http://127.0.0.1:5000")
            time.sleep(1.5)

            # 1. 初始状态
            page.screenshot(path=str(SCREENSHOTS_DIR / "01_initial_state.png"))

            # 2. 在线模式：打开空调
            page.fill("#user-input", "打开空调")
            page.click("#send-btn")
            time.sleep(2)
            page.screenshot(path=str(SCREENSHOTS_DIR / "02_online_open_ac.png"))

            # 3. 在线模式：复合指令
            page.fill("#user-input", "把空调调到23度并打开副驾车窗")
            page.click("#send-btn")
            time.sleep(2.5)
            page.screenshot(path=str(SCREENSHOTS_DIR / "03_online_complex_command.png"))

            # 4. 切换到离线模式并执行关闭车窗
            page.click(".mode-switch .slider")
            time.sleep(0.8)
            page.fill("#user-input", "关闭所有车窗")
            page.click("#send-btn")
            time.sleep(2)
            page.screenshot(path=str(SCREENSHOTS_DIR / "04_offline_close_windows.png"))

            browser.close()
            print(f"截图已保存到 {SCREENSHOTS_DIR}")
    finally:
        server.terminate()


if __name__ == "__main__":
    take_screenshots()
