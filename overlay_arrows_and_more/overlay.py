# -*- coding: utf-8 -*-
"""
The overlay: a transparent window on top of all the other windows, covering all the screens, on which graphical
elements are drawn: rectangles, ellipses, arrows, triangles, images and texts.
"""

import ctypes
import functools
import math
import sys
import threading
import time
import traceback
from ctypes import wintypes
from datetime import datetime
from enum import Enum
from uuid import uuid4

import win32api
import win32con
import win32gui

__all__ = ["Shape", "Brush", "Overlay", "load_png", "load_ico"]

CreateIconFromResourceEx = ctypes.windll.user32.CreateIconFromResourceEx

_user32 = ctypes.WinDLL("user32", use_last_error=True)  # a separate instance: argtypes set here do not leak to others
_user32.SetTimer.argtypes = [wintypes.HWND, ctypes.c_size_t, wintypes.UINT, ctypes.c_void_p]
_user32.SetTimer.restype = ctypes.c_size_t

_WINDOW_CREATION_TIMEOUT = 10.0
"""Maximum duration, in seconds, of the wait for the window of an overlay in its constructor."""

_REFRESH_TIMER_ID = 1
_DEFAULT_TEXT_FORMAT = win32con.DT_CENTER | win32con.DT_SINGLELINE | win32con.DT_VCENTER
_DEFAULT_XYRGB_ARRAY = ((15, 15, 255, 0, 0), (15, 45, 0, 255, 0), (45, 30, 0, 0, 255))


class Shape(Enum):
    rectangle = 0
    ellipse = 1
    arrow = 2
    triangle = 3
    image = 4


class Brush(Enum):
    solid = 0
    b_diagonal = 1  # 45 - degree upward left - to - right hatch
    cross = 2  # Horizontal and vertical crosshatch
    diag_cross = 3  # 45 - degree crosshatch
    f_diagonal = 4  # 45 - degree downward left - to - right hatch
    horizontal = 5  # Horizontal hatch
    vertical = 6  # Vertical hatch


_HATCH_STYLES = {
    Brush.b_diagonal: win32con.HS_BDIAGONAL,
    Brush.cross: win32con.HS_CROSS,
    Brush.diag_cross: win32con.HS_DIAGCROSS,
    Brush.f_diagonal: win32con.HS_FDIAGONAL,
    Brush.horizontal: win32con.HS_HORIZONTAL,
    Brush.vertical: win32con.HS_VERTICAL,
}


@functools.lru_cache(maxsize=None)
def _parse_text_format(text_format):
    """
    Returns the flags of DrawText written as a string, for example "win32con.DT_LEFT | win32con.DT_TOP".

    Each flag is the name of a DT_ constant of win32con, with or without "win32con.", or a number. Before, the string
    was evaluated by eval() at each refresh.
    """
    flags = 0
    for item in text_format.split("|"):
        name = item.strip()
        if name.startswith("win32con."):
            name = name[len("win32con."):]
        value = getattr(win32con, name, None) if name.startswith("DT_") else None
        if not isinstance(value, int):
            try:
                value = int(name, 0)
            except ValueError:
                raise ValueError("Unknown flag " + repr(item.strip()) + " in the text format " + repr(text_format)) from None
        flags |= value
    return flags


def _text_format_flags(text_format):
    """Returns the flags of DrawText of a text format given as flags (int) or as a string."""
    if isinstance(text_format, int):
        return text_format
    if isinstance(text_format, str):
        return _parse_text_format(text_format)
    raise TypeError("text_format must be flags of DrawText, such as win32con.DT_LEFT | win32con.DT_TOP, not " +
                    repr(text_format))


def _check_graphical_element(graphical_element):
    """It raises an exception if a graphical element cannot be drawn. Before, the error occurred at each refresh."""
    geometry = graphical_element.get("geometry")
    if geometry is not None and not isinstance(geometry, Shape):
        raise TypeError("geometry must be a Shape, not " + repr(geometry))
    brush = graphical_element.get("brush")
    if brush is not None and not isinstance(brush, Brush):
        raise TypeError("brush must be a Brush, not " + repr(brush))
    if geometry is Shape.image and "hicon" not in graphical_element:
        raise ValueError("An image needs an icon: hicon=load_ico(...) or hicon=load_png(...)")
    if geometry is Shape.triangle and "xyrgb_array" in graphical_element:
        xyrgb_array = graphical_element["xyrgb_array"]
        if len(xyrgb_array) < 3 or any(len(xyrgb) < 5 for xyrgb in xyrgb_array):
            raise ValueError("xyrgb_array needs 3 vertices (x, y, red, green, blue)")


def _create_brush(brush, color):
    """Returns a new brush of the given style and color (r, g, b)."""
    rgb = win32api.RGB(color[0], color[1], color[2])
    if brush is Brush.solid:
        return win32gui.CreateSolidBrush(rgb)
    return win32gui.CreateHatchBrush(_HATCH_STYLES[brush], rgb)


class Overlay(threading.Thread):
    """
    A transparent window on top of all the other windows, covering all the screens, on which graphical elements are
    drawn. The mouse and the keyboard go through it to the windows below.

    The window has its own thread, started by the constructor, which returns when the window is created.
    Pure white (255, 255, 255) is the transparent color: use (255, 255, 254) to draw in white.

    Example::

        with Overlay(transparency=0.5) as overlay:
            overlay.add(geometry=Shape.rectangle, x=100, y=100, width=300, height=200, thickness=5, color=(255, 0, 0))
            overlay.refresh()
            time.sleep(3)

    :param transparency: From 0.0 (opaque, the default) to 1.0 (invisible)
    :param frequency: The number of automatic refreshes per second (optional)
    """

    def __init__(self, **parameters):
        threading.Thread.__init__(self)
        self.h_window = None
        self.graphical_elements = []
        self.class_name = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
        if 'transparency' in parameters:
            self.transparency = int(255.0*(1.0 - parameters['transparency']))
        else:
            self.transparency = 255
        self.period = 0
        if parameters.get('frequency') is not None:
            frequency = float(parameters['frequency'])
            if frequency > 0:
                self.period = 1.0/frequency
        self.x_min = 0
        self.y_min = 0
        self._lock = threading.RLock()
        self._window_created = threading.Event()
        self._class_atom = None
        self._h_instance = None
        self._reported_errors = set()
        self._paint_count = 0
        self.daemon = True
        self.start()
        # Before, the constructor returned at once: quit() or refresh() could be called before the window existed
        self._window_created.wait(_WINDOW_CREATION_TIMEOUT)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.quit()
        return False

    def _to_pixels(self, value, base_px: int, origin: int = 0) -> int:
        """
        Converts a coordinate or a length to pixels:
            123          -> 123
            "123"        -> 123
            "12.5%"      -> origin + round(12.5 % of base_px)
        """
        if isinstance(value, (int, float)):
            return int(value)

        value = str(value).strip()
        if value.endswith('%'):
            pct = float(value[:-1])
            return origin + int(round(base_px * pct / 100.0))
        # plain integer string
        return int(value)

    @property
    def screen_width(self) -> int:
        """The width of the virtual screen, made of all the monitors."""
        return win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)

    @property
    def screen_height(self) -> int:
        """The height of the virtual screen, made of all the monitors."""
        return win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

    def run(self):
        """The thread of the overlay: it creates the window, then dispatches its messages until quit()."""
        try:
            self._create_window()
        finally:
            self._window_created.set()
        if self.period > 0:
            # A timer of the window: before, a new thread was started at each refresh, even after quit()
            _user32.SetTimer(self.h_window, _REFRESH_TIMER_ID, max(1, int(round(self.period * 1000))), None)
        win32gui.PumpMessages()
        self._destroy_window()

    def _create_window(self):
        """It creates the window of the overlay, which covers the virtual screen, made of all the monitors."""
        self._h_instance = win32api.GetModuleHandle()
        wnd_class = win32gui.WNDCLASS()
        wnd_class.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wnd_class.lpfnWndProc = self._window_procedure
        wnd_class.hInstance = self._h_instance
        wnd_class.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        wnd_class.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        wnd_class.lpszClassName = self.class_name
        self._class_atom = win32gui.RegisterClass(wnd_class)

        # The coordinates of the screen are converted to the coordinates of the window by subtracting its origin.
        # Before, the origin was taken from the work areas of the monitors, which exclude the taskbar: with a taskbar at
        # the top or on the left, everything was shifted.
        self.x_min = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        self.y_min = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        ex_style = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | \
            win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
        style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE
        self.h_window = win32gui.CreateWindowEx(
            ex_style, self._class_atom,
            'OverlayWindow',
            style,
            self.x_min,  # x
            self.y_min,  # y
            win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN),  # width
            win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN),  # height
            None,  # hWndParent
            None,  # hMenu
            self._h_instance,
            None  # lpParam
        )
        win32gui.SetLayeredWindowAttributes(self.h_window, 0x00ffffff, self.transparency,
                                            win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
        win32gui.SetWindowPos(self.h_window, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

    def _destroy_window(self):
        """At the end of the thread: it destroys the window if it still exists, and unregisters its class."""
        try:
            if self.h_window is not None and win32gui.IsWindow(self.h_window):
                win32gui.DestroyWindow(self.h_window)
        except win32gui.error:
            pass
        try:
            win32gui.UnregisterClass(self._class_atom, self._h_instance)
        except win32gui.error:
            pass

    def _window_procedure(self, h_window, message, w_param, l_param):
        """It handles the messages of the window, in the thread of the overlay."""
        if message == win32con.WM_PAINT:
            self._paint(h_window)
            return 0
        if message == win32con.WM_TIMER:
            win32gui.InvalidateRect(h_window, None, True)
            return 0
        if message == win32con.WM_CLOSE:
            win32gui.DestroyWindow(h_window)
            return 0
        if message in (win32con.WM_DESTROY, win32con.WM_QUIT):  # WM_QUIT: sent by quit() before version 0.6.0
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(h_window, message, w_param, l_param)

    def _paint(self, h_window):
        """It draws the graphical elements. An element that cannot be drawn does not prevent drawing the others."""
        hdc, paint_struct = win32gui.BeginPaint(h_window)
        try:
            win32gui.SetGraphicsMode(hdc, win32con.GM_ADVANCED)
            win32gui.BringWindowToTop(h_window)
            with self._lock:
                graphical_elements = list(self.graphical_elements)  # add() and clear_all() may be called meanwhile
            for graphical_element in graphical_elements:
                try:
                    self._draw(hdc, graphical_element)
                except Exception:
                    self._report_drawing_error(graphical_element)
        finally:
            win32gui.EndPaint(h_window, paint_struct)  # before, an error skipped it: the device context was not released
            self._paint_count += 1

    def _report_drawing_error(self, graphical_element):
        """It prints the error of a graphical element that cannot be drawn, once instead of at each refresh."""
        exc_type, exc_value, _ = sys.exc_info()
        error = (exc_type, str(exc_value))
        if error not in self._reported_errors:
            self._reported_errors.add(error)
            sys.stderr.write("overlay_arrows_and_more: this graphical element is not drawn: " + repr(graphical_element) +
                             "\n")
            traceback.print_exc()

    def _draw(self, hdc, r):
        """It draws a graphical element: the dictionary of the parameters given to add()."""
        geometry = r.get('geometry')
        x = r['x'] - self.x_min if 'x' in r else 0
        y = r['y'] - self.y_min if 'y' in r else 0
        width = r.get('width', 100)
        height = r.get('height', 100)
        xyrgb_array = r.get('xyrgb_array', _DEFAULT_XYRGB_ARRAY)
        thickness = r.get('thickness', 0)
        brush_color = r.get('brush_color', (255, 255, 255))
        color = r.get('color', (255, 0, 0)) if thickness != 0 else brush_color

        if geometry is Shape.triangle:
            self._fill_triangle(hdc, xyrgb_array)

        # The brush and the pen are kept in variables until they are deselected: pywin32 deletes them when they are
        # released, and a GDI object selected in a device context cannot be deleted.
        brush = old_brush = None
        if r.get('brush') is not None and width > 1 and height > 1:
            brush = _create_brush(r['brush'], brush_color)
            old_brush = win32gui.SelectObject(hdc, brush)
        pen = win32gui.CreatePen(win32con.PS_GEOMETRIC, thickness, win32api.RGB(color[0], color[1], color[2]))
        old_pen = win32gui.SelectObject(hdc, pen)
        try:
            x, y = self._draw_shape(hdc, r, geometry, x, y, width, height, thickness, xyrgb_array)
        finally:
            # before, the pen and the rotation were restored only for an element with a geometry
            win32gui.SelectObject(hdc, old_pen)
            if brush is not None:
                win32gui.SelectObject(hdc, old_brush)

        if 'text' in r:
            self._draw_text(hdc, r, x, y, width, height, brush_color)

    def _fill_triangle(self, hdc, xyrgb_array):
        """It fills a triangle with a gradient between the colors of its vertices (x, y, red, green, blue)."""
        vertices = tuple({'x': int(round(xyrgb[0])) - self.x_min,
                          'y': int(round(xyrgb[1])) - self.y_min,
                          'Red': xyrgb[2] * 256,
                          'Green': xyrgb[3] * 256,
                          'Blue': xyrgb[4] * 256,
                          'Alpha': 0} for xyrgb in xyrgb_array)
        mesh = ((0, 1, 2),)
        win32gui.GradientFill(hdc, vertices, mesh, win32con.GRADIENT_FILL_TRIANGLE)

    def _draw_shape(self, hdc, r, geometry, x, y, width, height, thickness, xyrgb_array):
        """
        It draws the shape of a graphical element with the selected pen and brush, rotated if it has an angle.

        :return: The position (x, y) where the text of the element is drawn
        """
        angle = r.get('angle', 0)
        old_transform = None
        if angle != 0:
            center_of_rotation = r.get('center_of_rotation', (0, 0))
            r_angle = angle * (math.pi / 180)
            old_transform = win32gui.GetWorldTransform(hdc)
            win32gui.SetWorldTransform(hdc,
                                       {'M11': math.cos(r_angle), 'M12': math.sin(r_angle),
                                        'M21': math.sin(r_angle) * -1, 'M22': math.cos(r_angle),
                                        'Dx': x, 'Dy': y})
            x, y = -center_of_rotation[0], -center_of_rotation[1]
        try:
            if geometry is Shape.rectangle:
                win32gui.Rectangle(
                    hdc, int(round(x)), int(round(y)), int(round(x + width)), int(round(y + height)))
            elif geometry is Shape.ellipse:
                win32gui.Ellipse(hdc, int(round(x)), int(round(y)), int(round(x + width)), int(round(y + height)))
            elif geometry is Shape.arrow:
                a = thickness
                t = ((x - int(a * 1.4), y), (x - a * 4, y + a * 3), (x, y), (x - a * 4, y - a * 3),
                     (x - int(a * 1.4), y), (x - a * 9, y))
                win32gui.Polyline(hdc, t)
            elif geometry is Shape.image:
                win32gui.DrawIconEx(hdc, x, y, r['hicon'], 0, 0, 0, None, 0x0003)
            elif geometry is Shape.triangle and thickness > 0:
                # before, the outline was not shifted like the gradient when the screen does not start at (0, 0)
                t = tuple((int(round(xyrgb[0])) - self.x_min, int(round(xyrgb[1])) - self.y_min) for xyrgb in xyrgb_array)
                t = t + (t[0],)
                win32gui.Polyline(hdc, t)
        finally:
            if old_transform is not None:
                win32gui.SetWorldTransform(hdc, old_transform)
        return x, y

    def _draw_text(self, hdc, r, x, y, width, height, brush_color):
        """It draws the text of a graphical element in its rectangle."""
        lf = win32gui.LOGFONT()
        lf.lfFaceName = r.get('font_name', "Arial")
        lf.lfHeight = r.get('font_size', 18)
        lf.lfWeight = win32con.FW_NORMAL
        lf.lfQuality = win32con.ANTIALIASED_QUALITY
        font = win32gui.CreateFontIndirect(lf)
        old_font = win32gui.SelectObject(hdc, font)
        try:
            text_color = r.get('text_color', (0, 0, 0))
            win32gui.SetTextColor(hdc, win32api.RGB(text_color[0], text_color[1], text_color[2]))
            # text_bg_color has no effect: the background of the text is transparent
            text_bg_color = r.get('text_bg_color', brush_color)
            win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
            win32gui.SetBkColor(hdc, win32api.RGB(text_bg_color[0], text_bg_color[1], text_bg_color[2]))
            rectangle = (int(round(x)), int(round(y)), int(round(x + width)), int(round(y + height)))
            text_format = _text_format_flags(r.get('text_format', _DEFAULT_TEXT_FORMAT))
            win32gui.DrawTextW(hdc, r['text'], -1, rectangle, text_format)
        finally:
            win32gui.SelectObject(hdc, old_font)

    def refresh(self):
        """It redraws the overlay with its graphical elements."""
        if self.h_window is None:
            return  # before, InvalidateRect(None, ...) redrew all the windows of the screen
        try:
            win32gui.InvalidateRect(self.h_window, None, True)
        except win32gui.error:
            pass  # the window is closed

    def auto_refresh(self):
        """
        It redraws the overlay. Kept for compatibility: the overlays created with a frequency are refreshed by a timer of
        their window.
        """
        self.refresh()

    def add(self, **kwargs) -> None:
        """Add a graphical element to the overlay. It is displayed at the next refresh().

        :param geometry: The shape (Shape), or no shape to draw only a text.
        :param x, y: The position on the screen, in pixels, or as a percentage of the screen such as "50%".
        :param width, height: The size, in pixels, or as a percentage of the screen such as "25%".
        :param color: Color of the outline (r, g, b).
        :param thickness: Thickness of the shape's outline (default is 0, which means no outline).
                            Accepts int/float (pixels) or str percentage such as "1.5%".
        :param brush: Type of brush to use for filling shapes (default is solid).
        :param brush_color: Color of the brush (defaults to white, that is considered as transparent). Use
                            any RGB value other than white (255, 255, 255) to make the shape visible.
        :param angle: The angle of rotation, in degrees, around center_of_rotation (x, y), relative to (x, y).
        :param text: A text displayed in the rectangle (x, y, width, height), with text_color (r, g, b), font_name,
                            font_size and text_format: flags of DrawText such as
                            win32con.DT_LEFT | win32con.DT_WORDBREAK, or a string such as "win32con.DT_LEFT".
        :param xyrgb_array: The vertices (x, y, red, green, blue) of a triangle.
        :param hicon: The icon of an image, returned by load_ico() or load_png().
        :raises TypeError, ValueError: If the graphical element cannot be drawn.
        """
        kwargs.setdefault("brush", Brush.solid)
        kwargs.setdefault("brush_color", (255, 255, 255))
        kwargs.setdefault("thickness", 0)
        # --- convert the 5 geometrical keys -----------------------------
        for key in ('x', 'y', 'width', 'height', 'thickness'):
            if key in kwargs:
                if key in ('x', 'width'):
                    base, origin = self.screen_width, win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
                else:
                    base, origin = self.screen_height, win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
                # a position in percentage is relative to the virtual screen, which may start before (0, 0)
                kwargs[key] = self._to_pixels(kwargs[key], base, origin if key in ('x', 'y') else 0)
        # ----------------------------------------------------------------
        _check_graphical_element(kwargs)
        if "text_format" in kwargs:
            kwargs["text_format"] = _text_format_flags(kwargs["text_format"])
        with self._lock:
            self.graphical_elements.append(kwargs)

    def clear_all(self):
        """It removes all the graphical elements: they disappear at the next refresh()."""
        with self._lock:
            del self.graphical_elements[:]

    def quit(self, timeout=None):
        """
        It closes the window of the overlay and waits for the end of its thread. It can be called several times.

        :param timeout: The maximum duration of the wait, in seconds; no limit if it is None.
        """
        deadline = None if timeout is None else time.monotonic() + timeout
        self._window_created.wait(timeout)
        if self.h_window is not None and self.is_alive():
            try:
                # before, WM_QUIT was sent, and the wait never ended if the window was not created yet
                win32gui.PostMessage(self.h_window, win32con.WM_CLOSE, 0, 0)
            except win32gui.error:
                pass  # the window is already closed
        if threading.current_thread() is not self:
            self.join(None if deadline is None else max(0.0, deadline - time.monotonic()))


def load_png(filename, size_x, size_y):
    """Returns an icon, for the images of the overlays, made from a PNG file."""
    LR_DEFAULTCOLOR = 0
    with open(filename, "rb") as f:
        png = f.read()
    return CreateIconFromResourceEx(png, len(png), 1, 0x30000, size_x, size_y, LR_DEFAULTCOLOR)


def load_ico(filename, size_x, size_y):
    """Returns an icon, for the images of the overlays, made from an ICO file."""
    return win32gui.LoadImage(0, filename, win32con.IMAGE_ICON, size_x, size_y, win32con.LR_LOADFROMFILE)
