
***********************
Overlay arrays and more
***********************

**WARNING:**
This library is still at a very early stage of development.

Description
###########
The 'Overlay arrays and more' library displays a transparent window on top of all other windows. The transparent window serves as a support for adding graphical elements such as arrows, rectangles, circles, text, etc...

Installation
############
 pip install overlay_arrows_and_more


Usage
#####

This is a simple example:

.. code-block:: c

    import overlay_arrays_and_more as oaam
    import time

	main_overlay = oaam.Overlay()
	transparent_overlay = oaam.Overlay(transparency=128)

	transparent_overlay.add(geometry=oaam.Shape.rectangle, x=300, y=300, width=100, height=100, thickness=10, color=(0, 255, 0))
	transparent_overlay.refresh()

	main_overlay.add(geometry=oaam.Shape.ellipse, x=10, y=10, width=40, height=40)
	main_overlay.add(geometry=oaam.Shape.rectangle, x=100, y=100, width=100, height=100, color=(0, 0, 255))
	main_overlay.add(geometry=oaam.Shape.rectangle, x=300, y=100, width=100, height=100, thickness=10, color=(0, 255, 0))
	main_overlay.refresh()

    time.sleep(9.0)
    main_overlay.clear_all()
    main_overlay.refresh()


Functions
**********************
.. automodule:: overlay_arrows_and_more.overlay
.. autofunction:: wnd_proc

To be completed