import os
import subprocess
import shutil

AUDIO_DIR = r"YOUR FOLDER\Audio"
VIDEO_PATH = r"YOUR FOLDER"
OUTPUT_DIR = r"YOUR FOLDER"
DONE_DIR = r"C:YOUR FOLDER"

# Ensure output and done directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DONE_DIR, exist_ok=True)

for audio_file in os.listdir(AUDIO_DIR):
    audio_path = os.path.join(AUDIO_DIR, audio_file)
    if not os.path.isfile(audio_path):
        continue
    
    # Get audio duration using ffprobe
    try:
        duration_str = subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]).decode().strip()
        audio_duration = float(duration_str)
    except Exception as e:
        print(f"Error getting duration for {audio_file}: {e}")
        continue
    
    total_duration = audio_duration + 7
    
    # Output file name: same as audio but with .mp4 extension
    output_file = os.path.splitext(audio_file)[0] + '.mp4'
    output_path = os.path.join(OUTPUT_DIR, output_file)
    
    # Run ffmpeg to add audio to muted video and crop to audio duration + 7 seconds
    try:
        subprocess.call([
            'ffmpeg', '-i', VIDEO_PATH, '-i', audio_path,
            '-c:v', 'copy', '-c:a', 'aac',
            '-map', '0:v:0', '-map', '1:a:0',
            '-t', str(total_duration), output_path
        ])
        print(f"Processed {audio_file} -> {output_file}")
        
        # Move the audio file to the Done folder
        shutil.move(audio_path, os.path.join(DONE_DIR, audio_file))
        print(f"Moved {audio_file} to Done folder")
    except Exception as e:
        print(f"Error processing {audio_file}: {e}")