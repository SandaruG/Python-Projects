import os
import subprocess
import re
import torch
import torchaudio
import warnings
import psutil
from dataclasses import dataclass
from typing import List

# Suppress torchcodec warning
warnings.filterwarnings("ignore", category=UserWarning, module="torchaudio._backend.utils")

# Define directories
TEST_FOLDER = r"Your Folder"
AUDIO_FOLDER = r"Your Folder"
VIDEO_FOLDER = r"Your Folder"
OUTPUT_FOLDER = r"Your Folder"

# Verify directories exist
print(f"Checking directories:")
print(f"  Video folder: {VIDEO_FOLDER} - Exists: {os.path.exists(VIDEO_FOLDER)}")
print(f"  Audio folder: {AUDIO_FOLDER} - Exists: {os.path.exists(AUDIO_FOLDER)}")
print(f"  Text folder: {TEST_FOLDER} - Exists: {os.path.exists(TEST_FOLDER)}")
print(f"  Output folder: {OUTPUT_FOLDER} - Exists: {os.path.exists(OUTPUT_FOLDER)}")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Point dataclass
@dataclass
class Point:
    token_index: int
    time_index: int
    score: float

# Segment dataclass
@dataclass
class Segment:
    label: str
    start: int
    end: int
    score: float

    def __repr__(self):
        return f"{self.label}\t({self.score:4.2f}): [{self.start:5d}, {self.end:5d})"

    @property
    def length(self):
        return self.end - self.start

# Function to get trellis
def get_trellis(emission, tokens, blank_id=0):
    num_frame = emission.size(0)
    num_tokens = len(tokens)

    trellis = torch.zeros((num_frame, num_tokens))
    trellis[1:, 0] = torch.cumsum(emission[1:, blank_id], 0)
    trellis[0, 1:] = -float("inf")
    trellis[-num_tokens + 1 :, 0] = float("inf")

    for t in range(num_frame - 1):
        trellis[t + 1, 1:] = torch.maximum(
            trellis[t, 1:] + emission[t, blank_id],
            trellis[t, :-1] + emission[t, tokens[1:]],
        )
    return trellis

# Function to backtrack
def backtrack(trellis, emission, tokens, blank_id=0):
    t, j = trellis.size(0) - 1, trellis.size(1) - 1
    path = [Point(j, t, emission[t, blank_id].exp().item())]

    while j > 0:
        assert t > 0
        p_stay = emission[t - 1, blank_id]
        p_change = emission[t - 1, tokens[j]]

        stayed = trellis[t - 1, j] + p_stay
        changed = trellis[t - 1, j - 1] + p_change

        t -= 1
        if changed > stayed:
            j -= 1
        prob = (p_change if changed > stayed else p_stay).exp().item()
        path.append(Point(j, t, prob))

    while t > 0:
        prob = emission[t - 1, blank_id].exp().item()
        path.append(Point(j, t - 1, prob))
        t -= 1

    return path[::-1]

# Function to merge repeats
def merge_repeats(path, transcript):
    i1, i2 = 0, 0
    segments = []
    while i1 < len(path):
        while i2 < len(path) and path[i1].token_index == path[i2].token_index:
            i2 += 1
        score = sum(path[k].score for k in range(i1, i2)) / (i2 - i1)
        segments.append(
            Segment(
                transcript[path[i1].token_index],
                path[i1].time_index,
                path[i2 - 1].time_index + 1,
                score,
            )
        )
        i1 = i2
    return segments

# Function to merge words
def merge_words(segments: List[Segment], separator: str = "|") -> List[Segment]:
    words = []
    i1, i2 = 0, 0
    while i1 < len(segments):
        if i2 >= len(segments) or segments[i2].label == separator:
            if i1 != i2:
                seg = segments[i1]
                if i1 > 0:
                    seg.score = sum(segments[k].score * segments[k].length for k in range(i1, i2)) / sum(segments[k].length for k in range(i1, i2))
                else:
                    seg.score = sum(segments[k].score for k in range(i1, i2)) / (i2 - i1)
                word = "".join([s.label for s in segments[i1:i2]])
                seg = Segment(word, segments[i1].start, segments[i2 - 1].end + 1, seg.score)
                words.append(seg)
            i1 = i2 + 1
            i2 = i1
        else:
            i2 += 1
    return words

# Function to format time for ASS
def format_ass_time(t: float) -> str:
    hours = int(t // 3600)
    mins = int((t % 3600) // 60)
    secs = t % 60
    return f"{hours}:{mins:02}:{secs:05.2f}"

# ASS header template
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

# Function to clean text
def clean_text(text: str) -> str:
    # Remove punctuation, numbers, and special characters, keep letters and spaces
    return re.sub(r"[^a-zA-Z\s]", "", text).strip()

# Function to get memory usage
def get_memory_usage():
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024  # Convert to MB

# Process each video
print("Scanning video folder for .mp4 files...")
device = torch.device("cpu")  # Force CPU
print(f"Using device: {device}")
try:
    bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
    model = bundle.get_model().to(device)
    labels = bundle.get_labels()
    sample_rate = bundle.sample_rate
    print(f"Loaded WAV2VEC2 model successfully, memory usage: {get_memory_usage():.2f} MB")
except Exception as e:
    print(f"Failed to load WAV2VEC2 model: {e}")
    exit(1)

video_files = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(".mp4")]
print(f"Found {len(video_files)} .mp4 files: {video_files}")

for filename in video_files:
    base_name = os.path.splitext(filename)[0]
    print(f"\nProcessing {base_name}...")
    
    txt_path = os.path.join(TEST_FOLDER, f"{base_name}.txt")
    audio_path = os.path.join(AUDIO_FOLDER, f"{base_name}.mp3")
    video_path = os.path.join(VIDEO_FOLDER, filename)
    ass_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.ass")
    temp_video_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_temp.mp4")
    output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_captioned.mp4")
    
    # Check file existence
    files_exist = {
        "video": os.path.exists(video_path),
        "audio": os.path.exists(audio_path),
        "text": os.path.exists(txt_path)
    }
    print(f"File check for {base_name}: Video={files_exist['video']}, Audio={files_exist['audio']}, Text={files_exist['text']}")
    
    if not all(files_exist.values()):
        print(f"Skipping {base_name} due to missing files.")
        continue
    
    # Read and clean text
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            text = clean_text(f.read().strip())
    except Exception as e:
        print(f"Failed to read text file {txt_path}: {e}")
        continue
    
    if not text:
        print(f"No valid text after cleaning for {base_name}, skipping.")
        continue
    words_original = text.split()
    print(f"Cleaned text for {base_name}: {text[:100]}... ({len(words_original)} words)")
    
    # Limit transcript for testing
    if len(words_original) > 100:
        print(f"Warning: Transcript has {len(words_original)} words, truncating to 100 for testing.")
        words_original = words_original[:100]
        text = " ".join(words_original)
    
    # Prepare transcript for alignment
    transcript = "|" + "|".join(word.upper() for word in words_original) + "|"
    dictionary = {c: i for i, c in enumerate(labels)}
    
    # Validate transcript characters
    try:
        tokens = [dictionary[c] for c in transcript]
        print(f"Generated tokens for {base_name}, token count: {len(tokens)}")
    except KeyError as e:
        print(f"Invalid character {e} in transcript for {base_name}, skipping.")
        continue
    
    # Load and validate audio
    try:
        waveform, audio_sr = torchaudio.load(audio_path)
        duration = waveform.size(1) / audio_sr
        print(f"Loaded audio {audio_path}, sample rate: {audio_sr}, duration: {duration:.2f} seconds, memory usage: {get_memory_usage():.2f} MB")
        if duration > 600:
            print(f"Warning: Audio duration ({duration:.2f}s) is long, may cause memory issues.")
    except Exception as e:
        print(f"Failed to load audio {audio_path}: {e}")
        continue
    
    # Validate waveform
    try:
        print(f"Waveform shape: {waveform.shape}, dtype: {waveform.dtype}")
        if waveform.ndim != 2 or waveform.shape[0] not in [1, 2]:
            raise ValueError("Waveform must be 1D or 2D with 1 or 2 channels")
        if waveform.shape[0] == 2:
            waveform = waveform.mean(dim=0, keepdim=True)  # Convert stereo to mono
        print(f"Processed waveform shape: {waveform.shape}")
    except Exception as e:
        print(f"Waveform validation failed for {base_name}: {e}")
        continue
    
    # Validate audio integrity with FFmpeg
    try:
        ffmpeg_check = subprocess.run(
            ["ffmpeg", "-i", audio_path, "-f", "null", "-"],
            capture_output=True, text=True, check=True
        )
        print(f"FFmpeg validated audio file {audio_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg audio validation failed for {base_name}: {e.stderr}")
        continue
    
    if audio_sr != sample_rate:
        try:
            waveform = torchaudio.functional.resample(waveform, audio_sr, sample_rate)
            print(f"Resampled audio to {sample_rate} Hz, memory usage: {get_memory_usage():.2f} MB")
        except Exception as e:
            print(f"Failed to resample audio for {base_name}: {e}")
            continue
    
    # Get emissions
    with torch.inference_mode():
        try:
            print(f"Processing model, memory usage before: {get_memory_usage():.2f} MB")
            emissions, _ = model(waveform.to(device))
            emissions = torch.log_softmax(emissions, dim=-1)
            print(f"Generated emissions for {base_name}, emissions shape: {emissions.shape}, memory usage after: {get_memory_usage():.2f} MB")
        except MemoryError as e:
            print(f"MemoryError during model processing for {base_name}: {e}")
            continue
        except RuntimeError as e:
            print(f"RuntimeError during model processing for {base_name}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error during model processing for {base_name}: {e}")
            continue
    emission = emissions[0].cpu().detach()
    
    # Get trellis, path, segments
    try:
        print(f"Starting alignment, memory usage: {get_memory_usage():.2f} MB")
        trellis = get_trellis(emission, tokens)
        path = backtrack(trellis, emission, tokens)
        segments = merge_repeats(path, transcript)
        word_segments = merge_words(segments)
        print(f"Aligned {len(word_segments)} words for {base_name}")
    except Exception as e:
        print(f"Alignment failed for {base_name}: {e}")
        continue
    
    # Calculate ratio for timestamps
    ratio = waveform.size(1) / trellis.size(0)
    
    # Update word_segments with original casing
    for i, seg in enumerate(word_segments):
        seg.label = words_original[i] if i < len(words_original) else seg.label
    
    # Generate ASS file with word highlighting
    try:
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ASS_HEADER)
            chunk_size = 5
            for i in range(0, len(word_segments), chunk_size):
                chunk = word_segments[i:i + chunk_size]
                if not chunk:
                    continue
                start_time = (chunk[0].start * ratio) / sample_rate
                end_time = (chunk[-1].end * ratio) / sample_rate
                ass_text = ""
                current_time = start_time * 100  # Centiseconds
                for seg in chunk:
                    dur_cs = int(((seg.end - seg.start) * ratio / sample_rate) * 100)
                    ass_text += r"{\t(" + str(int(current_time - start_time * 100)) + "," + str(int(current_time - start_time * 100 + dur_cs)) + ",,Highlight)}" + seg.label + r"{\t(" + str(int(current_time - start_time * 100 + dur_cs)) + "," + str(int(current_time - start_time * 100 + dur_cs + 10)) + ",,Default)}" + " "
                    current_time += dur_cs
                ass_text = ass_text.strip()
                start_ass = format_ass_time(start_time)
                end_ass = format_ass_time(end_time)
                f.write(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{ass_text}\n")
        print(f"Generated ASS file: {ass_path}")
    except Exception as e:
        print(f"Failed to generate ASS file for {base_name}: {e}")
        continue
    
    # Combine video and audio using ffmpeg
    combine_cmd = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        temp_video_path
    ]
    try:
        print(f"Running FFmpeg combine command: {' '.join(combine_cmd)}")
        result = subprocess.run(combine_cmd, check=True, capture_output=True, text=True)
        print(f"Combined video and audio: {temp_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed to combine video and audio for {base_name}: {e.stderr}")
        continue
# Add subtitles using ffmpeg with escaped path
ass_path_escaped = ass_path.replace('\\', '\\\\').replace(':', '\\:')
subtitle_cmd = [
    "ffmpeg",
    "-i", temp_video_path,
    "-vf", f"ass={ass_path_escaped}",
    "-c:v", "libx264",
    "-c:a", "copy",
    output_path
]
try:
    print(f"Running FFmpeg subtitle command: {' '.join(subtitle_cmd)}")
    result = subprocess.run(subtitle_cmd, check=True, capture_output=True, text=True)
    print(f"Added subtitles, output: {output_path}")
except subprocess.CalledProcessError as e:
    print(f"FFmpeg failed to add subtitles for {base_name}: {e.stderr}")
    # Remove temporary files to avoid clutter
    
    
    # Clean up temp files
    try:
        os.remove(temp_video_path)
        os.remove(ass_path)
        print(f"Cleaned up temporary files for {base_name}")
    except OSError as e:
        print(f"Failed to clean up temporary files for {base_name}: {e}")
    
    print(f"Successfully processed {base_name}")

print("Processing complete.")