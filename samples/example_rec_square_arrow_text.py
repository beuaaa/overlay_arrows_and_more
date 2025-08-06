import time
from overlay_arrows_and_more import Overlay, Shape, Brush

# Create a semi-transparent overlay
overlay = Overlay(transparency=0.3)

# Example 1: Recording indicator
# Red circle and "REC" text
overlay.add(
    geometry=Shape.ellipse,
    x=50, y=50,
    width=20, height=20,
    brush=Brush.solid,
    brush_color=(255, 0, 0),  # Red
    thickness=0
)

overlay.add(
    x=80, y=50,
    width=60, height=20,
    text="REC",
    text_color=(255, 0, 0),
    text_bg_color=(0, 0, 0),
    font_size=16,
    font_name="Arial"
)

# Example 2: Important area marker
# Rectangle with green border
overlay.add(
    geometry=Shape.rectangle,
    x=300, y=200,
    width=400, height=300,
    thickness=5,
    color=(0, 255, 0),  # Green
    brush=Brush.solid,
    brush_color=(0, 255, 0, 50)  # Semi-transparent green
)

# Example 3: Directional arrow
overlay.add(
    geometry=Shape.arrow,
    x=500, y=150,
    thickness=8,
    color=(0, 0, 255),  # Blue
    angle=-90  # Points downward
)

# Example 4: Informational text
overlay.add(
    geometry=Shape.rectangle,
    x=750, y=100,
    width=300, height=100,
    thickness=2,
    color=(0, 0, 0),
    brush=Brush.solid,
    brush_color=(255, 255, 255),
    text="Important information\nPress ESC to exit",
    text_color=(0, 255, 0),
    font_size=14,
    text_format="win32con.DT_CENTER | win32con.DT_WORDBREAK | win32con.DT_VCENTER"
)

# Refresh the overlay to display elements
overlay.refresh()

# Keep the overlay visible for 10 seconds
time.sleep(10)

# Close the overlay
overlay.quit()

print("Overlay closed")
