# -*- coding: utf-8 -*-
"""
Tests of overlay_arrows_and_more. They need Windows and a desktop: they run in the CI on the Windows runners of GitHub.
"""

import sys
import time

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="overlay_arrows_and_more needs Windows")

if sys.platform == "win32":
    import win32gui
    import overlay_arrows_and_more as oaam

RED = (255, 0, 0)


def _wait_for_the_window(overlay, timeout=10.0):
    """Waits until the thread of the overlay has created its window."""
    deadline = time.monotonic() + timeout
    while overlay.h_window is None and time.monotonic() < deadline:
        time.sleep(0.01)
    assert overlay.h_window is not None, "The window of the overlay was not created"


def _paint(overlay):
    """Refreshes the overlay and waits until it is painted."""
    overlay.refresh()
    win32gui.UpdateWindow(overlay.h_window)  # it returns when the thread of the overlay has painted it
    time.sleep(0.2)  # time for the desktop window manager to compose the screen


def _grab(bbox):
    """Returns a capture of the screen in the rectangle bbox (left, top, right, bottom), with the overlays."""
    from PIL import ImageGrab
    return ImageGrab.grab(bbox=bbox, include_layered_windows=True, all_screens=True).convert("RGB")


@pytest.fixture
def overlay():
    overlay = oaam.Overlay()
    _wait_for_the_window(overlay)
    yield overlay
    overlay.quit()


def test_to_pixels(overlay):
    assert overlay._to_pixels(123, 1000) == 123
    assert overlay._to_pixels(12.7, 1000) == 12
    assert overlay._to_pixels("123", 1000) == 123
    assert overlay._to_pixels("12.5%", 1000) == 125
    assert overlay._to_pixels(" 50% ", 801) == 400


def test_a_filled_rectangle_is_displayed(overlay):
    """Tests that the screen capture shows the overlay: the other tests compare captures of the screen."""
    bbox = (100, 100, 300, 200)
    overlay.add(geometry=oaam.Shape.rectangle, x=100, y=100, width=200, height=100, thickness=0,
                brush=oaam.Brush.solid, brush_color=RED)
    _paint(overlay)
    assert _grab(bbox).getpixel((100, 50)) == RED
    overlay.clear_all()
    _paint(overlay)
    assert _grab(bbox).getpixel((100, 50)) != RED
