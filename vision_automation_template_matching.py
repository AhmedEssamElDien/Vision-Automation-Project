import pyautogui
import cv2
import numpy as np
import requests
import time
from PIL import Image
import os
import sys
import pygetwindow as gw
import pyperclip

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

os.environ['PYTHONIOENCODING'] = 'utf-8'


API_URL = "https://jsonplaceholder.typicode.com/posts"
TARGET_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "tjm-project")
TARGET_ICON_NAME = "Notepad"
TEMPLATE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "templates", "notepad_icon.png")
TEMPLATE_MATCH_THRESHOLD = 0.7  # Confidence threshold for template matching


if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)
    print(f"Created directory: {TARGET_DIR}")

class VisionAutomation:
    def __init__(self, template_path=None):
        self.template_path = template_path or TEMPLATE_IMAGE_PATH
        self.threshold = TEMPLATE_MATCH_THRESHOLD
        
        # Check if template image exists
        if not os.path.exists(self.template_path):
            print(f"Warning: Template image not found at {self.template_path}")
            print("Please provide a template image of the Notepad icon for template matching.")
            print("You can create one by taking a screenshot of the icon and saving it as:")
            print(f"  {self.template_path}")
        
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1  
        
        self.mouse_duration = 1.0  
        self.mouse_tween = pyautogui.easeInOutQuad  
    
    def move_mouse_smoothly(self, x, y):
        print(f"Moving mouse to ({x}, {y})...")
        pyautogui.moveTo(x, y, duration=self.mouse_duration, tween=self.mouse_tween)
        time.sleep(0.1)

    def get_icon_coordinates(self):
        try:
            print(f"Looking for '{TARGET_ICON_NAME}' icon using template matching...")
            
            # Load template image
            if not os.path.exists(self.template_path):
                print(f"Template image not found: {self.template_path}")
                return None
            
            template = cv2.imread(self.template_path, cv2.IMREAD_COLOR)
            if template is None:
                print(f"Failed to load template image: {self.template_path}")
                return None
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # Try multiscale template matching for better detection
            best_match = None
            best_confidence = 0
            best_location = None
            scales = [1.0, 0.8, 1.2, 0.6, 1.4]  # Try different scales
            
            for scale in scales:
                # Resize template
                width = int(template.shape[1] * scale)
                height = int(template.shape[0] * scale)
                
                if width < 10 or height < 10 or width > screenshot_np.shape[1] or height > screenshot_np.shape[0]:
                    continue
                
                resized_template = cv2.resize(template, (width, height))
                
                # Perform template matching
                result = cv2.matchTemplate(screenshot_np, resized_template, cv2.TM_CCOEFF_NORMED)
                
                # Find the best match
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val > best_confidence:
                    best_confidence = max_val
                    best_location = max_loc
                    best_match = resized_template
            
            if best_confidence >= self.threshold and best_location:
                # Calculate center of matched region
                template_h, template_w = best_match.shape[:2]
                center_x = best_location[0] + template_w // 2
                center_y = best_location[1] + template_h // 2
                
                print(f"Found icon at ({center_x}, {center_y}) with confidence {best_confidence:.2f}")
                return center_x, center_y
            else:
                print(f"Icon not found. Best match confidence: {best_confidence:.2f} (threshold: {self.threshold})")
                return None
            
        except Exception as e:
            print(f"Error in get_icon_coordinates: {e}")
            import traceback
            traceback.print_exc()
            return None

    def fetch_posts(self):
        try:
            print("Fetching posts from API...")
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            posts = response.json()[:10]
            print(f"Successfully fetched {len(posts)} posts from API")
            return posts, False
        except Exception as e:
            print(f"Failed to fetch from API: {e}")
            print("Using placeholder data instead...")
            
            placeholders = []
            for i in range(1, 11):
                placeholders.append({
                    "id": i,
                    "title": f"Placeholder for post {i}",
                    "body": f"This is a placeholder for post {i} because API call failed"
                })
            
            return placeholders, True

    def write_text_fast(self, text):
        print(f"Pasting {len(text)} characters using clipboard...")
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            print("Text pasted successfully!")
        except Exception as e:
            print(f"Clipboard failed: {e}, falling back to typing...")
            self.write_text_safely_backup(text)
    
    def write_text_safely_backup(self, text):
        print(f"Typing {len(text)} characters...")
        for i, char in enumerate(text):
            try:
                pyautogui.write(char, interval=0.01)  
            except:
                if char == '\n':
                    pyautogui.press('enter')
                else:
                    pyautogui.press('space')
            
            if (i + 1) % 50 == 0:
                print(f"  Typed {i + 1}/{len(text)} characters...")

    def process_automation(self):
        posts, is_fallback = self.fetch_posts()
        
        if not posts:
            print("No posts to process!")
            return
        
        if is_fallback:
            print("\n⚠️  Using placeholder data due to API failure ⚠️\n")
        
        for i, post in enumerate(posts, 1):
            print(f"\n{'='*50}")
            print(f"Processing Post {i}/{len(posts)} - ID: {post['id']}")
            print(f"{'='*50}")
            
            coords = None
            for attempt in range(3):
                print(f"Attempt {attempt + 1}/3 to find Notepad icon...")
                coords = self.get_icon_coordinates()
                if coords:
                    break
                time.sleep(1)
            
            if not coords:
                print(f"ERROR: Could not find Notepad icon after 3 attempts!")
                print("Make sure Notepad shortcut is visible on desktop")
                continue

            try:
                self.move_mouse_smoothly(coords[0], coords[1])
                
                print(f"Double-clicking at position {coords}")
                pyautogui.doubleClick()
                time.sleep(1)  
                
                print("Looking for Notepad window...")
                notepad_window = None
                for _ in range(5):  
                    windows = gw.getWindowsWithTitle('Notepad')
                    if windows:
                        notepad_window = windows[0]
                        break
                    time.sleep(0.1)
                
                if notepad_window:
                    print("Activating Notepad window...")
                    notepad_window.activate()
                    time.sleep(1)
                else:
                    print("Warning: Could not find Notepad window, proceeding anyway...")
                    time.sleep(1)

                print("Writing content...")
                content = f"Title: {post['title']}\n\n{post['body']}"
                self.write_text_fast(content)
                time.sleep(0.1)
                
                print("Saving file (Ctrl+S)...")
                pyautogui.hotkey('ctrl', 's')
                time.sleep(1)  
                
                filename = f"post_{post['id']}.txt"
                filepath = os.path.join(TARGET_DIR, filename)
                
                if os.path.exists(filepath):
                    print(f"File exists, removing: {filepath}")
                    try:
                        os.remove(filepath)
                    except:
                        pass
                
                print(f"Entering filepath: {filepath}")
                pyautogui.hotkey('ctrl', 'a')  
                time.sleep(0.1)
                
                pyperclip.copy(filepath)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.1)
                
                print("Pressing Enter to save...")
                pyautogui.press('enter')
                time.sleep(1)
                
                pyautogui.press('enter')  
                time.sleep(1)
                
                print("Closing Notepad (Alt+F4)...")
                pyautogui.hotkey('alt', 'f4')
                time.sleep(1)
                
                pyautogui.press('n')  
                time.sleep(0.1)
                
                print(f"Successfully processed post {post['id']}")
                
            except Exception as e:
                print(f"Error processing post {post['id']}: {e}")
                try:
                    pyautogui.hotkey('alt', 'f4')
                    time.sleep(0.1)
                    pyautogui.press('n')
                except:
                    pass
                continue
        
        print(f"\n{'='*50}")
        print("Automation completed!")
        print(f"Files saved to: {TARGET_DIR}")
        if is_fallback:
            print("⚠️  NOTE: Placeholder data was used due to API failure")
        print(f"{'='*50}")

if __name__ == "__main__":
    try:
        print("Starting Vision Automation Bot with Template Matching...")
        print("Make sure Notepad shortcut is visible on your desktop!")
        print("Press Ctrl+C to stop at any time")
        
        # Check if template image exists
        if not os.path.exists(TEMPLATE_IMAGE_PATH):
            print(f"\n⚠️  WARNING: Template image not found at {TEMPLATE_IMAGE_PATH}")
            print("Please create a template image of the Notepad icon.")
            print("You can:")
            print("  1. Take a screenshot of the Notepad icon")
            print("  2. Crop it to show just the icon")
            print(f"  3. Save it as '{TEMPLATE_IMAGE_PATH}'")
            print("\nProceeding anyway, but icon detection may fail...\n")
        else:
            print(f"Template image found: {TEMPLATE_IMAGE_PATH}\n")
        
        time.sleep(3)
        
        bot = VisionAutomation()
        bot.process_automation()
        
    except KeyboardInterrupt:
        print("\n\nAutomation stopped by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()