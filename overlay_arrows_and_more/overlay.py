# -*- coding: utf-8 -*-

import win32api
import win32con
import win32gui
import win32ui
from threading import Thread
from threading import Lock
from enum import Enum
from datetime import datetime
from uuid import uuid4


class Shape(Enum):
	rectangle = 0
	ellipse = 1
	arrow = 2

class Brush(Enum):
	solid = 0
	b_diagonal = 1 # 45 - degree upward left - to - right hatch
	cross = 2 # Horizontal and vertical crosshatch
	diag_cross = 3 # 45 - degree crosshatch
	f_diagonal = 4 # 45 - degree downward left - to - right hatch
	horizontal = 5 # Horizontal hatch
	vertical = 6 # Vertical hatch


class Overlay(Thread):
	def __init__(self, **parameters):
		Thread.__init__(self)
		self.lock = Lock()
		self.lock2 = Lock()
		self.h_window = None
		self.graphical_elements = []
		self.class_name = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
		if 'transparency' in parameters:
			self.transparency = parameters['transparency']
		else:
			self.transparency = 255
		self.start()

	def run(self):
		def wnd_proc(h_wnd, message, w_param, l_param):
			"""Displays a transparent window with some graphic elements

			Displays a transparent window with some graphic elements

			:param h_wnd: an input argument

			:returns: nothing
			"""
			global graphical_elements

			if message == win32con.WM_PAINT:
				hdc, paint_struct = win32gui.BeginPaint(h_wnd)
				win32gui.BringWindowToTop(h_wnd)

				self.lock.acquire()
				for r in self.graphical_elements:

					if 'x' in r:
						x = r['x']
					else:
						x = 0
					if 'y' in r:
						y = r['y']
					else:
						y = 0
					if 'width' in r:
						width = r['width']
					else:
						width = 100
					if 'height' in r:
						height = r['height']
					else:
						height = 100

					if 'color' in r:
						color_r = r['color'][0]
						color_g = r['color'][1]
						color_b = r['color'][2]
					else:
						color_r = 255
						color_g = 0
						color_b = 0

					if 'thickness' in r:
						thickness = r['thickness']
					else:
						thickness = 5

					pen = win32gui.CreatePen(win32con.PS_GEOMETRIC, thickness, win32api.RGB(color_r, color_g, color_b))
					old_pen = win32gui.SelectObject(hdc, pen)

					if r['geometry'] is Shape.rectangle:
						win32gui.Rectangle(hdc, r['x'], r['y'], r['x'] + r['width'], r['y'] + r['height'])
					elif r['geometry'] is Shape.ellipse:
						win32gui.Ellipse(hdc, r['x'], r['y'], r['x'] + r['width'], r['y'] + r['height'])
					elif r['geometry'] is Shape.arrow:
						a = thickness
						t = ( (x-int(a*1.4), y), (x-a*4, y+a*3), (x,y), (x-a*4, y-a*3), (x-int(a*1.4),y), (x-a*9,y) )
						win32gui.Polyline(hdc,t)
					elif r['geometry'] is Shape.text:
						win32gui.DrawText(hdc, r['text'], )
					else:
						print('Unknown geometry of graphical element: ' + r)

					win32gui.SelectObject(hdc, old_pen)

					if 'brush_color' in r:
						brush_color_r = r['brush_color'][0]
						brush_color_g = r['brush_color'][1]
						brush_color_b = r['brush_color'][2]
					else:
						brush_color_r = 255
						brush_color_g = 0
						brush_color_b = 0

					if 'brush' in r and r['width']>1 and r['height']>1:
						brush = r['brush']
						brush_color = win32api.RGB(brush_color_r, brush_color_g, brush_color_b)
						if brush is Brush.solid:
							my_brush = win32gui.CreateSolidBrush(brush_color)
						elif brush is Brush.b_diagonal:
							my_brush = win32gui.CreateHatchBrush(win32con.HS_BDIAGONAL, brush_color)
						elif brush is Brush.cross:
							my_brush = win32gui.CreateHatchBrush(win32con.HS_CROSS, brush_color)
						elif brush is Brush.diag_cross:
							my_brush = win32gui.CreateHatchBrush(win32con.HS_DIAGCROSS, brush_color)
						elif brush is Brush.f_diagonal:
							my_brush = win32gui.CreateHatchBrush(win32con.HS_FDIAGONAL, brush_color)
						elif brush is Brush.horizontal:
							my_brush = win32gui.CreateHatchBrush(win32con.HS_HORIZONTAL, brush_color)
						elif brush is Brush.vertical:
							my_brush = win32gui.CreateHatchBrush(win32con.HS_VERTICAL, brush_color)
						old_brush = win32gui.SelectObject(hdc, my_brush)
						try:
							win32gui.ExtFloodFill(hdc, r['x'] + r['width'] / 2, r['y'] + r['height'] / 2,
											  win32api.RGB(color_r, color_g, color_b), win32con.FLOODFILLBORDER)
						except Exception:
							pass
						win32gui.SelectObject(hdc, old_brush)

					if 'text' in r:
						text = r['text']
						rect = win32gui.GetClientRect(h_wnd)
						fontSize = 18
						lf = win32gui.LOGFONT()
						lf.lfFaceName = "Arial Unicode MS"
						lf.lfHeight = fontSize
						lf.lfWeight = 600

						lf.lfQuality = win32con.ANTIALIASED_QUALITY
						hf = win32gui.CreateFontIndirect(lf)
						old_font = win32gui.SelectObject(hdc, hf)

						win32gui.SetTextColor(hdc, win32api.RGB(0, 0, 0))
						win32gui.SetBkColor(hdc, win32api.RGB(255, 0, 0))
						text_format = win32con.DT_CENTER | win32con.DT_SINGLELINE | win32con.DT_VCENTER
						tuple_r = tuple([r['x'], r['y'], r['x'] + r['width'], r['y'] + r['height']])
						win32gui.DrawTextW(hdc, text, -1, tuple_r, text_format | win32con.DT_CALCRECT)
						win32gui.DrawTextW(hdc, text, -1, tuple_r, text_format)

						win32gui.SelectObject(hdc, old_font)
				self.lock.release()
				win32gui.EndPaint(h_wnd, paint_struct)
				return 0

			# elif message == win32con.WM_DESTROY:
			#	print 'Closing the window.'
			#	win32gui.PostQuitMessage(0)
			#	return 0
			else:
				return win32gui.DefWindowProc(h_wnd, message, w_param, l_param)

		h_instance = win32api.GetModuleHandle()
		wnd_class = win32gui.WNDCLASS()
		wnd_class.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
		wnd_class.lpfnWndProc = wnd_proc
		wnd_class.hInstance = h_instance
		wnd_class.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
		wnd_class.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
		wnd_class.lpszClassName = self.class_name

		wnd_class_atom = win32gui.RegisterClass(wnd_class)
		ex_style = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | \
				   win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
		style = win32con.WS_DISABLED | win32con.WS_POPUP | win32con.WS_VISIBLE

		self.h_window = win32gui.CreateWindowEx(
			ex_style, wnd_class_atom,
			'OverlayWindow',
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

		win32gui.SetLayeredWindowAttributes(self.h_window, 0x00ffffff, self.transparency, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
		win32gui.SetWindowPos(self.h_window, win32con.HWND_TOPMOST, 0, 0, 0, 0,
							  win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

		win32gui.PumpMessages()

	def refresh(self):
		self.lock2.acquire()
		win32gui.InvalidateRect(self.h_window, None, True)
		self.lock2.release()

	def add(self, **geometry):
		self.lock2.acquire()
		self.lock.acquire()
		self.graphical_elements.append(geometry)
		self.lock.release()
		self.lock2.release()

	def clear_all(self):
		self.lock2.acquire()
		self.lock.acquire()
		del self.graphical_elements[:]
		self.lock.release()
		self.lock2.release()


if __name__ == '__main__':

	main_overlay = Overlay()
	transparent_overlay = Overlay(transparency=128)

	transparent_overlay.add(geometry=Shape.rectangle, x=300, y=300, width=100, height=100, thickness=10, color=(0, 255, 0))
	transparent_overlay.refresh()

	main_overlay.add(geometry=Shape.ellipse, x=10, y=10, width=18, height=18)
	main_overlay.add(geometry=Shape.ellipse, x=40, y=10, width=18, height=18)
	# main_overlay.add(geometry=Shape.ellipse, x=10, y=10, width=40, height=40, brush=Brush.cross, brush_color=(0, 255, 255))
	main_overlay.add(geometry=Shape.rectangle, x=100, y=100, width=300, height=100, thickness=10, color=(0, 0, 255), text=u'Il était une fois...')
	main_overlay.add(geometry=Shape.rectangle, x=500, y=100, width=300, height=100, thickness=10, color=(0, 255, 0), brush=Brush.solid, brush_color=(255,0,255), text=u'Il était deux fois...')
	main_overlay.add(geometry=Shape.rectangle, x=100, y=500, width=300, height=100, thickness=10, color=(0, 0, 255), brush = Brush.solid, brush_color = (255, 0, 255), text = u'Il était trois fois...')

	main_overlay.add(geometry=Shape.rectangle, x=201, y=423, width=6, height=1, thickness=1, color=(255, 0, 0),
					 brush = Brush.solid, brush_color = (255, 0, 255) )

	main_overlay.add(geometry=Shape.arrow, x=800, y=500, width=300, height=100, thickness=8, color=(0, 0, 255))

	main_overlay.refresh()
