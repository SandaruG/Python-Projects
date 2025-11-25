import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Define paths
base_image_path = r"....Thumbnail.png"
text_file_path = r"....txt_file_names.txt"
output_dir = r"folder"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Font paths (primary and fallback)
font_paths = [
    r"C:\Windows\Fonts\segoepr.ttf", 
    r"C:\Windows\Fonts\calibril.ttf",      
    r"C:\Windows\Fonts\CascadiaCode.ttf" 
]

# Coordinates and widths for text placement (adjusted to fit within green box: 640, 24, 1242, 702)
first_line_start = (230, 100)  # Adjusted to be within x=640-1242, y=24-702
first_line_end = (1030, 100)   # Adjusted to be within x=640-1242
first_line_width = first_line_end[0] - first_line_start[0]  # 580 pixels
rest_start = (250, 200)        # Adjusted to be within x=640-1242
rest_end = (1020, 200)         # Adjusted to be within x=640-1242
rest_width = rest_end[0] - rest_start[0]  # 560 pixels

# Wrap width in characters for the rest of the text
wrap_width = 15

# Line spacing for multi-line text (in pixels)
line_spacing = 18

# Function to try loading fonts from a list
def load_font(font_paths, size):
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"Failed to load font {font_path}: {e}")
            continue
    return None

# Modified fit_text to use multiple font paths
def fit_text_with_fallback(draw, text, font_paths, max_width, max_height, max_font_size=80, min_font_size=40, spacing=10):
    for size in range(max_font_size, min_font_size - 1, -1):
        font = load_font(font_paths, size)
        if font:
            try:
                bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center", spacing=spacing)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                if w <= max_width and h <= max_height:
                    return font, w, h
            except Exception as e:
                print(f"Error rendering text at size {size}: {e}")
                continue
    # Fallback to minimum size
    font = load_font(font_paths, min_font_size)
    if font:
        try:
            bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center", spacing=spacing)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            return font, w, h
        except Exception as e:
            print(f"Failed to load font at minimum size: {e}")
    return None, 0, 0

# Function to draw text with outline and shine effect
def draw_text_with_outline(draw, position, text, font, text_color=(255, 255, 255), outline_color=(0, 0, 0), align="center", spacing=0):
    x, y = position
    # Draw outline by offsetting text in multiple directions
    outline_offset = 2
    for dx in [-outline_offset, outline_offset]:
        for dy in [-outline_offset, outline_offset]:
            draw.multiline_text((x + dx, y + dy), text, fill=outline_color, font=font, align=align, spacing=spacing)
    # Draw main text
    draw.multiline_text((x, y), text, fill=text_color, font=font, align=align, spacing=spacing)

# Read the text file with windows-1252 encoding
try:
    with open(text_file_path, 'r', encoding='windows-1252') as f:
        lines = f.readlines()
except Exception as e:
    print(f"Failed to read {text_file_path}: {e}")
    exit()

# Process each line in the text file
for line in lines:
    line = line.strip()
    if not line:
        continue
    # Split the line into text and filename
    try:
        text_part, filename_part = line.split(" - ", 1)
        text_part = text_part.strip()
        filename_part = filename_part.strip()
    except ValueError:
        print(f"Skipping line due to incorrect format: {line}")
        continue
    # Ensure filename is safe for saving
    filename_clean = filename_part.replace(" ", "_").replace("?", "").replace("!", "").replace("'", "").replace(":", "")
    
    # Split into first line ("Am I the A## Hole") and the rest
    first_line = "Am I the A## Hole"
    rest = text_part
    # Wrap the rest of the text for multiple lines
    rest_lines = textwrap.wrap(rest, width=wrap_width)
    rest_text = "\n".join(rest_lines)
    try:
        # Open the base image
        img = Image.open(base_image_path)
    except Exception as e:
        print(f"Failed to open image {base_image_path} for {line}: {e}")
        continue
    # Create draw object
    draw = ImageDraw.Draw(img)
    # Fit font for the first line
    font_first, text_width_first, text_height_first = fit_text_with_fallback(
        draw, first_line, font_paths, first_line_width * 0.9, 100, max_font_size=60, min_font_size=40
    )
    if font_first is None:
        print(f"Skipping {line} due to font loading failure for first line.")
        continue
    # Draw the first line with outline and shine
    x_first = first_line_start[0] + (first_line_width - text_width_first) / 2
    y_first = first_line_start[1]
    print(f"Placing first line '{first_line}' at: x={x_first}, y={y_first}")
    draw_text_with_outline(draw, (x_first, y_first), first_line, font_first, text_color=(57, 255, 20), outline_color=(0, 0, 0), align="center")
    # Fit font for the rest of the text with line spacing, increased font size
    if rest_text:
        font_rest, text_width_rest, text_height_rest = fit_text_with_fallback(
            draw, rest_text, font_paths, rest_width * 0.9, 500, max_font_size=100, min_font_size=90, spacing=line_spacing
        )
        if font_rest is None:
            print(f"Skipping rest of text for {line} due to font loading failure.")
        else:
            # Draw the rest of the text with outline and shine
            x_rest = rest_start[0] + (rest_width - text_width_rest) / 2
            y_rest = rest_start[1]
            print(f"Placing rest text '{rest_text}' at: x={x_rest}, y={y_rest}")
            draw_text_with_outline(draw, (x_rest, y_rest), rest_text, font_rest, text_color=(255, 117, 24), outline_color=(0, 0, 0), align="center", spacing=line_spacing)
    # Save the new thumbnail
    output_path = os.path.join(output_dir, f"{filename_clean}.png")
    try:
        img.save(output_path)
        print(f"Saved thumbnail for {line} at {output_path}")
    except Exception as e:
        print(f"Failed to save thumbnail for {line}: {e}")