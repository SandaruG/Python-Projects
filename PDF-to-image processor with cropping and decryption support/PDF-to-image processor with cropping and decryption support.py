import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

# Define input and output directories
input_dir = r"INput Folder"
output_dir = r"Output Folder"
password = "Password"
poppler_path = r"Path"

# Verify script is running from the correct directory
if not os.path.exists(input_dir):
    raise FileNotFoundError(f"Input directory {input_dir} does not exist. Ensure the script is run from the correct location.")

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Verify poppler path
if not os.path.exists(os.path.join(poppler_path, "pdftoppm.exe")):
    raise FileNotFoundError(f"pdftoppm.exe not found in {poppler_path}. Please verify the poppler installation.")

# Function to crop white borders from an image
def crop_white_borders(image):
    # Convert image to numpy array
    img_array = np.array(image)
    # Convert to grayscale for simpler processing
    gray = np.array(image.convert("L"))
    # Threshold to identify white areas (assuming white is near 255)
    non_white = gray < 240  # Adjust threshold if needed
    # Find non-white pixel coordinates
    coords = np.argwhere(non_white)
    if coords.size == 0:
        print("Warning: No non-white content found in image, returning original.")
        return image
    # Get bounding box
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)
    # Crop the image
    cropped = image.crop((x_min, y_min, x_max + 1, y_max + 1))
    return cropped

# Process each PDF in the input directory
for filename in os.listdir(input_dir):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(input_dir, filename)
        temp_pdf_path = None
        try:
            # Open and decrypt PDF
            pdf_reader = PdfReader(pdf_path)
            if pdf_reader.is_encrypted:
                if not pdf_reader.decrypt(password):
                    print(f"Error: Failed to decrypt {filename} with provided password.")
                    continue
            
            # Create a temporary decrypted PDF
            temp_pdf = PdfWriter()
            for page in pdf_reader.pages:
                temp_pdf.add_page(page)
            temp_pdf_path = os.path.join(tempfile.gettempdir(), f"decrypted_{filename}")
            with open(temp_pdf_path, "wb") as temp_file:
                temp_pdf.write(temp_file)
            
            # Convert first page of decrypted PDF to image with high DPI
            images = convert_from_path(temp_pdf_path, dpi=300, first_page=1, last_page=1, poppler_path=poppler_path)
            if not images:
                print(f"Error: Failed to convert {filename} to image.")
                continue
            
            # Get the first page image
            image = images[0]
            
            # Resize to simulate 56% zoom
            original_size = image.size
            new_size = (int(original_size[0] * 0.56), int(original_size[1] * 0.56))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Crop white borders
            image = crop_white_borders(image)
            
            # Save the image with the same name (but .png extension)
            output_filename = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(output_dir, output_filename)
            image.save(output_path, "PNG", quality=95)
            print(f"Processed {filename} -> {output_filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                try:
                    os.remove(temp_pdf_path)
                except Exception as e:
                    print(f"Warning: Failed to delete temporary file {temp_pdf_path}: {str(e)}")