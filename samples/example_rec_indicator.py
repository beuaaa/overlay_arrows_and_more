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
        x=55, y=50,
        width=100, height=20,
        text="REC",
        text_color=(255, 0, 0),
        text_bg_color=(255, 255, 255),
        font_size=16
    )

    rec_overlay.refresh()
    time.sleep(0.5)  # Half second intervals

rec_overlay.quit()