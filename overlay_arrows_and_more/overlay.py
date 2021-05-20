# -*- coding: utf-8 -*-

import win32api
import win32con
import win32gui
from threading import Timer
from threading import Thread
from enum import Enum
from datetime import datetime
from uuid import uuid4

import math

from ctypes import *
CreateIconFromResourceEx = windll.user32.CreateIconFromResourceEx


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


class Overlay(Thread):
	def __init__(self, **parameters):
		Thread.__init__(self)
		self.h_window = None
		self.graphical_elements = []
		self.class_name = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
		if 'transparency' in parameters:
			self.transparency = int(255.0*(1.0 - parameters['transparency']))
		else:
			self.transparency = 255
		self.period = 0
		if 'frequency' in parameters:
			frequency = float(parameters['frequency'])
			if frequency > 0:
				self.period = 1.0/frequency
		else:
			self.period = 0
		self.x_min = 0
		self.y_min = 0
		self.daemon = True
		self.start()

	def run(self):
		def wnd_proc(h_wnd, message, w_param, l_param):
			"""Displays a transparent window with some graphic elements
			Displays a transparent window with some graphic elements
			:param h_wnd: an input argument
			:returns: nothing
			"""
			if message == win32con.WM_QUIT:
				# print("Closing the window overlay")
				win32gui.PostQuitMessage(0)
				return 0
			
			if message == win32con.WM_PAINT:
				hdc, paint_struct = win32gui.BeginPaint(h_wnd)
				win32gui.SetGraphicsMode(hdc, win32con.GM_ADVANCED)
				win32gui.BringWindowToTop(h_wnd)

				for r in self.graphical_elements:

					if 'geometry' in r:
						geometry = r['geometry']
					else:
						geometry = None
					if 'x' in r:
						x = r['x'] - self.x_min
					else:
						x = 0
					if 'y' in r:
						y = r['y'] - self.y_min
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
					if 'xyrgb_array' in r:
						xyrgb_array = r['xyrgb_array']
					else:
						xyrgb_array = ((15, 15, 255, 0, 0), (15, 45, 0, 255, 0), (45, 30, 0, 0, 255))
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
						thickness = 0

					if 'angle' in r:
						angle = r['angle']
					else:
						angle = 0

					if 'geometry' in r and r['geometry'] is Shape.triangle:
						vertices = ()
						for xyrgb in xyrgb_array:
							vertices = vertices + ({'x': int(round(xyrgb[0])) - self.x_min,
							                        'y': int(round(xyrgb[1])) - self.y_min,
													'Red': xyrgb[2] * 256,
													'Green': xyrgb[3] * 256,
													'Blue': xyrgb[4] * 256,
													'Alpha': 0},)
						mesh = ((0, 1, 2),)
						win32gui.GradientFill(hdc, vertices, mesh, win32con.GRADIENT_FILL_TRIANGLE)

					if 'brush_color' in r:
						brush_color_r = r['brush_color'][0]
						brush_color_g = r['brush_color'][1]
						brush_color_b = r['brush_color'][2]
					else:
						brush_color_r = 255
						brush_color_g = 255
						brush_color_b = 255

					if thickness == 0:
						color_r = brush_color_r
						color_g = brush_color_g
						color_b = brush_color_b

					if 'font_size' in r:
						font_size = r['font_size']
					else:
						font_size = 18

					if 'font_name' in r:
						font_name = r['font_name']
					else:
						font_name = "Arial"

					my_brush = None
					if 'brush' in r and width > 1 and height > 1:
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
					pen = win32gui.CreatePen(win32con.PS_GEOMETRIC, thickness, win32api.RGB(color_r, color_g, color_b))
					old_pen = win32gui.SelectObject(hdc, pen)

					if 'center_of_rotation' in r:
						center_of_rotation_x = r['center_of_rotation'][0]
						center_of_rotation_y = r['center_of_rotation'][1]
					else:
						center_of_rotation_x = 0
						center_of_rotation_y = 0

					if angle != 0:
						r_angle = angle * (math.pi / 180)
						Py_XFORM = win32gui.GetWorldTransform(hdc)
						win32gui.SetWorldTransform(hdc,
												   {'M11': math.cos(r_angle), 'M12': math.sin(r_angle),
													'M21': math.sin(r_angle) * -1, 'M22': math.cos(r_angle),
													'Dx': x, 'Dy': y})
						x, y = -center_of_rotation_x, -center_of_rotation_y
					
					if 'text_format' in r:
						text_format = eval(r['text_format'])
					else:
						text_format = win32con.DT_CENTER | win32con.DT_SINGLELINE | win32con.DT_VCENTER
						
					if 'geometry' in r:
						if r['geometry'] is Shape.rectangle:
							win32gui.Rectangle(
								hdc, int(round(x)), int(round(y)), int(round(x + width)), int(round(y + height)))
						elif r['geometry'] is Shape.ellipse:
							win32gui.Ellipse(hdc, int(round(x)), int(round(y)), int(round(x + width)), int(round(y + height)))
						elif r['geometry'] is Shape.arrow:
							a = thickness
							t = ((x - int(a * 1.4), y), (x - a * 4, y + a * 3), (x, y), (x - a * 4, y - a * 3),
								 (x - int(a * 1.4), y), (x - a * 9, y))
							win32gui.Polyline(hdc, t)
						elif r['geometry'] is Shape.image:
							hicon = r['hicon']
							win32gui.DrawIconEx(hdc, x, y, hicon, 0, 0, 0, None, 0x0003)
						elif r['geometry'] is Shape.triangle and thickness > 0:
							t = ()
							for xyrgb in xyrgb_array:
								t = t + ((int(round(xyrgb[0])), + int(round(xyrgb[1]))),)
							t = t + ((int(round(xyrgb_array[0][0])), int(round(xyrgb_array[0][1]))),)
							win32gui.Polyline(hdc, t)
						if angle != 0:
							win32gui.SetWorldTransform(hdc, Py_XFORM)
						win32gui.SelectObject(hdc, old_pen)

					if 'brush' in r and width > 1 and height > 1:
						win32gui.SelectObject(hdc, old_brush)

					if 'text' in r:
						text = r['text']
						lf = win32gui.LOGFONT()
						lf.lfFaceName = font_name
						lf.lfHeight = font_size
						lf.lfWeight = win32con.FW_NORMAL
						lf.lfQuality = win32con.ANTIALIASED_QUALITY
						hf = win32gui.CreateFontIndirect(lf)
						old_font = win32gui.SelectObject(hdc, hf)

						if 'text_color' in r:
							text_color_r = r['text_color'][0]
							text_color_g = r['text_color'][1]
							text_color_b = r['text_color'][2]
						else:
							text_color_r = 0
							text_color_g = 0
							text_color_b = 0
						win32gui.SetTextColor(hdc, win32api.RGB(text_color_r, text_color_g, text_color_b))

						if 'text_bg_color' in r:
							text_bg_color_r = r['text_bg_color'][0]
							text_bg_color_g = r['text_bg_color'][1]
							text_bg_color_b = r['text_bg_color'][2]
						else:
							text_bg_color_r = brush_color_r
							text_bg_color_g = brush_color_g
							text_bg_color_b = brush_color_b
						win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
						win32gui.SetBkColor(hdc, win32api.RGB(text_bg_color_r, text_bg_color_g, text_bg_color_b))
						tuple_r = tuple([int(round(x)), int(round(y)), int(round(x + width)), int(round(y + height))])
						win32gui.DrawTextW(hdc, text, -1, tuple_r, text_format)
						win32gui.SelectObject(hdc, old_font)
				win32gui.EndPaint(h_wnd, paint_struct)
				return 0
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
			win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN),  # x
			win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN),  # y
			win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN),  # width
			win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN),  # height
			None,  # hWndParent
			None,  # hMenu
			h_instance,
			None  # lpParam
		)
		monitors = win32api.EnumDisplayMonitors()
		self.x_min = min([win32api.GetMonitorInfo(monitor[0])['Work'][0] for monitor in monitors])
		self.y_min = min([win32api.GetMonitorInfo(monitor[0])['Work'][1] for monitor in monitors])
		win32gui.SetLayeredWindowAttributes(self.h_window, 0x00ffffff, self.transparency,
											win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
		win32gui.SetWindowPos(self.h_window, win32con.HWND_TOPMOST, 0, 0, 0, 0,
							  win32con.SWP_NOACTIVATE | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

		if self.period > 0:
			self.auto_refresh()
		#print("PumpMessages start")
		win32gui.PumpMessages()
		#print("Overlay quit")

	def refresh(self):
		win32gui.InvalidateRect(self.h_window, None, True)

	def auto_refresh(self):
		self.refresh()
		Timer(self.period, self.auto_refresh).start()

	def add(self, **geometry):
		self.graphical_elements.append(geometry)

	def clear_all(self):
		del self.graphical_elements[:]
		
	def quit(self):
		win32gui.SendMessage(self.h_window, win32con.WM_QUIT, 0, 0)
		self.join()


def load_png(filename, size_x, size_y):
	LR_DEFAULTCOLOR = 0
	with open(filename, "rb") as f:
		png = f.read()
	return CreateIconFromResourceEx(png, len(png), 1, 0x30000, size_x, size_y, LR_DEFAULTCOLOR)


def load_ico(filename, size_x, size_y):
	return win32gui.LoadImage(0, filename, win32con.IMAGE_ICON, size_x, size_y, win32con.LR_LOADFROMFILE)


if __name__ == '__main__':
	import time

	main_overlay = Overlay()
	transparent_overlay = Overlay(transparency=0.5)

	transparent_overlay.add(geometry=Shape.rectangle, x=300, y=800, width=100, height=1000, thickness=10,
							color=(0, 255, 0))
	transparent_overlay.refresh()

	main_overlay.add(x=60, y=10, width=98, height=20, text_bg_color=(255, 255, 254), text_color=(255, 0, 0),
					 text='Recording...')

	main_overlay.add(geometry=Shape.ellipse, x=10, y=10, width=18, height=18)
	main_overlay.add(geometry=Shape.ellipse, x=40, y=10, width=18, height=18)



	main_overlay.add(geometry=Shape.rectangle, x=100, y=100, width=300, height=100, thickness=10, color=(0, 0, 255),
					 text_color=(255, 255, 254), text=u'Il était une fois...')

	main_overlay.add(geometry=Shape.triangle, thickness=0,
					 xyrgb_array=((815, 150, 255, 0, 0), (1400, 150, 0, 255, 0), (1400, 800, 0, 0, 255)),
					 )

	main_overlay.add(geometry=Shape.rectangle, x=1200, y=300, width=400, height=0, thickness=10, color=(0, 0, 255),
					 text_color=(255, 255, 254),
					 text=u'Pywinauto recorder 0.1.0 blabla blabla blabla blabla blabla blabla xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx\n aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa\n aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa\n aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa',
					 # text_format="win32con.DT_CENTER | win32con.DT_NOCLIP | win32con.DT_VCENTER",
					 text_format="win32con.DT_LEFT | win32con.DT_TOP | win32con.DT_WORDBREAK | win32con.DT_WORD_ELLIPSIS | win32con.DT_NOCLIP",
					 font_size=40)



	main_overlay.add(geometry=Shape.rectangle, x=500, y=100, width=300, height=100, thickness=10, color=(0, 255, 0),
					 brush=Brush.solid, brush_color=(255, 0, 255), text=u'Il était deux fois...')

	main_overlay.add(geometry=Shape.rectangle, x=201, y=423, width=6, height=1, thickness=1, color=(255, 0, 0),
					 brush=Brush.solid, brush_color=(255, 0, 255))


	main_overlay.add(geometry=Shape.rectangle, x=800, y=500, width=300, height=100, thickness=8, color=(0, 255, 0), angle=45)
	main_overlay.add(geometry=Shape.arrow, x=800, y=500, thickness=8, color=(0, 0, 255), angle=-180)

	main_overlay.add( geometry=Shape.rectangle, x=10, y=10, width=40, height=40,
		color=(0, 0, 0), thickness=1, brush=Brush.solid, brush_color=(255, 255, 254))

	main_overlay.add(geometry=Shape.triangle, thickness=0, color=(0,0,0),
					 xyrgb_array=((15, 15, 255, 0, 0), (15, 45, 0, 255, 0), (45, 30, 0, 0, 255)))

	main_overlay.add(geometry=Shape.ellipse, x=10, y=800, width=40, height=40,
					 color=(255, 0, 0), thickness=2, brush=Brush.solid, brush_color=(255, 255, 254))
	

	
	main_overlay.refresh()
	time.sleep(2)
	transparent_overlay.quit()
	main_overlay.quit()

	
	hicon = load_ico(r'C:\Users\oktalse\PycharmProjects\pywinauto_recorder\pywinauto_recorder\Icons\play.ico', 48, 48)


	time.sleep(1)
	animated_overlay = Overlay(transparency=0.5, frequency=25.)
	animated_overlay.refresh()
	

	
	x, y = 350, 600
	a = 0.0
	for i in range(100):
		animated_overlay.clear_all()
		animated_overlay.add(geometry=Shape.image, hicon=hicon, x=120, y=700)
		animated_overlay.add(geometry=Shape.image, hicon=hicon, x=x, y=y, angle=a, center_of_rotation=(20, 20))
		animated_overlay.add(geometry=Shape.arrow, x=x, y=y, thickness=7, color=(0, 0, 255))
		x += 1
		a += 0.9
		time.sleep(1./25.)


	
	animated_overlay.quit()
