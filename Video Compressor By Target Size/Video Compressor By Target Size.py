import ffmpeg
import os

def compress_video(input_path, output_path, target_size_mb=200):
    try:
        # Probe the input video to get its duration
        probe = ffmpeg.probe(input_path)
        duration = float(probe['format']['duration'])  # Duration in seconds

        # Calculate target bitrate to achieve ~200MB (1 MB = 8 Mb)
        # Target size in bits = target_size_mb * 8 * 1024 * 1024
        target_bitrate = int((target_size_mb * 8 * 1024 * 1024) / duration)  # bits per second

        # Use H.265 (libx265) with CRF 28 for good quality and high compression
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            vcodec='libx265',  # H.265 codec
            crf=28,           # Constant Rate Factor (lower = better quality, 28 is a good balance)
            **{'b:v': target_bitrate},  # Set video bitrate
            acodec='aac',     # Re-encode audio to AAC
            ab='128k',        # Audio bitrate (128k is sufficient for most cases)
            preset='medium',  # Encoding speed vs compression trade-off
            movflags='faststart',  # Optimize for web streaming
            y=None            # Overwrite output file if it exists
        )

        # Run the FFmpeg command
        ffmpeg.run(stream)
        print(f"Compressed video saved as {output_path}")

        # Verify output file size
        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Output file size: {output_size_mb:.2f} MB")

    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode()}")
    except FileNotFoundError:
        print("Input file not found. Please check the path.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    input_path = "Downloads/IMG_5300.MOV"
    output_path = "Downloads/New Folder/video_com.mp4"
    compress_video(input_path, output_path)