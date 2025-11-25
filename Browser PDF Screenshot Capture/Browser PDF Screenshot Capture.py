import os
import time
import pyautogui
import img2pdf
from PIL import Image

# Set up the output directory
output_dir = r"C:\Users\Sandaru\OneDrive\Desktop\ss"
os.makedirs(output_dir, exist_ok=True)

# Wait 5 seconds for user to open the browser
print("You have 5 seconds to switch to the PDF viewer in the browser...")
time.sleep(10)

# Initialize variables
total_pages = 227
screenshots = []

# Take screenshots for each page
for page in range(total_pages):
    # Take screenshot of the current screen
    screenshot = pyautogui.screenshot()
    
    # Save screenshot as PNG
    screenshot_path = os.path.join(output_dir, f"page_{page + 1}.png")
    screenshot.save(screenshot_path, "PNG")
    screenshots.append(screenshot_path)
    
    print(f"Saved screenshot for page {page + 1}/{total_pages}")
    
    # Scroll to the next page (simulate down arrow key or mouse scroll)
    pyautogui.scroll(-600)  # Adjust scroll amount if needed
    time.sleep(1)  # Wait for the page to load

# Create PDF from screenshots
pdf_path = os.path.join(output_dir, "combined_screenshots.pdf")
with open(pdf_path, "wb") as f:
    f.write(img2pdf.convert(screenshots))
print(f"PDF created at: {pdf_path}")

# Clean up individual screenshot files (optional)
for screenshot in screenshots:
    os.remove(screenshot)
print("Individual screenshots deleted.")