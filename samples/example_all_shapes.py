"""
All the shapes, with texts, rotations, brushes and an animation.

Before version 0.6.0, this example was at the end of overlay_arrows_and_more/overlay.py.
"""
import time

import win32con
import win32gui

import overlay_arrows_and_more as oaam

with oaam.Overlay() as main_overlay, oaam.Overlay(transparency=0.5) as transparent_overlay:
    transparent_overlay.add(geometry=oaam.Shape.rectangle, x=300, y=800, width=100, height=1000, thickness=10,
                            color=(0, 255, 0))
    transparent_overlay.refresh()

    main_overlay.add(x=60, y=10, width=98, height=20, text_color=(255, 0, 0), text='Recording...')
    main_overlay.add(geometry=oaam.Shape.ellipse, x=10, y=10, width=18, height=18)
    main_overlay.add(geometry=oaam.Shape.ellipse, x=40, y=10, width=18, height=18)
    main_overlay.add(geometry=oaam.Shape.rectangle, x=100, y=100, width=300, height=100, thickness=10,
                     color=(0, 0, 255), text_color=(255, 255, 254), text=u'Il était une fois...')
    main_overlay.add(geometry=oaam.Shape.triangle, thickness=0,
                     xyrgb_array=((815, 150, 255, 0, 0), (1400, 150, 0, 255, 0), (1400, 800, 0, 0, 255)))
    main_overlay.add(geometry=oaam.Shape.rectangle, x=1200, y=300, width=400, height=0, thickness=10,
                     color=(0, 0, 255), text_color=(255, 255, 254),
                     text=u'Pywinauto recorder 0.1.0 blabla blabla blabla blabla blabla blabla xxx xxx xxx xxx xxx\n'
                          u' aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa\n aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa aaaaaaaa',
                     text_format=win32con.DT_LEFT | win32con.DT_TOP | win32con.DT_WORDBREAK | win32con.DT_WORD_ELLIPSIS |
                     win32con.DT_NOCLIP,
                     font_size=40)
    main_overlay.add(geometry=oaam.Shape.rectangle, x=100, y="50%", width=300, height=100, thickness=10,
                     color=(0, 255, 0), brush=oaam.Brush.solid, brush_color=(255, 0, 255), text=u'Il était deux fois...')
    main_overlay.add(geometry=oaam.Shape.rectangle, x=201, y=423, width=6, height=1, thickness=1, color=(255, 0, 0),
                     brush=oaam.Brush.solid, brush_color=(255, 0, 255))
    main_overlay.add(geometry=oaam.Shape.rectangle, x=800, y=500, width=300, height=100, thickness=8,
                     color=(0, 255, 0), angle=45)
    main_overlay.add(geometry=oaam.Shape.arrow, x=800, y=500, thickness=8, color=(0, 0, 255), angle=-180)
    main_overlay.add(geometry=oaam.Shape.rectangle, x=10, y=10, width=40, height=40,
                     color=(0, 0, 0), thickness=1, brush=oaam.Brush.solid, brush_color=(255, 255, 254))
    main_overlay.add(geometry=oaam.Shape.triangle, thickness=0, color=(0, 0, 0),
                     xyrgb_array=((15, 15, 255, 0, 0), (15, 45, 0, 255, 0), (45, 30, 0, 0, 255)))
    main_overlay.add(geometry=oaam.Shape.ellipse, x=10, y=800, width=40, height=40,
                     color=(255, 0, 0), thickness=2, brush=oaam.Brush.solid, brush_color=(255, 255, 254))
    main_overlay.refresh()
    time.sleep(2)

hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
with oaam.Overlay(transparency=0.5, frequency=25.) as animated_overlay:
    x, y = 350, 600
    a = 0.0
    for i in range(100):
        animated_overlay.clear_all()
        animated_overlay.add(geometry=oaam.Shape.image, hicon=hicon, x=120, y=700)
        animated_overlay.add(geometry=oaam.Shape.image, hicon=hicon, x=x, y=y, angle=a, center_of_rotation=(20, 20))
        animated_overlay.add(geometry=oaam.Shape.arrow, x=x, y=y, thickness=7, color=(0, 0, 255))
        x += 1
        a += 0.9
        time.sleep(1. / 25.)
