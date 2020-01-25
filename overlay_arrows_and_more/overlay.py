# -*- coding: utf-8 -*-

import win32api, win32con, win32gui, win32ui


def wnd_proc(h_wnd, message, w_param, l_param):
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
	h_instance = win32api.GetModuleHandle()
	className = 'MyWindowClassName'
	wndClass = win32gui.WNDCLASS()

	wndClass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
	wndClass.lpfnWndProc = wnd_proc
	wndClass.hInstance = h_instance
	wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
	wndClass.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
	wndClass.lpszClassName = className

	wndClassAtom = win32gui.RegisterClass(wndClass)
	exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
	style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

	h_window = win32gui.CreateWindowEx(
		exStyle, wndClassAtom,
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

	win32gui.SetLayeredWindowAttributes(h_window, 0x00ffffff, 255, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
	win32gui.SetWindowPos(h_window, win32con.HWND_TOPMOST, 0, 0, 0, 0,
						  win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

	win32gui.PumpMessages()
