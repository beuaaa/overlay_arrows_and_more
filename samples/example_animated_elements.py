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