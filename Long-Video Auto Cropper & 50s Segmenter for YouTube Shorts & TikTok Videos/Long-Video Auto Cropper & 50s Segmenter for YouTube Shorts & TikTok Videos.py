import os
import subprocess
import re

# Paths
input_dir = r'your input OUTPUT2'
output_dir = r'your output folder'

# FFmpeg executable path (update if FFmpeg is not in PATH)
ffmpeg_path = 'ffmpeg'  # Replace with r'C:\path\to\ffmpeg.exe' if needed

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Supported video extensions
video_extensions = ['.mp4', '.avi', '.mov', '.mkv']

def get_video_info(input_path):
    """Get video duration and dimensions using FFmpeg."""
    cmd = [ffmpeg_path, '-i', input_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        output = result.stderr  # FFmpeg outputs info to stderr
        
        # Extract duration (e.g., Duration: 00:02:50.00)
        duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.\d{2}', output)
        if not duration_match:
            return None, None, None
        hours, minutes, seconds = map(int, duration_match.groups())
        duration = hours * 3600 + minutes * 60 + seconds
        
        # Extract dimensions (e.g., 1920x1080)
        dimension_match = re.search(r'(\d+)x(\d+)[,\s]', output)
        if not dimension_match:
            return None, None, None
        width, height = map(int, dimension_match.groups())
        
        return duration, width, height
    except Exception as e:
        print(f"Error getting info for {input_path}: {e}")
        return None, None, None

# Iterate over files in input directory
for filename in os.listdir(input_dir):
    if any(filename.lower().endswith(ext) for ext in video_extensions):
        input_path = os.path.join(input_dir, filename)
        
        try:
            # Get video info
            duration, width, height = get_video_info(input_path)
            if duration is None or width is None or height is None:
                print(f"Skipping {filename}: Could not retrieve video info")
                continue
            
            # Verify 16:9 aspect ratio (allow small tolerance)
            if abs(width / height - 16 / 9) > 0.1:
                print(f"Skipping {filename}: Not in 16:9 ratio (width: {width}, height: {height})")
                continue
            
            # Calculate new width for 9:16 ratio
            new_width = int(height * 13 / 16)
            if new_width >= width:
                print(f"Skipping {filename}: Cannot crop to 9:16, insufficient width")
                continue
            
            # Calculate crop region (center crop)
            crop_x = (width - new_width) // 2
            crop_filter = f"crop={new_width}:{height}:{crop_x}:0"
            
            # Calculate number of 50-second parts
            segment_length = 50
            num_parts = int(duration // segment_length) + (1 if duration % segment_length > 0 else 0)
            
            base_name, _ = os.path.splitext(filename)
            
            for part in range(num_parts):
                start_time = part * segment_length
                end_time = min((part + 1) * segment_length, duration)
                
                # Output filename
                part_name = f"{base_name}_part{part+1}.mp4"
                output_path = os.path.join(output_dir, part_name)
                
                # FFmpeg command
                cmd = [
                    ffmpeg_path,
                    '-i', input_path,
                    '-ss', str(start_time),  # Start time
                    '-t', str(end_time - start_time),  # Duration of segment
                    '-vf', crop_filter,  # Crop filter
                    '-c:v', 'libx264',  # Video codec
                    '-c:a', 'aac',  # Audio codec
                    '-y',  # Overwrite output
                    output_path
                ]
                
                # Run FFmpeg command
                try:
                    subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print(f"Saved {part_name}")
                except subprocess.CalledProcessError as e:
                    print(f"Error processing {part_name}: {e}")
            
            # Delete the original video after all parts are processed
            try:
                os.remove(input_path)
                print(f"Deleted original video: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")