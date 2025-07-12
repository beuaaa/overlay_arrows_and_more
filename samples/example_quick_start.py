import overlay_arrows_and_more as overlay
import time

# Create a semi-transparent overlay
my_overlay = overlay.Overlay(transparency=0.5)

# Add a red rectangle with background
my_overlay.add(
    geometry=overlay.Shape.rectangle,
    x=100, y=100,
    width=200, height=100,
    color=(255, 0, 0),
    thickness=3,
    brush=overlay.Brush.solid,
    brush_color=(255, 255, 255)  # White background for text visibility
)

# Add text with proper background
my_overlay.add(
    x=110, y=120,
    width=180, height=60,
    text="Hello World!",
    text_color=(0, 0, 0),  # Black text
    text_bg_color=(255, 255, 255),  # White background
    font_size=20
)

# Refresh to display
my_overlay.refresh()

# Keep overlay visible for 5 seconds
time.sleep(5)

# Clean up
my_overlay.quit()