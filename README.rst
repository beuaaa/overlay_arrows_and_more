|PyPI version| |License|

***********************
Overlay arrows and more
***********************

**WARNING:**
This library is still at an early stage of development.

Description
###########
The 'Overlay arrows and more' library displays a transparent window on top of all other windows. The transparent window serves as a support for adding graphical elements such as arrows, rectangles, circles, text, etc...

Features
********
- **Transparent overlays** that don't block underlying applications
- **Multiple shapes**: rectangles, ellipses, arrows, triangles, and images
- **Customizable styling**: colors, brushes, line thickness, fonts
- **Rotation support** for any graphical element
- **Auto-refresh** capability with configurable frequency
- **Multi-threaded** design for smooth performance
- **Multi-monitor support**
- **Context manager**: ``with Overlay() as overlay:`` closes the overlay at the end of the block

Installation
############

.. code-block:: bash

    pip install overlay_arrows_and_more

It needs Windows and Python 3.8 or later. pip also installs pywin32.


Usage
#####

This is a simple example:

.. code-block:: python

    import overlay_arrows_and_more as oaam
    import time

    main_overlay = oaam.Overlay()
    transparent_overlay = oaam.Overlay(transparency=.5)

    transparent_overlay.add(geometry=oaam.Shape.rectangle, x=300, y=300, width=100, height=100, thickness=10, color=(0, 255, 0))
    transparent_overlay.refresh()

    main_overlay.add(geometry=oaam.Shape.ellipse, x=10, y=10, width=40, height=40, thickness=1)
    main_overlay.add(geometry=oaam.Shape.rectangle, x=100, y=100, width=100, height=100, color=(0, 0, 255), thickness=5)
    main_overlay.add(geometry=oaam.Shape.rectangle, x=300, y=100, width=100, height=100, thickness=10, color=(0, 255, 0))
    main_overlay.refresh()

    time.sleep(9.0)
    main_overlay.clear_all()
    main_overlay.refresh()
    main_overlay.quit()
    transparent_overlay.quit()

The same with ``with`` statements, which close the overlays at the end of the block:

.. code-block:: python

    import overlay_arrows_and_more as oaam
    import time

    with oaam.Overlay() as main_overlay, oaam.Overlay(transparency=.5) as transparent_overlay:
        transparent_overlay.add(geometry=oaam.Shape.rectangle, x=300, y=300, width=100, height=100, thickness=10, color=(0, 255, 0))
        transparent_overlay.refresh()
        main_overlay.add(geometry=oaam.Shape.ellipse, x=10, y=10, width=40, height=40, thickness=1)
        main_overlay.refresh()
        time.sleep(9.0)

Functions
*********

Classes
=======

Overlay
-----------------


.. code-block:: python

    Overlay(transparency=0.0, frequency=None)

Main class for creating overlay windows. The window covers all the monitors; it has its own thread, and the
constructor returns when the window is created.

**Parameters:**

* ``transparency`` (float): Transparency level (0.0 = opaque, 1.0 = fully transparent)
* ``frequency`` (float): Auto-refresh frequency in Hz (optional)

**Methods:**

* ``add(**kwargs)``: Add a graphical element to the overlay. It raises ``TypeError`` or ``ValueError`` if the element
  cannot be drawn, for example an image without ``hicon``
* ``refresh()``: Update the overlay display
* ``clear_all()``: Remove all graphical elements
* ``quit(timeout=None)``: Close the overlay and wait for the end of its thread, at most ``timeout`` seconds. It can be
  called several times. ``with Overlay() as overlay:`` calls it at the end of the block

Shape (Enum)
-----------------

Available shapes for drawing:

Shape.rectangle: Rectangular shape
Shape.ellipse: Elliptical/circular shape
Shape.arrow: Arrow shape
Shape.triangle: Triangular shape
Shape.image: Image/icon

Brush (Enum)
-----------------

Fill patterns for shapes:

* ``Brush.solid``: Solid color fill
* ``Brush.b_diagonal``: 45° upward diagonal lines
* ``Brush.cross``: Horizontal and vertical crosshatch
* ``Brush.diag_cross``: 45° crosshatch
* ``Brush.f_diagonal``: 45° downward diagonal lines
* ``Brush.horizontal``: Horizontal lines
* ``Brush.vertical``: Vertical lines


Element Properties
------------------

When adding elements with ``add()``, you can use these properties:

Position and Size

* x, y: Position coordinates on the screen, in pixels, or as a percentage of the virtual screen (all the monitors),
  such as ``"50%"``

* width, height: Element dimensions, in pixels, or as a percentage of the virtual screen

Appearance

* ``color``: Outline color as RGB tuple ``(r, g, b)``
* ``thickness``: Line thickness (0 for filled shapes)
* ``brush``: Fill pattern (Brush enum)
* ``brush_color``: Fill color as RGB tuple
* ``angle``: Rotation angle in degrees
* ``center_of_rotation``: Rotation center as tuple ``(x, y)``

Text Properties

* text: Text content
* text_color: Text color as RGB tuple
* text_bg_color: No effect, kept for compatibility: the background of the texts is transparent
* font_size: Font size in pixels
* font_name: Font family name
* text_format: Text alignment flags of DrawText, such as ``win32con.DT_LEFT | win32con.DT_WORDBREAK``, or the same as a
  string: ``"win32con.DT_LEFT | win32con.DT_WORDBREAK"``

Special Properties

* ``geometry``: Shape type (Shape enum)
* ``xyrgb_array``: Vertex data for triangles
* ``hicon``: Icon handle for images

Examples
========

Recording Indicator
-------------------

.. code-block:: python

    import overlay_arrows_and_more as overlay
    import time

    # Create overlay
    rec_overlay = overlay.Overlay()

    # Blinking recording indicator
    for i in range(20):  # Blink 20 times
        rec_overlay.clear_all()

        # Show red dot on even iterations (blinking effect)
        if i % 2 == 0:
            rec_overlay.add(
                geometry=overlay.Shape.ellipse,
                x=50, y=50,
                width=20, height=20,
                brush=overlay.Brush.solid,
                brush_color=(255, 0, 0),
                thickness=0
            )

        # Recording text (always visible)
        rec_overlay.add(
            x=80, y=50,
            width=100, height=20,
            text="REC",
            text_color=(255, 0, 0),
            font_size=16
        )

        rec_overlay.refresh()
        time.sleep(0.5)  # Half second intervals

    rec_overlay.quit()

Highlighted Area
----------------

.. code-block:: python

    import overlay_arrows_and_more as overlay
    import time

    # Create transparent overlay
    highlight_overlay = overlay.Overlay(transparency=0.7)

    # Highlight rectangle
    highlight_overlay.add(
        geometry=overlay.Shape.rectangle,
        x=200, y=150,
        width=400, height=300,
        thickness=5,
        color=(0, 255, 0),
        brush=overlay.Brush.solid,
        brush_color=(0, 255, 0)
    )

    # Instruction text
    highlight_overlay.add(
        x=220, y=170,
        width=360, height=50,
        text="Click here to continue",
        text_color=(255, 255, 254),  # pure white is the transparent color
        font_size=18
    )

    highlight_overlay.refresh()
    time.sleep(5)
    highlight_overlay.quit()

Animated Elements
-----------------

.. code-block:: python

    import overlay_arrows_and_more as overlay
    import time

    # Create auto-refreshing overlay
    animated_overlay = overlay.Overlay(transparency=0.3, frequency=30)

    # Animate a rotating arrow
    for i in range(360):
        animated_overlay.clear_all()
        animated_overlay.add(
            geometry=overlay.Shape.arrow,
            x=400, y=300,
            thickness=8,
            color=(0, 0, 255),
            angle=i,
            center_of_rotation=(20, 10)
        )
        time.sleep(1/30)  # 30 FPS

    animated_overlay.quit()

Use Cases
=========

* **Screen recording tools**: Recording indicators, selection frames
* **Tutorial applications**: Highlighting UI elements, step-by-step guides
* **Presentation tools**: Annotations, pointers, emphasis
* **Gaming overlays**: Status displays, minimaps, notifications
* **Accessibility tools**: Visual indicators, screen readers
* **Development tools**: Debug information, performance metrics

Utility Functions
=================

load_png
--------

.. code-block:: python

    load_png(filename, size_x, size_y)

Load a PNG image for use in overlays.

**Parameters:**

* ``filename``: Path to PNG file
* ``size_x``, ``size_y``: Desired icon dimensions

**Returns:** Icon handle for use with ``hicon`` property

load_ico
--------

.. code-block:: python

    load_ico(filename, size_x, size_y)

Load an ICO file for use in overlays.

**Parameters:**

* ``filename``: Path to ICO file
* ``size_x``, ``size_y``: Desired icon dimensions

**Returns:** Icon handle for use with ``hicon`` property

Important Notes
===============

* This library only works on Windows systems
* Overlays are always on top of other windows
* The overlay window is transparent to mouse clicks
* Remember to call ``quit()``, or to use a ``with`` statement, to properly clean up resources
* For animated overlays, consider using the ``frequency`` parameter for smooth updates

**Color Key Warning:**

Pure white ``(255, 255, 255)`` is used as a transparency key and will be invisible. Use almost-white ``(255, 255, 254)`` or light gray ``(250, 250, 250)`` instead, either for ``color`` or ``brush_color``.





Changes
=======

0.6.0
-----

* ``quit()`` no longer blocks when it is called just after the creation of the overlay: the constructor now returns
  when the window exists. ``quit()`` accepts a ``timeout``, and an overlay can be used in a ``with`` statement
* The drawings are no longer shifted when the taskbar is at the top or on the left of the screen
* An element that cannot be drawn no longer stops the drawing of the others, and ``add()`` rejects it at once
* No more leaks of GDI objects with the texts without geometry; the rotation of such a text no longer applies to the
  next elements
* ``frequency``: the refresh no longer starts a new thread at each refresh, and it stops with ``quit()``
* ``add()`` and ``clear_all()`` can be called while the overlay is drawn; ``text_format`` accepts flags, and its strings
  are no longer evaluated by ``eval()``
* Positions in percentage are relative to the virtual screen, which may start before (0, 0) with several monitors
* The package depends on pywin32 (the package 0.5.1 had no dependency) and needs Python 3.8 or later

.. |PyPI version| image:: https://img.shields.io/pypi/v/overlay-arrows-and-more.svg
   :target: https://pypi.org/project/overlay-arrows-and-more/
.. |License| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT/
   :alt: Repository License
