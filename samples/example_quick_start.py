import overlay_arrows_and_more as overlay
import time

# Create a semi-transparent overlay
my_overlay = overlay.Overlay(transparency=0.5)

# Add a red rectangle with a white background, and a text on it
my_overlay.add(
    geometry=overlay.Shape.rectangle,
    x=100, y=100,
    width=200, height=100,
    color=(255, 0, 0),
    thickness=3,
    brush=overlay.Brush.solid,
    brush_color=(255, 255, 254),  # White background: pure white (255, 255, 255) is the transparent color
    text="Hello World!",  # The background of a text is transparent: it is drawn on the rectangle
    text_color=(0, 0, 0),  # Black text
    font_size=20
)

# Refresh to display
my_overlay.refresh()

# Keep overlay visible for 5 seconds
time.sleep(5)

# Clean up
my_overlay.quit()