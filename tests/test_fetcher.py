"""Tests cho fetcher: chỉ check phần không phụ thuộc network/browser."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from fetcher import PlaywrightFetcher, fetch_with_requests, get_fetcher


def test_get_fetcher_requests_returns_callable():
    fetcher = get_fetcher("requests")
    assert callable(fetcher)
    assert fetcher is fetch_with_requests


def test_get_fetcher_playwright_returns_context_manager():
    fetcher = get_fetcher("playwright")
    assert isinstance(fetcher, PlaywrightFetcher)
    # Có __enter__/__exit__ -> dùng được với 'with'
    assert hasattr(fetcher, "__enter__")
    assert hasattr(fetcher, "__exit__")


def test_get_fetcher_invalid_engine_raises():
    with pytest.raises(ValueError, match="Engine không hỗ trợ"):
        get_fetcher("selenium")


def test_playwright_fetcher_init_does_not_start_browser():
    """Khởi tạo không nên launch browser - chỉ launch khi vào context."""
    fetcher = PlaywrightFetcher(headless=True)
    assert fetcher._browser is None
    assert fetcher._pw is None
