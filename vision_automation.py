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

import easyocr


API_URL = "https://jsonplaceholder.typicode.com/posts"
TARGET_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "tjm-project")
TARGET_ICON_NAME = "Notepad"


if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)
    print(f"Created directory: {TARGET_DIR}")

class VisionAutomation:
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
        
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3  
        
        self.mouse_duration = 1.0  
        self.mouse_tween = pyautogui.easeInOutQuad  
    
    def move_mouse_smoothly(self, x, y):
        print(f"Moving mouse to ({x}, {y})...")
        pyautogui.moveTo(x, y, duration=self.mouse_duration, tween=self.mouse_tween)
        time.sleep(0.1)

    def get_icon_coordinates(self):
        try:
            print(f"Looking for '{TARGET_ICON_NAME}' icon...")
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            results = self.reader.readtext(screenshot_np)
            
            for (bbox, text, prob) in results:
                if TARGET_ICON_NAME.lower() in text.lower():
                    top_left = bbox[0]
                    bottom_right = bbox[2]
                    center_x = int((top_left[0] + bottom_right[0]) / 2)
                    center_y = int((top_left[1] + bottom_right[1]) / 2)
                    print(f"Found '{text}' at ({center_x}, {center_y})")
                    return center_x, center_y
            
            print(f"'{TARGET_ICON_NAME}' not found in screenshot")
            return None
            
        except Exception as e:
            print(f"Error in get_icon_coordinates: {e}")
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
                time.sleep(2)
            
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
                    time.sleep(0.2)
                
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
                time.sleep(0.2)
                
                print("Saving file (Ctrl+S)...")
                pyautogui.hotkey('ctrl', 's')
                time.sleep(2.5)  
                
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
                time.sleep(0.2)
                
                pyperclip.copy(filepath)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.8)
                
                print("Pressing Enter to save...")
                pyautogui.press('enter')
                time.sleep(2)
                
                pyautogui.press('enter')  
                time.sleep(1)
                
                print("Closing Notepad (Alt+F4)...")
                pyautogui.hotkey('alt', 'f4')
                time.sleep(1.5)
                
                pyautogui.press('n')  
                time.sleep(0.8)
                
                print(f"Successfully processed post {post['id']}")
                
            except Exception as e:
                print(f"Error processing post {post['id']}: {e}")
                try:
                    pyautogui.hotkey('alt', 'f4')
                    time.sleep(0.5)
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
        print("Starting Vision Automation Bot with Fast Clipboard Writing...")
        print("Make sure Notepad shortcut is visible on your desktop!")
        print("Press Ctrl+C to stop at any time")
        time.sleep(3)
        
        bot = VisionAutomation()
        bot.process_automation()
        
    except KeyboardInterrupt:
        print("\n\nAutomation stopped by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()