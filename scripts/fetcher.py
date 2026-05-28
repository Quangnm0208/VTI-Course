"""
fetcher.py — Lớp trừu tượng để tải HTML.

Hỗ trợ 2 engine:
    - requests:    Nhanh, ít tốn tài nguyên. Hay bị Cloudflare chặn (403).
    - playwright:  Headless Chromium thật, vượt được hầu hết bot-check
                   (Cloudflare, Akamai...). Chậm hơn ~3-5 lần.

Cả 2 engine đều export cùng interface: fetch_page(url) -> Optional[str].
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import requests

from config import HTTP_HEADERS, REQUEST_TIMEOUT

log = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Engine 1: requests (mặc định nhanh nhưng dễ bị block)
# -----------------------------------------------------------------------------
def fetch_with_requests(url: str) -> Optional[str]:
    """Tải HTML bằng requests. Trả về None nếu lỗi."""
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as err:
        log.error("[requests] Lỗi %s: %s", url, err)
        return None


# -----------------------------------------------------------------------------
# Engine 2: Playwright (vượt Cloudflare)
# -----------------------------------------------------------------------------
class PlaywrightFetcher:
    """
    Wrapper Playwright để fetch nhiều URL trong cùng 1 session (tái sử dụng
    browser - tiết kiệm thời gian startup ~2s mỗi URL).

    Dùng theo pattern context manager:
        with PlaywrightFetcher() as fetcher:
            html = fetcher.fetch(url)
    """

    def __init__(self, headless: bool = True, wait_for: str = "networkidle"):
        """
        Args:
            headless: True chạy không hiển thị browser (production).
            wait_for: 'load' | 'domcontentloaded' | 'networkidle'. Mặc định
                     'networkidle' để Cloudflare challenge chạy xong.
        """
        self._headless = headless
        self._wait_for = wait_for
        self._pw = None
        self._browser = None
        self._context = None

    def __enter__(self):
        # Import bên trong để không bắt buộc cài playwright khi dùng engine requests
        from playwright.sync_api import sync_playwright

        self._pw = sync_playwright().start()

        # Dùng Chromium - tương thích nhất với Cloudflare challenge
        self._browser = self._pw.chromium.launch(
            headless=self._headless,
            args=[
                "--disable-blink-features=AutomationControlled",   # ẩn cờ webdriver
                "--no-sandbox",                                    # cần cho CI
                "--disable-dev-shm-usage",                         # tránh hết RAM trên CI
            ],
        )

        # Tạo browser context với user-agent thật & viewport desktop
        self._context = self._browser.new_context(
            user_agent=HTTP_HEADERS["User-Agent"],
            viewport={"width": 1920, "height": 1080},
            locale="vi-VN",
            timezone_id="Asia/Ho_Chi_Minh",
        )

        # Patch JS để ẩn navigator.webdriver=true (cờ phổ biến mà bot detector check)
        self._context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._context: self._context.close()
            if self._browser: self._browser.close()
            if self._pw:      self._pw.stop()
        except Exception as err:
            log.warning("Lỗi khi đóng Playwright: %s", err)

    def fetch(self, url: str, retries: int = 2) -> Optional[str]:
        """
        Tải 1 URL. Tự retry nếu gặp Cloudflare challenge.

        Returns:
            HTML string nếu thành công, None nếu mọi retry đều fail.
        """
        page = self._context.new_page()
        try:
            for attempt in range(1, retries + 1):
                try:
                    response = page.goto(
                        url,
                        wait_until=self._wait_for,
                        timeout=REQUEST_TIMEOUT * 1000,
                    )

                    # Status check
                    if response is None:
                        log.warning("[playwright] %s: không có response", url)
                        continue

                    status = response.status
                    if status == 403:
                        # Có thể là Cloudflare 5-second challenge - đợi thêm
                        log.info("[playwright] %s: 403, chờ challenge...", url)
                        page.wait_for_timeout(5000)

                    # Check tiêu đề có chứa "Just a moment" (Cloudflare challenge)
                    title = page.title()
                    if "just a moment" in title.lower() or "checking" in title.lower():
                        log.info("[playwright] %s: Cloudflare challenge, chờ 8s", url)
                        page.wait_for_timeout(8000)

                    html = page.content()
                    if html and len(html) > 1000:        # Trang valid thường > 1KB
                        return html

                    log.warning(
                        "[playwright] %s lần %d: content quá ngắn (%d)",
                        url, attempt, len(html or ""),
                    )
                except Exception as err:
                    log.warning("[playwright] %s lần %d: %s", url, attempt, err)
                    time.sleep(2)

            return None
        finally:
            page.close()


# -----------------------------------------------------------------------------
# Factory: tạo fetcher theo tên engine
# -----------------------------------------------------------------------------
def get_fetcher(engine: str):
    """
    Trả về 1 fetcher tương ứng với engine.

    Đối với 'requests' trả về callable đơn giản,
    đối với 'playwright' trả về context manager (cần dùng `with ... as f`).
    """
    if engine == "requests":
        return fetch_with_requests
    if engine == "playwright":
        return PlaywrightFetcher()
    raise ValueError(f"Engine không hỗ trợ: {engine!r}. Dùng 'requests' hoặc 'playwright'.")
