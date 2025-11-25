import fitz  # PyMuPDF
import os
import glob
from PIL import Image
import io

# Define the input directory and output PDF path
input_dir = r"folder"
output_pdf = os.path.join(input_dir, "output_images_compressed.pdf")

# Find the first PDF file in the directory
pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
if not pdf_files:
    raise FileNotFoundError("No PDF files found in the specified directory")
input_pdf = pdf_files[0]  # Take the first PDF found

# Open the input PDF
pdf_document = fitz.open(input_pdf)

# Create a new PDF document
new_pdf = fitz.open()

# Process each page
for page_num in range(len(pdf_document)):
    # Load the page
    page = pdf_document[page_num]
    
    # Convert the page to an image (PNG) with lower DPI for smaller size
    pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))  # 150 DPI
    
    # Convert pixmap to PIL Image for JPEG compression
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    # Save the image as JPEG with compression in memory
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=75)  # Adjust quality (0-100, lower = more compression)
    img_data = output.getvalue()
    
    # Get image dimensions
    img_width, img_height = img.size
    
    # Create a new page in the output PDF with the same dimensions
    new_page = new_pdf.new_page(width=img_width, height=img_height)
    
    # Insert the compressed image into the new page
    new_page.insert_image(new_page.rect, stream=img_data)

# Save the new PDF with compression options
new_pdf.save(output_pdf, deflate=True, clean=True)  # Enable compression
new_pdf.close()
pdf_document.close()

print(f"Compressed PDF created at: {output_pdf}")