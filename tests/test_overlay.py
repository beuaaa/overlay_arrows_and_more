# -*- coding: utf-8 -*-
"""
Tests of overlay_arrows_and_more. They need Windows and a desktop: they run in the CI on the Windows runners of GitHub.
"""

import ctypes
import importlib.util
import os
import sys
import threading
import time

import pytest

if sys.platform != "win32":
    pytest.skip("overlay_arrows_and_more needs Windows", allow_module_level=True)

import win32api  # noqa: E402
import win32con  # noqa: E402
import win32gui  # noqa: E402
from ctypes import wintypes  # noqa: E402

import overlay_arrows_and_more as oaam  # noqa: E402
from overlay_arrows_and_more import overlay as overlay_module  # noqa: E402

RED = (255, 0, 0)
GRAY = (128, 128, 128)

# The tests check positions in captures of the screen, which are in physical pixels: on a display scaled to 125 % or
# more, Windows enlarges the windows of a process that is not DPI aware, and the drawings would not be where expected.
ctypes.windll.user32.SetProcessDPIAware()


def _paint(overlay):
    """Refreshes the overlay and waits until it is painted and displayed."""
    overlay.refresh()
    win32gui.UpdateWindow(overlay.h_window)  # it returns when the thread of the overlay has painted the window
    time.sleep(0.2)  # time for the desktop window manager to compose the screen


def _grab(bbox):
    """Returns a capture of the screen in the rectangle bbox (left, top, right, bottom), with the overlays."""
    from PIL import ImageGrab
    return ImageGrab.grab(bbox=bbox, include_layered_windows=True, all_screens=True).convert("RGB")


_kernel32 = ctypes.WinDLL("kernel32")
_kernel32.GetCurrentProcess.restype = wintypes.HANDLE
_user32 = ctypes.WinDLL("user32")
_user32.GetGuiResources.argtypes = [wintypes.HANDLE, wintypes.DWORD]
_user32.GetGuiResources.restype = wintypes.DWORD


def _gdi_objects():
    """Returns the number of GDI objects of this process."""
    return _user32.GetGuiResources(_kernel32.GetCurrentProcess(), 0)  # 0: GR_GDIOBJECTS


@pytest.fixture
def overlay():
    overlay = oaam.Overlay()
    yield overlay
    overlay.quit(timeout=10)


# ---------------------------------------------------------------------------------------------------- life cycle

def test_the_window_exists_when_the_constructor_returns():
    """Before, the constructor returned before the window was created: refresh() then redrew all the windows."""
    overlay = oaam.Overlay()
    try:
        assert overlay.h_window is not None
        assert win32gui.IsWindow(overlay.h_window)
    finally:
        overlay.quit(timeout=10)


def test_quit_just_after_the_creation():
    """Before, quit() never returned if it was called before the window was created."""
    for _ in range(20):
        overlay = oaam.Overlay()
        overlay.quit(timeout=10)
        assert not overlay.is_alive()
        assert not win32gui.IsWindow(overlay.h_window)


def test_quit_twice_then_refresh():
    overlay = oaam.Overlay()
    overlay.quit(timeout=10)
    overlay.quit(timeout=10)
    overlay.refresh()
    assert not overlay.is_alive()


def test_with_statement():
    with oaam.Overlay(transparency=0.5) as overlay:
        overlay.add(geometry=oaam.Shape.rectangle, x=10, y=10, width=50, height=50, thickness=2, color=RED)
        overlay.refresh()
    assert not overlay.is_alive()


def test_the_window_covers_the_virtual_screen(overlay):
    """Before, the origin was taken from the work areas: the drawings were shifted with a taskbar at the top or left."""
    x = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    y = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    assert (overlay.x_min, overlay.y_min) == (x, y)
    assert win32gui.GetWindowRect(overlay.h_window) == (
        x, y, x + win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN),
        y + win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN))


def test_frequency():
    """Tests the automatic refresh, by a timer of the window. Before, a thread was started at each refresh."""
    threads = threading.active_count()
    overlay = oaam.Overlay(frequency=20)
    try:
        paint_count = overlay._paint_count
        time.sleep(1.0)
        assert overlay._paint_count - paint_count >= 5
        assert threading.active_count() <= threads + 1  # the thread of the overlay only
    finally:
        overlay.quit(timeout=10)
    paint_count = overlay._paint_count
    time.sleep(0.3)
    assert overlay._paint_count == paint_count
    assert threading.active_count() <= threads


def test_frequency_none():
    """Overlay(frequency=None), as written in the README, raised a TypeError."""
    with oaam.Overlay(frequency=None) as overlay:
        assert overlay.period == 0


# ---------------------------------------------------------------------------------------------------- elements

def test_to_pixels(overlay):
    assert overlay._to_pixels(123, 1000) == 123
    assert overlay._to_pixels(12.7, 1000) == 12
    assert overlay._to_pixels("123", 1000) == 123
    assert overlay._to_pixels("12.5%", 1000) == 125
    assert overlay._to_pixels(" 50% ", 801) == 400
    assert overlay._to_pixels("0%", 3840, origin=-1920) == -1920
    assert overlay._to_pixels("50%", 3840, origin=-1920) == 0


def test_a_position_in_percentage_starts_at_the_origin_of_the_virtual_screen(overlay):
    overlay.add(geometry=oaam.Shape.rectangle, x="0%", y="0%", width="50%", height="10%")
    element = overlay.graphical_elements[-1]
    assert element["x"] == win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    assert element["y"] == win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)


@pytest.mark.parametrize("text_format, flags", [
    ("win32con.DT_RIGHT | win32con.DT_BOTTOM", win32con.DT_RIGHT | win32con.DT_BOTTOM),
    ("win32con.DT_LEFT|win32con.DT_WORDBREAK|win32con.DT_EXPANDTABS|win32con.DT_EDITCONTROL|win32con.DT_NOCLIP",
     win32con.DT_LEFT | win32con.DT_WORDBREAK | win32con.DT_EXPANDTABS | win32con.DT_EDITCONTROL | win32con.DT_NOCLIP),
    ("DT_CENTER | DT_SINGLELINE", win32con.DT_CENTER | win32con.DT_SINGLELINE),
    ("0x10 | 1", 0x11),
    (0x25, 0x25),
])
def test_text_format(text_format, flags):
    """Before, a text format given as a string was evaluated by eval() at each refresh."""
    assert overlay_module._text_format_flags(text_format) == flags


@pytest.mark.parametrize("text_format, error", [
    ("win32con.DT_LEFT | os.system('calc')", ValueError), ("win32con.WS_POPUP", ValueError), ("", ValueError),
    (1.5, TypeError), (None, TypeError)])
def test_wrong_text_format(text_format, error):
    with pytest.raises(error):
        overlay_module._text_format_flags(text_format)


def test_add_converts_the_text_format(overlay):
    overlay.add(geometry=oaam.Shape.rectangle, text="Text", text_format="win32con.DT_RIGHT | win32con.DT_WORDBREAK")
    assert overlay.graphical_elements[-1]["text_format"] == win32con.DT_RIGHT | win32con.DT_WORDBREAK


@pytest.mark.parametrize("parameters, error", [
    (dict(geometry=1), TypeError),
    (dict(geometry=oaam.Shape.rectangle, brush=1), TypeError),
    (dict(geometry=oaam.Shape.image), ValueError),
    (dict(geometry=oaam.Shape.triangle, xyrgb_array=((1, 2, 0, 0, 0),)), ValueError),
    (dict(text="Text", text_format="DT_UNKNOWN"), ValueError),
])
def test_add_an_element_that_cannot_be_drawn(overlay, parameters, error):
    """Before, add() accepted it, and the error occurred at each refresh, in the thread of the overlay."""
    with pytest.raises(error):
        overlay.add(**parameters)
    assert overlay.graphical_elements == []


def test_an_element_that_cannot_be_drawn_does_not_prevent_drawing_the_others(overlay, capsys):
    """
    Before, the drawing stopped at the first element that could not be drawn, EndPaint was not called, and the error
    was printed at each refresh.
    """
    bbox = (100, 100, 300, 200)
    overlay.graphical_elements.append({'geometry': oaam.Shape.image, 'x': 100, 'y': 100})  # without hicon
    overlay.add(geometry=oaam.Shape.rectangle, x=100, y=100, width=200, height=100, brush_color=RED)
    for _ in range(3):
        _paint(overlay)
    assert _grab(bbox).getpixel((100, 50)) == RED
    assert capsys.readouterr().err.count("this graphical element is not drawn") == 1


def test_add_and_clear_all_while_the_overlay_is_drawn(overlay):
    """Before, add() and clear_all() changed the list of the elements while the thread of the overlay used it."""
    stop = threading.Event()

    def change_the_elements():
        while not stop.is_set():
            overlay.clear_all()
            for i in range(20):
                overlay.add(geometry=oaam.Shape.rectangle, x=10 + i, y=10, width=50, height=50, thickness=1, color=RED,
                            text=str(i))

    thread = threading.Thread(target=change_the_elements)
    thread.start()
    try:
        for _ in range(100):
            overlay.refresh()
            win32gui.UpdateWindow(overlay.h_window)
    finally:
        stop.set()
        thread.join()
    assert overlay._reported_errors == set()


def test_no_gdi_object_leak(overlay):
    """Before, the pen of an element without geometry, a text only, was not deselected and could not be deleted."""
    overlay.add(x=10, y=10, width=100, height=20, text="Text only", text_color=RED)
    overlay.add(x=10, y=40, width=100, height=20, text="Rotated text only", angle=30)
    overlay.add(geometry=oaam.Shape.rectangle, x=10, y=70, width=100, height=20, thickness=2, color=RED,
                brush=oaam.Brush.cross, brush_color=GRAY, text="Rectangle")
    overlay.add(geometry=oaam.Shape.arrow, x=200, y=100, thickness=5, color=RED, angle=45)
    for _ in range(10):
        _paint(overlay)
    gdi_objects = _gdi_objects()
    assert gdi_objects > 0
    for _ in range(200):
        overlay.refresh()
        win32gui.UpdateWindow(overlay.h_window)
    assert _gdi_objects() - gdi_objects < 10


def test_the_package_needs_pywin32():
    """Before, the packages built on Linux by the publishing workflow had no dependency."""
    import importlib.metadata
    assert 'pywin32; sys_platform == "win32"' in importlib.metadata.requires("overlay_arrows_and_more")
    assert importlib.metadata.version("overlay_arrows_and_more") == oaam.__version__


def test_module_exports():
    assert set(overlay_module.__all__) == {"Shape", "Brush", "Overlay", "load_png", "load_ico"}
    assert not hasattr(oaam, "Thread")  # before, "from .overlay import *" also exported Thread, Timer, windll...


# ---------------------------------------------------------------------------------------------------- drawings

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


def test_load_png(overlay, tmp_path):
    from PIL import Image
    path = tmp_path / "red.png"
    Image.new("RGBA", (32, 32), RED + (255,)).save(path)
    hicon = oaam.load_png(str(path), 32, 32)
    assert hicon
    overlay.add(geometry=oaam.Shape.image, hicon=hicon, x=300, y=300)
    _paint(overlay)
    assert _grab((300, 300, 332, 332)).getpixel((16, 16)) == RED


def _scene(module):
    """The graphical elements drawn by 0.5.1 and by this version, on an opaque background."""
    shape, brush = module.Shape, module.Brush
    hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    elements = [
        dict(geometry=shape.rectangle, x=20, y=20, width=760, height=560, thickness=0, brush=brush.solid,
             brush_color=(200, 200, 200)),
        dict(geometry=shape.rectangle, x=40, y=40, width=200, height=80, thickness=6, color=(0, 0, 255)),
        dict(geometry=shape.rectangle, x=260, y=40, width=200, height=80, thickness=0, brush=brush.solid,
             brush_color=RED),
        dict(geometry=shape.ellipse, x=480, y=40, width=120, height=80, color=(0, 128, 0), thickness=3,
             brush=brush.solid, brush_color=(255, 255, 0)),
        dict(geometry=shape.arrow, x=700, y=80, thickness=6, color=(0, 0, 255), angle=-180),
        dict(geometry=shape.rectangle, x=600, y=200, width=120, height=50, thickness=4, color=(0, 128, 0), angle=30,
             center_of_rotation=(60, 25)),
        dict(geometry=shape.triangle, thickness=0,
             xyrgb_array=((40, 450, 255, 0, 0), (240, 450, 0, 255, 0), (240, 560, 0, 0, 255))),
        dict(geometry=shape.triangle, thickness=3, color=(0, 0, 0),
             xyrgb_array=((260, 450, 255, 0, 0), (360, 450, 0, 255, 0), (360, 560, 0, 0, 255))),
        dict(geometry=shape.image, hicon=hicon, x=400, y=470),
        dict(geometry=shape.image, hicon=hicon, x=480, y=470, angle=30, center_of_rotation=(16, 16)),
        dict(geometry=shape.rectangle, x=40, y=150, width=300, height=60, thickness=2, color=(0, 0, 255),
             text_color=(0, 0, 0), text=u"Il était une fois..."),
        dict(geometry=shape.rectangle, x=40, y=230, width=300, height=100, thickness=1, color=(0, 0, 0),
             brush=brush.solid, brush_color=(255, 255, 254), text="Name: OK\nType:\tButton", text_color=(0, 0, 0),
             font_size=14, font_name="Consolas",
             text_format="win32con.DT_LEFT|win32con.DT_WORDBREAK|win32con.DT_EXPANDTABS|win32con.DT_EDITCONTROL|"
                         "win32con.DT_NOCLIP"),
        dict(geometry=shape.rectangle, x=360, y=150, width=200, height=40, font_size=30, text="Pywinauto recorder",
             text_color=(254, 255, 255), color=(255, 255, 255), thickness=0),
    ]
    elements += [dict(geometry=shape.rectangle, x=40 + 60 * i, y=360, width=50, height=50, thickness=1, color=(0, 0, 0),
                      brush=b, brush_color=(0, 128, 0))
                 for i, b in enumerate([brush.b_diagonal, brush.cross, brush.diag_cross, brush.f_diagonal,
                                        brush.horizontal, brush.vertical])]
    return elements


def _draw_scene(module):
    """Returns a capture of the screen with the scene drawn by an overlay of the module."""
    overlay = module.Overlay()
    deadline = time.monotonic() + 10
    while overlay.h_window is None and time.monotonic() < deadline:  # the constructor of 0.5.1 did not wait for it
        time.sleep(0.01)
    try:
        for element in _scene(module):
            overlay.add(**element)
        _paint(overlay)
        time.sleep(0.3)
        return _grab((20, 20, 780, 580))
    finally:
        overlay.quit()
        time.sleep(0.3)


def test_drawings_identical_to_0_5_1():
    """The drawings of the elements are the same as those of version 0.5.1, pixel by pixel."""
    spec = importlib.util.spec_from_file_location(
        "overlay_0_5_1", os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlay_0_5_1.py"))
    overlay_0_5_1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(overlay_0_5_1)
    expected = _draw_scene(overlay_0_5_1)
    assert len(expected.getcolors(maxcolors=1 << 24)) > 10, "the capture of the screen does not show the overlay"
    drawn = _draw_scene(oaam)
    from PIL import ImageChops
    difference = ImageChops.difference(expected, drawn)
    different = sum(difference.point(lambda value: 255 if value else 0).convert("L").histogram()[1:])
    assert difference.getbbox() is None, "%d different pixels in %s" % (different, difference.getbbox())
