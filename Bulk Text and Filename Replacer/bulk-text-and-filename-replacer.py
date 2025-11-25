import os

# Define the directory path
directory = r"Directory"

# Define the strings to replace
old_string = "aita"
new_string = "Am I the A Hole"

# Function to replace text in file content
def replace_text_in_file(file_path):
    try:
        # Read the content of the file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace AITA with Am I the A Hole in content
        new_content = content.replace(old_string, new_string)
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Iterate through all files in the directory
for filename in os.listdir(directory):
    # Check if the file is a .txt file
    if filename.endswith('.txt'):
        # Full path of the file
        old_file_path = os.path.join(directory, filename)
        
        # Replace AITA in the file name
        if old_string in filename:
            new_filename = filename.replace(old_string, new_string)
            new_file_path = os.path.join(directory, new_filename)
            
            # Rename the file
            try:
                os.rename(old_file_path, new_file_path)
                print(f"Renamed file: {filename} -> {new_filename}")
            except Exception as e:
                print(f"Error renaming file {filename}: {e}")
        else:
            new_file_path = old_file_path
        
        # Replace AITA in the file content
        replace_text_in_file(new_file_path)

print("Replacement process completed.")