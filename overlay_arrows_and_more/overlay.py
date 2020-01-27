# -*- coding: utf-8 -*-

import win32api
import win32con
import win32gui
import win32ui

from threading import Thread

from enum import Enum


class Shape(Enum):
	rectangle = 0
	arrow = 1


class TransparentWindow(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.h_window = None

	def run(self):
		h_instance = win32api.GetModuleHandle()
		class_name = 'MyWindowClassName'
		wnd_class = win32gui.WNDCLASS()

		wnd_class.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
		wnd_class.lpfnWndProc = wnd_proc
		wnd_class.hInstance = h_instance
		wnd_class.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
		wnd_class.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
		wnd_class.lpszClassName = class_name

		wnd_class_atom = win32gui.RegisterClass(wnd_class)
		ex_style = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | \
				   win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
		style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

		self.h_window = win32gui.CreateWindowEx(
			ex_style, wnd_class_atom,
			'OverlayWindow',  # WindowName
			style,
			0,  # x
			0,  # y
			win32api.GetSystemMetrics(win32con.SM_CXSCREEN),  # width
			win32api.GetSystemMetrics(win32con.SM_CYSCREEN),  # height
			None,  # hWndParent
			None,  # hMenu
			h_instance,
			None  # lpParam
		)

		win32gui.SetLayeredWindowAttributes(self.h_window, 0x00ffffff, 255, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
		win32gui.SetWindowPos(self.h_window, win32con.HWND_TOPMOST, 0, 0, 0, 0,
							  win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

		win32gui.PumpMessages()

	def refresh(self):
		win32gui.InvalidateRect(self.h_window, None, True)

	def get_rectangles(self):
		return self.rectangle_list


rectangle_list = []

def add(geometry=Shape.rectangle, x=0, y=0, width=22, height=22):
	global rectangle_list
	if geometry is Shape.rectangle:
		rectangle_list.append([x, y, width, height])

def wnd_proc(h_wnd, message, w_param, l_param):
	"""Displays a transparent window with some graphic elements

	Displays a transparent window with some graphic elements

	:param h_wnd: an input argument

	:returns: nothing
	"""
	global rectangle_list
	if message == win32con.WM_PAINT:
		hdc, paint_struct = win32gui.BeginPaint(h_wnd)

		dpi_scale = win32ui.GetDeviceCaps(hdc, win32con.LOGPIXELSX) / 60.0
		font_size = 8

		lf = win32gui.LOGFONT()
		lf.lfFaceName = "Times New Roman"
		lf.lfHeight = int(round(dpi_scale * font_size))
		hf = win32gui.CreateFontIndirect(lf)
		win32gui.SelectObject(hdc, hf)

		rect = win32gui.GetClientRect(h_wnd)
		win32gui.BringWindowToTop(h_wnd)

		try:
			pen = win32gui.CreatePen(win32con.PS_GEOMETRIC, 5, win32api.RGB(255, 0, 0))

			win32gui.SelectObject(hdc, pen)
			win32gui.Ellipse(hdc, 10, 10, 40, 40)

			for r in rectangle_list:
				win32gui.Rectangle(hdc, r[0], r[1], r[0] + r[2], r[1] + r[3])



		except:
			# exc_type, exc_value, exc_traceback = sys.exc_info()
			# print(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
			pass

		win32gui.EndPaint(h_wnd, paint_struct)
		return 0

	# elif message == win32con.WM_DESTROY:
	#	print 'Closing the window.'
	#	win32gui.PostQuitMessage(0)
	#	return 0
	else:
		return win32gui.DefWindowProc(h_wnd, message, w_param, l_param)


if __name__ == '__main__':
	transparent_window = TransparentWindow()
	transparent_window.start()
	add(geometry=Shape.rectangle, x=100, y=100, width=100, height=100)
	add(geometry=Shape.rectangle, x=300, y=100, width=100, height=100)
	transparent_window.refresh()
