
***********************
Overlay arrays and more
***********************

Description
###########
The 'Overlay arrays and more' library displays a transparent window on top of all other windows. The transparent window serves as a support for adding graphical elements such as arrows, rectangles, circles, text, etc...

Installation
############
 pip install overlay_arrows_and_more


Use
###

This is a simple example:

.. code-block:: c

    import overlay_arrays_and_more as oaam

    ooaam.initialize()
    ooaam.add_element(geometry=rectangle, x=0, y=0, width=20, height=20)
    ooaam.finalize()

Functions
**********************
.. automodule:: overlay_arrows_and_more.overlay
.. autofunction:: wnd_proc

To be completed