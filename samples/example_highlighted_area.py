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

# Instruction text, in white on a black rectangle
highlight_overlay.add(
    geometry=overlay.Shape.rectangle,
    x=220, y=170,
    width=360, height=50,
    brush=overlay.Brush.solid,
    brush_color=(0, 0, 0),
    text="Click here to continue",
    text_color=(255, 255, 254),  # Pure white (255, 255, 255) is the transparent color
    font_size=18
)

highlight_overlay.refresh()
time.sleep(5)
highlight_overlay.quit()