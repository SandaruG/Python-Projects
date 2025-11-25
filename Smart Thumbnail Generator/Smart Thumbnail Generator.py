import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Define paths
base_image_path = r"C:New folder\Thumbnail.png"
text_dir = r"add your folderText"
output_dir = r"add your directory"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Font path (Calibri Bold for attractiveness; adjust if not available)
font_path = r"C:\Windows\Fonts\calibrib.ttf"

# Coordinates and widths for text placement
first_line_start = (540, 108)  # W540, H108
first_line_end = (1150, 108)   # W1150, H108
first_line_width = first_line_end[0] - first_line_start[0]  # 610 pixels
rest_start = (550, 200)        # W550, H200
rest_end = (1140, 200)         # W1140, H200
rest_width = rest_end[0] - rest_start[0]  # 590 pixels

# Wrap width in characters for the rest of the text
wrap_width = 15

# Line spacing for multi-line text (in pixels)
line_spacing = 10

# Function to find the bounding box of the green square area (color #9DC760) on the right side
def find_green_square(img, target_rgb=(157, 199, 96), tolerance=40):
    width, height = img.size
    pixels = img.load()
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    found_green = False
    green_pixels = []
    
    # Scan only the right half of the image
    for x in range(width // 2, width):
        for y in range(height):
            r, g, b = pixels[x, y][:3]
            if (abs(r - target_rgb[0]) <= tolerance and 
                abs(g - target_rgb[1]) <= tolerance and 
                abs(b - target_rgb[2]) <= tolerance):
                found_green = True
                green_pixels.append((x, y))
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
    
    if found_green:
        print(f"Found {len(green_pixels)} green pixels in area: ({min_x}, {min_y}, {max_x}, {max_y})")
        # Verify coordinates are within the green box
        if (first_line_start[0] >= min_x and first_line_start[0] <= max_x and
            first_line_end[0] >= min_x and first_line_end[0] <= max_x and
            first_line_start[1] >= min_y and first_line_start[1] <= max_y and
            rest_start[0] >= min_x and rest_start[0] <= max_x and
            rest_end[0] >= min_x and rest_end[0] <= max_x and
            rest_start[1] >= min_y and rest_start[1] <= max_y):
            print("Text coordinates are within the green box.")
        else:
            print("Warning: Some text coordinates are outside the green box.")
        return (min_x, min_y, max_x + 1, max_y + 1)
    else:
        print("No green square found on the right side. Possible reasons:")
        print("- The green area may not match #9DC760 (RGB: 157, 199, 96).")
        print("- The green box may not be on the right half of the image.")
        print("- Try increasing tolerance (e.g., to 50) or verify the color.")
        return None

# Function to find the largest font size that fits the text in the given width
def fit_text(draw, text, font_path, max_width, max_height, max_font_size=80, min_font_size=12, spacing=0):
    for size in range(max_font_size, min_font_size - 1, -1):
        try:
            font = ImageFont.truetype(font_path, size)
            bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center", spacing=spacing)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if w <= max_width and h <= max_height:
                return font, w, h
        except Exception as e:
            print(f"Font error at size {size}: {e}")
            continue
    # Fallback to minimum size
    try:
        font = ImageFont.truetype(font_path, min_font_size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center", spacing=spacing)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        return font, w, h
    except Exception as e:
        print(f"Failed to load font: {e}")
        return None, 0, 0

# Function to process title text
def process_title(filename):
    name = os.path.splitext(filename)[0]
    # Remove underscores and split into words
    words = name.replace('_', ' ').split()
    # Capitalize each word
    words = [word.capitalize() for word in words]
    return ' '.join(words)

# Process each txt file
for filename in os.listdir(text_dir):
    if filename.endswith(".txt"):
        # Process the title
        title = process_title(filename)
        
        # Split into first line ("Am I the A## Hole") and the rest
        first_line = "Am I the A## Hole"
        if title.lower().startswith(first_line.lower()):
            rest = title[len(first_line):].strip()
        else:
            rest = title
        
        # Wrap the rest of the text for multiple lines
        rest_lines = textwrap.wrap(rest, width=wrap_width)
        rest_text = "\n".join(rest_lines)
        
        try:
            # Open the base image
            img = Image.open(base_image_path)
        except Exception as e:
            print(f"Failed to open image {base_image_path}: {e}")
            continue
        
        # Find the green square on the right side
        green_box = find_green_square(img)
        if green_box is None:
            print(f"Skipping {filename} due to failure in finding green square.")
            continue
        
        left, top, right, bottom = green_box
        print(f"Green box dimensions: width={right - left}, height={bottom - top}")
        
        # Create draw object
        draw = ImageDraw.Draw(img)
        
        # Fit font for the first line
        font_first, text_width_first, text_height_first = fit_text(
            draw, first_line, font_path, first_line_width * 0.9, 100
        )
        if font_first is None:
            print(f"Skipping {filename} due to font loading failure for first line.")
            continue
        
        # Draw the first line at specified coordinates
        x_first = first_line_start[0] + (first_line_width - text_width_first) / 2
        y_first = first_line_start[1]
        print(f"Placing first line '{first_line}' at: x={x_first}, y={y_first}")
        draw.multiline_text((x_first, y_first), first_line, fill=(0, 0, 0), font=font_first, align="center")
        
        # Fit font for the rest of the text with line spacing
        if rest_text:
            font_rest, text_width_rest, text_height_rest = fit_text(
                draw, rest_text, font_path, rest_width * 0.9, (bottom - rest_start[1]) * 0.9, spacing=line_spacing
            )
            if font_rest is None:
                print(f"Skipping rest of text for {filename} due to font loading failure.")
            else:
                # Draw the rest of the text with line spacing
                x_rest = rest_start[0] + (rest_width - text_width_rest) / 2
                y_rest = rest_start[1]
                print(f"Placing rest text '{rest_text}' at: x={x_rest}, y={y_rest}")
                draw.multiline_text((x_rest, y_rest), rest_text, fill=(0, 0, 0), font=font_rest, align="center", spacing=line_spacing)
        
        # Save the new thumbnail
        output_path = os.path.join(output_dir, f"{title.replace(' ', '_')}.png")
        try:
            img.save(output_path)
            print(f"Saved thumbnail for {filename} at {output_path}")
        except Exception as e:
            print(f"Failed to save thumbnail for {filename}: {e}")