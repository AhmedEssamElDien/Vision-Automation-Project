import pyautogui
import cv2
import numpy as np
import os
from PIL import Image
import time

TEMPLATE_DIR = "templates"
TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "notepad_icon.png")


def capture_template():
    """Capture a region of the screen to use as a template."""
    print("Template Image Capture Tool")
    print("=" * 50)
    print("\nInstructions:")
    print("1. Position your mouse over the Notepad icon")
    print("2. This script will capture a 64x64 pixel region around your mouse")
    print("3. Adjust the size in the code if needed")
    print("\nPress Enter when ready to capture...")
    input()
    
    # Get mouse position
    x, y = pyautogui.position()
    print(f"Mouse position: ({x}, {y})")
    
    # Capture region (adjust size as needed)
    width, height = 64, 64
    left = max(0, x - width // 2)
    top = max(0, y - height // 2)
    
    print(f"Capturing {width}x{height} region...")
    time.sleep(1)
    
    # Take screenshot
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    
    # Create templates directory if it doesn't exist
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    
    # Save template
    screenshot.save(TEMPLATE_PATH)
    print(f"\nTemplate saved to: {TEMPLATE_PATH}")
    print("You can now use this template for icon detection!")


if __name__ == "__main__":
    try:
        capture_template()
    except KeyboardInterrupt:
        print("\n\nCapture cancelled by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
