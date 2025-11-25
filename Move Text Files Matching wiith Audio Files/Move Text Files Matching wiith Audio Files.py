import os
import shutil

# Define the paths
audio_folder = r"Your Folder"
text_folder = r"Your Folder"
destination_folder = r"Your Folder"

# Get list of audio files
audio_files = [f for f in os.listdir(audio_folder) if f.endswith(('.mp3', '.wav', '.m4a'))]

# Process each audio file
for audio_file in audio_files:
    # Get the base name without extension
    base_name = os.path.splitext(audio_file)[0]
    # Construct the corresponding text file name
    text_file = base_name + '.txt'
    text_file_path = os.path.join(text_folder, text_file)
    destination_path = os.path.join(destination_folder, text_file)
    
    # Check if the text file exists and move it
    if os.path.exists(text_file_path):
        try:
            shutil.move(text_file_path, destination_path)
            print(f"Moved: {text_file} to {destination_folder}")
        except Exception as e:
            print(f"Error moving {text_file}: {str(e)}")
    else:
        print(f"No matching text file found for {audio_file}")

# Verify the result
print("\nFiles in destination folder after moving:")
for file in os.listdir(destination_folder):
    if file.endswith('.txt'):
        print(file)