import os
import subprocess
import torch
from melo.api import TTS

# Define paths
TEXT_DIR = r"C:\Users\Sandaru\OneDrive\Desktop\New folder\test"
AUDIO_DIR = r"C:\Users\Sandaru\OneDrive\Desktop\New folder\Audio"
DONE_DIR = r"C:\Users\Sandaru\OneDrive\Desktop\New folder\Done"

def get_device() -> str:
    """Auto-detect torch device."""
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return 'mps'
    return 'cuda:0' if torch.cuda.is_available() else 'cpu'

def text_to_audio(input_file):
    """Convert text to audio and save as MP3."""
    device = get_device()
    try:
        model = TTS(language='EN', device=device)
        speaker_id = model.hps.data.spk2id['EN-US']
    except Exception as e:
        print(f"Error initializing TTS: {e}")
        return None, None

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            text = file.read().strip()
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return None, None

    if not text:
        print(f"Empty text in {input_file}. Skipping.")
        return None, None

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    wav_file = os.path.join(AUDIO_DIR, f"{base_name}.wav")
    mp3_file = os.path.join(AUDIO_DIR, f"{base_name}.mp3")

    try:
        model.tts_to_file(text, speaker_id, wav_file, speed=0.9)
        subprocess.run(['ffmpeg', '-y', '-i', wav_file, '-acodec', 'mp3', mp3_file], check=True, capture_output=True)
        os.remove(wav_file)
        print(f"Audio saved: {mp3_file}")
        
        # Move the input text file to Done folder
        os.makedirs(DONE_DIR, exist_ok=True)
        done_file = os.path.join(DONE_DIR, f"{base_name}.txt")
        os.rename(input_file, done_file)
        print(f"Text file moved to: {done_file}")
        
        return mp3_file, text
    except Exception as e:
        print(f"Error generating audio for {input_file}: {e}")
        if os.path.exists(wav_file):
            os.remove(wav_file)
        return None, None

def main():
    """Process all text files in TEXT_DIR sequentially."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(DONE_DIR, exist_ok=True)

    txt_files = [f for f in os.listdir(TEXT_DIR) if f.lower().endswith('.txt')]
    if not txt_files:
        print("No .txt files found.")
        return

    for txt_file in txt_files:
        print(f"\nProcessing {txt_file}...")
        # Generate audio and move text file
        input_file = os.path.join(TEXT_DIR, txt_file)
        audio_path, text = text_to_audio(input_file)
        if audio_path and text:
            print(f"Successfully processed {txt_file}")
        else:
            print(f"Failed to process {txt_file}")

if __name__ == "__main__":
    main()