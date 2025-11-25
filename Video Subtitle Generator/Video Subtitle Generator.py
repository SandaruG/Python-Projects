import os
import subprocess
import json
import math
import hashlib
import whisper_timestamped

# Function to format time for ASS subtitles (HH:MM:SS.CC)
def format_time(seconds):
    if seconds < 0:
        seconds = 0
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds - int(seconds)) * 100)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"

# Function to get video duration
def get_video_duration(video_path):
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'json', video_path
        ], capture_output=True, text=True, check=True)
        return float(json.loads(result.stdout)['format']['duration'])
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        print(f"Error getting duration: {e}")
        return 0

# Directories
base_dir = r"C:\Users\Sandaru\OneDrive\Desktop\New Folder"
video_dir = os.path.join(base_dir, "Video")
txt_dir = os.path.join(base_dir, "Done")
out_dir = os.path.join(base_dir, "Output")
temp_dir = os.path.join(base_dir, "Temp")

# Validate directories
for directory in [video_dir, txt_dir, out_dir, temp_dir]:
    os.makedirs(directory, exist_ok=True)
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory.")
        exit(1)

# ASS header (unchanged)
ass_header = """[Script Info]
Title: Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1280
PlayResY: 720
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Seagl Print,50,&H00FFFFFF,&H00FFFF00,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,5,30,30,30,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Check FFmpeg installation
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
    subprocess.run(['ffprobe', '-version'], capture_output=True, text=True, check=True)
except FileNotFoundError:
    print("Error: FFmpeg or ffprobe not found. Please ensure FFmpeg is installed and added to PATH.")
    exit(1)

# Process each video
for video_file in os.listdir(video_dir):
    if not video_file.lower().endswith('.mp4'):
        print(f"Skipping non-MP4 file: {video_file}")
        continue

    base_name, _ = os.path.splitext(video_file)
    txt_path = os.path.join(txt_dir, base_name + '.txt')
    video_path = os.path.join(video_dir, video_file)
    
    # Shorten output file name
    safe_base_name = hashlib.md5(base_name.encode()).hexdigest()[:10]
    output_path = os.path.join(out_dir, f"{safe_base_name}.mp4")
    temp_ass = os.path.join(temp_dir, f"{safe_base_name}.ass")

    print(f"Processing video: {video_file}")

    # Check text file
    if not os.path.exists(txt_path):
        print(f"Text file not found for {video_file}, skipping.")
        continue

    # Get video duration
    duration = get_video_duration(video_path)
    if duration == 0:
        print(f"Invalid duration for {video_file}, skipping.")
        continue

    # Load whisper-timestamped model
    try:
        model = whisper_timestamped.load_model("tiny")
        result = whisper_timestamped.transcribe(model, video_path, beam_size=5, word_level=True)
    except Exception as e:
        print(f"Error transcribing with whisper-timestamped for {video_file}: {e}")
        continue

    # Extract word-level timings
    words = []
    timings = []
    for segment in result["segments"]:
        for word in segment["words"]:
            if "start" in word and "end" in word and "text" in word:
                words.append(word["text"])
                timings.append((word["start"], word["end"]))

    if not words:
        print(f"No valid words transcribed for {video_file}, skipping.")
        continue

    # Timing parameters
    speed_factor = 4
    title_duration = 19 / speed_factor
    audio_end = duration / speed_factor
    min_chunk_duration = 0.5  # Minimum display time per chunk

    # Use whisper-timestamped word-level timings
    chunks = []
    chunk_timings = []
    current_chunk = []
    current_start = None
    for word, (start, end) in zip(words, timings):
        if not current_chunk:
            current_start = start
        current_chunk.append(word)
        if len(current_chunk) >= 3 or end - current_start >= min_chunk_duration:
            chunks.append(current_chunk)
            chunk_timings.append((current_start, end))
            current_chunk = []
            current_start = None
    if current_chunk:
        chunks.append(current_chunk)
        chunk_timings.append((current_start, timings[-1][1]))

    if not chunks:
        print(f"No valid chunks for {video_file}, skipping.")
        continue

    # Generate ASS subtitles
    try:
        ass_content = ass_header
        title_text = base_name.replace('_', ' ')
        title_text = title_text.replace('{', '\\{').replace('}', '\\}')
        ass_content += f"Dialogue: 0,0:00:00.00,{format_time(title_duration)},Default,,0,0,0,,{title_text}\n"

        print(f"Generating {len(chunks)} subtitle chunks for {video_file}")
        for i, (chunk, (start_time, end_time)) in enumerate(zip(chunks, chunk_timings)):
            if start_time >= audio_end or end_time <= start_time:
                print(f"Skipping invalid timing for chunk {i}: start={start_time}, end={end_time}")
                continue
            chunk_duration = end_time - start_time
            if chunk_duration < min_chunk_duration:
                end_time = start_time + min_chunk_duration
            ass_text = ' '.join(chunk).replace('{', '\\{').replace('}', '\\}').replace('\n', '\\N')
            start_str = format_time(start_time)
            end_str = format_time(end_time)
            ass_content += f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{ass_text}\n"
            print(f"Chunk {i}: {start_str} to {end_str}, Text: {ass_text}")

        # Write ASS file
        with open(temp_ass, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        print(f"Successfully wrote ASS file: {temp_ass}")
        # Log ASS file content for debugging
        with open(temp_ass, 'r', encoding='utf-8') as f:
            print(f"ASS file content:\n{f.read()}")
    except Exception as e:
        print(f"Error generating or writing ASS file for {video_file}: {e}")
        continue

    # Verify ASS file
    if not os.path.exists(temp_ass) or os.path.getsize(temp_ass) == 0:
        print(f"ASS file {temp_ass} is missing or empty, skipping.")
        continue

    # Burn subtitles into video
    try:
        temp_ass_ffmpeg = temp_ass.replace('\\', '\\\\').replace(':', '\\:').replace(',', '\\,')
        ffmpeg_command = [
            'ffmpeg', '-i', video_path,
            '-vf', f"subtitles='{temp_ass_ffmpeg}':force_style='FontName=Seagl\\ Print,FontSize=50':charenc=UTF-8",
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-c:a', 'copy', '-y', output_path
        ]
        print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
        result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"Successfully processed {video_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error burning subtitles for {video_file}: {e.stderr}")
        continue
    except Exception as e:
        print(f"Unexpected error running FFmpeg for {video_file}: {e}")
        continue
    finally:
        if os.path.exists(temp_ass):
            try:
                os.remove(temp_ass)
                print(f"Cleaned up ASS file: {temp_ass}")
            except Exception as e:
                print(f"Error cleaning up ASS file {temp_ass}: {e}")