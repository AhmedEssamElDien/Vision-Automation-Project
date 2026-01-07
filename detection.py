import pyautogui
import cv2
import numpy as np
import time
import os
import sys

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

os.environ['PYTHONIOENCODING'] = 'utf-8'

import easyocr


TARGET_DIR = r"D:\Work\Projects\notepad_icon_detection"
DEBUG_DIR = TARGET_DIR
TARGET_ICON_NAME = "Notepad"


if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)
    print(f"Created directory: {TARGET_DIR}")

if not os.path.exists(DEBUG_DIR):
    os.makedirs(DEBUG_DIR)
    print(f"Created debug directory: {DEBUG_DIR}")

class IconDetector:
    def __init__(self):
        print("Initializing EasyOCR (this may take a moment)...")
        print("If download fails, the script will retry automatically...")
        try:
            self.reader = easyocr.Reader(
                ['en'], 
                verbose=False, 
                gpu=False,
                download_enabled=True,
                model_storage_directory=os.path.join(os.path.expanduser("~"), ".EasyOCR", "model")
            )
            print("EasyOCR initialized successfully!")
        except Exception as e:
            print(f"Error initializing EasyOCR: {e}")
            print("\nTroubleshooting:")
            print("1. Check your internet connection")
            print("2. Try running the script again")
            print("3. Or download models manually from:")
            print("   https://www.jaided.ai/easyocr/modelhub/")
            raise

    def save_debug_image(self, screenshot_np, bbox, center_x, center_y, text, prob):
        debug_img = screenshot_np.copy()
        
        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))
        
        icon_width = bottom_right[0] - top_left[0]
        icon_height = bottom_right[1] - top_left[1]
        radius = int(max(icon_width, icon_height) * 0.8)
        
        cv2.circle(debug_img, (center_x, center_y), radius, (0, 255, 0), 4)
        
        arrow_start_x = center_x + int(radius * 1.5)
        arrow_start_y = center_y - int(radius * 1.5)
        arrow_end_x = center_x + int(radius * 0.3)
        arrow_end_y = center_y - int(radius * 0.3)
        
        cv2.arrowedLine(debug_img, 
                       (arrow_start_x, arrow_start_y),
                       (arrow_end_x, arrow_end_y),
                       (0, 255, 0), 4, tipLength=0.3)
        
        coords_text = f"Icon Detected: ({center_x}, {center_y})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 3
        
        text_x = arrow_start_x + 20
        text_y = arrow_start_y - 10
        
        cv2.putText(debug_img, coords_text, (text_x, text_y),
                   font, font_scale, (0, 255, 0), thickness, cv2.LINE_AA)
        
        success_text = "SUCCESS"
        success_font_scale = 2.5
        success_thickness = 5
        
        (success_width, success_height), _ = cv2.getTextSize(success_text, font, success_font_scale, success_thickness)
        
        success_x = center_x - success_width // 2
        success_y = center_y + radius + success_height + 30
        
        cv2.putText(debug_img, success_text, (success_x, success_y),
                   font, success_font_scale, (0, 255, 0), success_thickness, cv2.LINE_AA)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        debug_filename = f"detection_{timestamp}.png"
        debug_path = os.path.join(DEBUG_DIR, debug_filename)
        
        cv2.imwrite(debug_path, debug_img)
        print(f"✅ Debug image saved: {debug_path}")
        print(f"   Icon: '{text}' | Confidence: {prob:.2f} | Center: ({center_x}, {center_y})")
        
        return debug_path

    def detect_icon(self):
        try:
            print(f"\nTaking screenshot and looking for '{TARGET_ICON_NAME}' icon...")
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            print("Running OCR to detect text...")
            results = self.reader.readtext(screenshot_np)
            
            for (bbox, text, prob) in results:
                if TARGET_ICON_NAME.lower() in text.lower():
                    top_left = bbox[0]
                    bottom_right = bbox[2]
                    center_x = int((top_left[0] + bottom_right[0]) / 2)
                    center_y = int((top_left[1] + bottom_right[1]) / 2)
                    
                    print(f"\n✅ SUCCESS! Found '{text}' at ({center_x}, {center_y})")
                    print(f"   Confidence: {prob:.2f}")
                    
                    self.save_debug_image(screenshot_np, bbox, center_x, center_y, text, prob)
                    
                    return True
            
            print(f"\n❌ '{TARGET_ICON_NAME}' not found in screenshot")
            
            no_match_timestamp = time.strftime("%Y%m%d_%H%M%S")
            no_match_filename = f"NO_MATCH_{no_match_timestamp}.png"
            no_match_path = os.path.join(DEBUG_DIR, no_match_filename)
            cv2.imwrite(no_match_path, screenshot_np)
            print(f"⚠️  Screenshot saved (no match found): {no_match_path}")
            
            return False
            
        except Exception as e:
            print(f"\n❌ Error in detect_icon: {e}")
            return False

if __name__ == "__main__":
    try:
        print("="*60)
        print("Icon Detection Tool - Single Run Mode")
        print("="*60)
        print(f"Target icon: {TARGET_ICON_NAME}")
        print(f"Images will be saved to: {DEBUG_DIR}")
        print("Make sure the icon is visible on your desktop!")
        print("="*60)
        
        print("\nStarting in 5 seconds...")
        for i in range(5, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("\n🚀 Starting detection now!")
        print("="*60)
        
        detector = IconDetector()
        success = detector.detect_icon()
        
        print("\n" + "="*60)
        if success:
            print("✅ Detection completed successfully!")
        else:
            print("❌ Detection failed - icon not found")
        print(f"📁 Check images in: {DEBUG_DIR}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n❌ Detection stopped by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()