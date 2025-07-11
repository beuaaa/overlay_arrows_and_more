import overlay_arrows_and_more as oaam
import time

main_overlay = oaam.Overlay()
transparent_overlay = oaam.Overlay(transparency=.5)

transparent_overlay.add(geometry=oaam.Shape.rectangle, x=300, y=300, width=100, height=100, thickness=10,
                        color=(0, 255, 0))
transparent_overlay.refresh()

main_overlay.add(geometry=oaam.Shape.rectangle, x=200, y=200, width=40, height=40, color=(0, 255, 255))
main_overlay.add(geometry=oaam.Shape.rectangle, x=100, y=100, width=100, height=100, color=(0, 0, 255))
main_overlay.add(geometry=oaam.Shape.rectangle, x=300, y=100, width=100, height=100, thickness=10, color=(0, 255, 0))
main_overlay.refresh()

time.sleep(9.0)
main_overlay.clear_all()
main_overlay.refresh()
