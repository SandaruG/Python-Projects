import os
import subprocess
import logging
import tempfile
import shutil
import torchaudio
import torch
import math
import warnings
from speechbrain.inference.ASR import EncoderDecoderASR
from speechbrain.utils.text_to_sequence import text_to_sequence
from speechbrain.utils.fetching import LocalStrategy
import numpy as np
from huggingface_hub import login

# Suppress torchaudio and huggingface_hub symlink warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torchaudio._backend")
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub.file_download")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("process.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define directories
TEST_FOLDER = r"test"
AUDIO_FOLDER = r"audio"
VIDEO_FOLDER = r"video"
OUTPUT_FOLDER = r"output"

# Ensure output directory exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ASS header for subtitle file
ASS_HEADER = """[Script Info]
Title: Generated Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,50,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,2,5,0,0,0,1
Style: Highlight,Arial,50,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,2,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# Format time for ASS (hours:minutes:seconds.hundredths)
def format_ass_time(t: float) -> str:
    t = max(0, t)  # Ensure non-negative time
    hours = int(t // 3600)
    mins = int((t % 3600) // 60)
    secs = t % 60
    return f"{hours}:{mins:02}:{secs:05.2f}"

# Clean text (remove extra whitespace and normalize)
def clean_text(text: str) -> str:
    return ' '.join(text.strip().split())

# Custom FFmpeg path escaping for Windows
def escape_ffmpeg_path(path):
    path = os.path.normpath(path)
    return f'"{path}"'

# Check if FFmpeg is installed
def check_ffmpeg():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        logger.info(f"FFmpeg version: {result.stdout.splitlines()[0]}")
        return True
    except Exception as e:
        logger.error(f"FFmpeg check failed: {e}")
        return False

# Split audio if duration exceeds chunk_duration (default 1800 seconds)
def split_audio(audio_path, chunk_duration=1800):
    try:
        info = torchaudio.info(audio_path)
        duration = info.num_frames / info.sample_rate
        if duration <= chunk_duration:
            return [audio_path]
        logger.info(f"Audio duration {duration:.2f}s exceeds {chunk_duration}s, splitting...")
        temp_dir = tempfile.mkdtemp()
        chunk_paths = []
        num_chunks = math.ceil(duration / chunk_duration)
        cmd = [
            "ffmpeg",
            "-i", escape_ffmpeg_path(audio_path),
            "-f", "segment",
            "-segment_time", str(chunk_duration),
            "-c", "copy",
            os.path.join(temp_dir, "chunk_%03d.mp3")
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        chunk_paths = sorted([os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".mp3")])
        logger.info(f"Split into {len(chunk_paths)} chunks: {chunk_paths}")
        return chunk_paths
    except Exception as e:
        logger.error(f"Failed to split audio {audio_path}: {e}")
        return [audio_path]

# Load audio waveform
def load_audio(audio_path):
    try:
        waveform, sample_rate = torchaudio.load(audio_path)
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)
        return waveform, 16000
    except Exception as e:
        logger.error(f"Failed to load audio {audio_path}: {e}")
        return None, None

# Perform forced alignment using SpeechBrain
def align_transcript(asr_model, waveform, sample_rate, transcript):
    try:
        # Tokenize transcript
        tokens = text_to_sequence(transcript, task="asr")
        token_tensor = torch.tensor([tokens], device=waveform.device)
        
        # Get audio duration
        duration = waveform.shape[1] / sample_rate
        
        # Perform transcription to get logits
        logits, _ = asr_model.transcribe_batch(waveform, torch.tensor([1.0]))
        
        # Estimate word timings (simplified approach)
        words = transcript.split()
        num_words = len(words)
        if num_words == 0:
            return []
        
        # Approximate timing by dividing audio duration
        word_duration = duration / num_words
        alignments = []
        for i, word in enumerate(words):
            start_time = i * word_duration
            end_time = (i + 1) * word_duration
            alignments.append({
                'word': word,
                'time_start': start_time,
                'time_end': end_time
            })
        return alignments
    except Exception as e:
        logger.error(f"Alignment failed: {e}")
        return []

# Main processing
def main():
    # Verify FFmpeg
    if not check_ffmpeg():
        logger.error("FFmpeg is not installed or not in PATH. Please install FFmpeg.")
        return

    # Authenticate with Hugging Face (optional, set HF_TOKEN environment variable if needed)
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        try:
            login(token=hf_token)
            logger.info("Authenticated with Hugging Face Hub.")
        except Exception as e:
            logger.warning(f"Failed to authenticate with Hugging Face: {e}")

    # Load SpeechBrain model with LocalStrategy to avoid symlinks
    try:
        asr_model = EncoderDecoderASR.from_hparams(
            source="speechbrain/asr-crdnn-rnnlm-librispeech",
            savedir="pretrained_models/asr-crdnn-rnnlm-librispeech",
            fetch_strategy=LocalStrategy.FETCH_LOCAL
        )
        logger.info("SpeechBrain ASR model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load SpeechBrain model: {e}")
        return

    # Get list of video files
    video_files = [f for f in os.listdir(VIDEO_FOLDER) if f.lower().endswith(".mp4")]
    logger.info(f"Found {len(video_files)} video files: {video_files}")

    for filename in video_files:
        try:
            base_name = os.path.splitext(filename)[0]
            logger.info(f"\nProcessing {base_name}...")

            # Define file paths
            txt_path = os.path.join(TEST_FOLDER, f"{base_name}.txt")
            audio_path = os.path.join(AUDIO_FOLDER, f"{base_name}.mp3")
            video_path = os.path.join(VIDEO_FOLDER, filename)
            ass_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.ass")
            output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_captioned.mp4")

            # Check if required files exist
            if not (os.path.exists(video_path) and os.path.exists(audio_path) and os.path.exists(txt_path)):
                logger.warning(f"Skipping {base_name}: Missing video, audio, or transcript file")
                continue

            # Read transcript
            with open(txt_path, "r", encoding="utf-8") as f:
                transcript = clean_text(f.read())
            if not transcript:
                logger.warning(f"Skipping {base_name}: Empty transcript")
                continue

            # Split audio if necessary
            audio_chunks = split_audio(audio_path)
            all_words = []
            offset = 0

            # Process each audio chunk
            for chunk_path in audio_chunks:
                try:
                    logger.info(f"Aligning chunk {chunk_path}...")
                    waveform, sample_rate = load_audio(chunk_path)
                    if waveform is None:
                        logger.warning(f"Skipping chunk {chunk_path}: Failed to load audio")
                        continue

                    # Move waveform to the same device as the model
                    device = next(asr_model.parameters()).device
                    waveform = waveform.to(device)

                    # Perform forced alignment
                    alignments = align_transcript(asr_model, waveform, sample_rate, transcript)
                    if not alignments:
                        logger.warning(f"No alignments generated for chunk {chunk_path}")
                        continue

                    # Adjust timestamps by offset
                    for word in alignments:
                        word['time_start'] += offset
                        word['time_end'] += offset
                    all_words.extend(alignments)
                    offset += torchaudio.info(chunk_path).num_frames / torchaudio.info(chunk_path).sample_rate
                except Exception as e:
                    logger.error(f"Alignment failed for chunk {chunk_path}: {e}")
                    continue
                finally:
                    if chunk_path != audio_path and os.path.exists(chunk_path):
                        try:
                            os.remove(chunk_path)
                            logger.info(f"Removed temporary chunk: {chunk_path}")
                        except Exception as e:
                            logger.error(f"Failed to remove chunk {chunk_path}: {e}")

            if not all_words:
                logger.warning(f"Skipping {base_name}: No alignments generated")
                continue

            logger.info(f"Aligned {len(all_words)} words.")

            # Generate ASS file
            with open(ass_path, "w", encoding="utf-8") as f:
                f.write(ASS_HEADER)
                for i in range(0, len(all_words), 5):
                    chunk = all_words[i:i + 5]
                    if not chunk:
                        continue
                    start_time = chunk[0]['time_start']
                    end_time = chunk[-1]['time_end']
                    if start_time >= end_time:
                        logger.warning(f"Invalid timing for chunk {i}: start={start_time}, end={end_time}")
                        continue
                    ass_text = ""
                    current_time = start_time * 100
                    for word in chunk:
                        dur_cs = int((word['time_end'] - word['time_start']) * 100)
                        if dur_cs <= 0:
                            logger.warning(f"Invalid duration for word {word['word']}: {dur_cs}")
                            continue
                        ass_text += f"{{\\t({int(current_time - start_time * 100)},{int(current_time - start_time * 100 + dur_cs)},,Highlight)}}{word['word']}{{\\t({int(current_time - start_time * 100 + dur_cs)},{int(current_time - start_time * 100 + dur_cs + 10)},,Default)}} "
                        current_time += dur_cs
                    f.write(f"Dialogue: 0,{format_ass_time(start_time)},{format_ass_time(end_time)},Default,,0,0,0,,{ass_text.strip()}\n")

            if not os.path.exists(ass_path):
                logger.error(f"ASS file {ass_path} not created.")
                continue

            # Combine video with subtitles
            temp_ass_path = None
            try:
                logger.info("Running FFmpeg to add subtitles...")
                temp_ass_path = os.path.join(tempfile.gettempdir(), f"temp_subtitle_{os.getpid()}.ass")
                shutil.copy(ass_path, temp_ass_path)

                video_path_escaped = escape_ffmpeg_path(video_path)
                temp_ass_path_escaped = escape_ffmpeg_path(temp_ass_path)
                output_path_escaped = escape_ffmpeg_path(output_path)

                subtitle_cmd = [
                    "ffmpeg",
                    "-i", video_path_escaped,
                    "-vf", f"ass={temp_ass_path_escaped}",
                    "-c:v", "libx264",
                    "-c:a", "copy",
                    "-y",
                    output_path_escaped
                ]
                logger.info(f"FFmpeg command: {' '.join(subtitle_cmd)}")
                result = subprocess.run(subtitle_cmd, check=True, capture_output=True, text=True)
                logger.info(f"FFmpeg output: {result.stdout}")
                logger.info(f"Successfully processed {base_name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"FFmpeg failed for {base_name}: {e.stderr}")
            finally:
                if temp_ass_path and os.path.exists(temp_ass_path):
                    try:
                        os.remove(temp_ass_path)
                        logger.info(f"Removed temporary ASS file: {temp_ass_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove temporary ASS file {temp_ass_path}: {e}")
                if os.path.exists(ass_path):
                    try:
                        os.remove(ass_path)
                        logger.info(f"Removed ASS file: {ass_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove ASS file {ass_path}: {e}")

        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            continue

    logger.info("Processing complete.")

if __name__ == "__main__":
    main()