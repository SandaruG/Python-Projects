import os
import subprocess
import logging
try:
    from moviepy import VideoFileClip
except ImportError as e:
    print(f"Failed to import moviepy.editor: {e}")
    exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("captioning.log")]
)
logger = logging.getLogger(__name__)

# Define directories
VIDEO_FOLDER = r"Video"
SUBTITLE_FOLDER = r"Done"
OUTPUT_FOLDER = r"OUTPUT"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def escape_ffmpeg_path(path):
    """Escape file paths for FFmpeg, handling special characters."""
    path = os.path.normpath(path)
    # Replace backslashes with forward slashes and escape quotes
    path = path.replace('\\', '/').replace('"', '\\"')
    return f'"{path}"'

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        logger.info(f"FFmpeg version: {result.stdout.splitlines()[0]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"FFmpeg is not installed or not in PATH: {e}")
        return False

def validate_video_file(video_path):
    """Validate that a video file exists and is readable."""
    if not os.path.exists(video_path):
        logger.error(f"Video file does not exist: {video_path}")
        return False
    try:
        # Test if FFmpeg can read the file
        subprocess.run(
            ["ffmpeg", "-i", escape_ffmpeg_path(video_path), "-f", "null", "-"],
            capture_output=True, text=True, check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Invalid or corrupted video file {video_path}: {e.stderr}")
        return False

def create_srt_from_txt(txt_path, video_duration, output_srt_path):
    """Create a simple SRT file from a text transcript with estimated timings."""
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            transcript = f.read().strip().split()
        if not transcript:
            logger.warning(f"Empty transcript in {txt_path}")
            return False

        words_per_entry = 5
        subtitle_entries = []
        for i in range(0, len(transcript), words_per_entry):
            chunk = transcript[i:i + words_per_entry]
            start_time = (i / len(transcript)) * video_duration
            end_time = min(((i + words_per_entry) / len(transcript)) * video_duration, video_duration)

            start_h, start_m, start_s = int(start_time // 3600), int((start_time % 3600) // 60), start_time % 60
            end_h, end_m, end_s = int(end_time // 3600), int((end_time % 3600) // 60), end_time % 60
            start_time_str = f"{start_h:02d}:{start_m:02d}:{start_s:06.3f}".replace(".", ",")
            end_time_str = f"{end_h:02d}:{end_m:02d}:{end_s:06.3f}".replace(".", ",")

            subtitle_text = " ".join(chunk)
            subtitle_entries.append(
                f"{i // words_per_entry + 1}\n{start_time_str} --> {end_time_str}\n{subtitle_text}\n"
            )

        with open(output_srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(subtitle_entries))
        logger.info(f"Created SRT file: {output_srt_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create SRT from {txt_path}: {e}")
        return False

def add_captions_to_video(video_path, subtitle_path, output_path):
    """Add captions to a video using FFmpeg."""
    try:
        video_path_escaped = escape_ffmpeg_path(video_path)
        subtitle_path_escaped = escape_ffmpeg_path(subtitle_path)
        output_path_escaped = escape_ffmpeg_path(output_path)

        cmd = [
            "ffmpeg",
            "-i", video_path_escaped,
            "-vf", f"subtitles={subtitle_path_escaped}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "copy",
            "-y",
            output_path_escaped
        ]
        logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"FFmpeg output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error adding captions to {video_path}: {e}")
        return False

def main():
    """Main function to process videos and add captions."""
    if not check_ffmpeg():
        logger.error("Cannot proceed without FFmpeg. Please install it.")
        return

    video_files = [f for f in os.listdir(VIDEO_FOLDER) if f.lower().endswith(".mp4")]
    logger.info(f"Found {len(video_files)} video files: {video_files}")

    for video_file in video_files:
        try:
            base_name = os.path.splitext(video_file)[0]
            video_path = os.path.join(VIDEO_FOLDER, video_file)
            subtitle_path = os.path.join(SUBTITLE_FOLDER, f"{base_name}.srt")
            txt_path = os.path.join(SUBTITLE_FOLDER, f"{base_name}.txt")
            output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_captioned.mp4")

            # Validate video file
            if not validate_video_file(video_path):
                logger.warning(f"Skipping {base_name}: Invalid or inaccessible video file")
                continue

            # Get video duration
            try:
                video = VideoFileClip(video_path)
                video_duration = video.duration
                video.close()
            except Exception as e:
                logger.error(f"Failed to get duration for {video_path}: {e}")
                continue

            # Create SRT if needed
            if not os.path.exists(subtitle_path) and os.path.exists(txt_path):
                logger.info(f"No SRT found for {base_name}, creating from {txt_path}")
                if not create_srt_from_txt(txt_path, video_duration, subtitle_path):
                    logger.warning(f"Skipping {base_name}: Failed to create SRT")
                    continue

            if not os.path.exists(subtitle_path):
                logger.warning(f"Skipping {base_name}: No subtitle file (.srt) or transcript (.txt) found")
                continue

            if add_captions_to_video(video_path, subtitle_path, output_path):
                logger.info(f"Processed {base_name} successfully")
            else:
                logger.error(f"Failed to process {base_name}")
        except Exception as e:
            logger.error(f"Error processing {video_file}: {e}")
            continue

    logger.info("Processing complete.")

if __name__ == "__main__":
    main()