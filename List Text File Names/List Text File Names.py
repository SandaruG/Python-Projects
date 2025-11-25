import os

# Define the input and output directories using raw strings
input_dir = r"Your Folder"
output_dir = r"Your Folder"
output_file = os.path.join(output_dir, "txt_file_names.txt")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Get all .txt files in the input directory
txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]

# Write the file names to the output file
with open(output_file, 'w') as f:
    for file_name in txt_files:
        f.write(file_name + '\n')

print(f"Text file names have been written to {output_file}")