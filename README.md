# Vision Automation

A Python-based desktop automation bot that uses computer vision (OCR) to locate desktop icons and automate tasks. This project fetches posts from an API and automatically saves them as text files using Notepad.

## Features

- 🔍 **Icon Detection**: Uses EasyOCR to find desktop icons by text recognition
- 📝 **Automated File Creation**: Automatically creates and saves text files
- 📋 **Fast Clipboard Operations**: Uses pyperclip for efficient text pasting
- 🖱️ **Smooth Mouse Movements**: Animated mouse movements for better visibility
- 🔄 **Error Handling**: Fallback mechanisms for API failures and OCR errors
- ⚡ **Retry Logic**: Automatic retries for icon detection

## Requirements

- Python 3.8 or higher
- Windows OS (tested on Windows 10/11)
- Notepad shortcut visible on desktop
- Internet connection (for API calls and EasyOCR model download)

## Installation

### Using uv (Recommended)

```bash
# Install uv if you haven't already
# Visit: https://github.com/astral-sh/uv

# Install dependencies
uv sync

# Run the script
uv run vision_automation.py
```

### Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Or install from pyproject.toml
pip install -e .
```

## Dependencies

- `pyautogui` - GUI automation
- `opencv-python` - Image processing
- `numpy` - Numerical operations
- `requests` - HTTP requests
- `Pillow` - Image handling
- `pygetwindow` - Window management
- `pyperclip` - Clipboard operations
- `easyocr` - OCR for icon detection

## Usage

1. **Prepare your desktop**: Make sure the Notepad shortcut is visible on your desktop

2. **Run the script**:
   ```bash
   python vision_automation.py
   ```

3. **Wait for initialization**: EasyOCR will download models on first run (this may take a few minutes)

4. **Let it run**: The bot will:
   - Fetch posts from the API
   - Find the Notepad icon on your desktop
   - Open Notepad for each post
   - Write the post content
   - Save files to `~/Desktop/tjm-project/`

## Configuration

You can modify these constants in `vision_automation.py`:

```python
API_URL = "https://jsonplaceholder.typicode.com/posts"
TARGET_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "tjm-project")
TARGET_ICON_NAME = "Notepad"
```

## How It Works

1. **Initialization**: Loads EasyOCR model for text recognition
2. **API Fetching**: Retrieves posts from the configured API endpoint
3. **Icon Detection**: Takes screenshots and uses OCR to find the Notepad icon
4. **Automation**: For each post:
   - Locates and clicks the Notepad icon
   - Opens Notepad window
   - Writes post content using clipboard
   - Saves file with proper naming
   - Closes Notepad

## Output

Files are saved to: `~/Desktop/tjm-project/post_{id}.txt`

Each file contains:
```
Title: {post_title}

{post_body}
```

## Troubleshooting

### EasyOCR Download Issues
- Check your internet connection
- The script will retry automatically
- Models are cached after first download

### Icon Not Found
- Ensure Notepad shortcut is visible on desktop
- Make sure the icon text is clearly readable
- Try adjusting desktop resolution or icon size

### API Failures
- The script will use placeholder data if API fails
- Check your internet connection
- Verify the API URL is accessible

## Safety Features

- **Failsafe**: Move mouse to top-left corner to stop automation
- **Error Recovery**: Continues processing even if one post fails
- **Window Management**: Properly handles Notepad window activation

## License

This project is open source and available for personal and educational use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Notes

- First run will download EasyOCR models (~100MB)
- The script requires desktop access and will control your mouse/keyboard
- Press `Ctrl+C` to stop the automation at any time
- Files are saved to your Desktop by default
