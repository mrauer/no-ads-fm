import argparse
import os
import ssl
import certifi
from pydub import AudioSegment
import torch

ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())


def estimate_bitrate(input_path, duration_ms):
    file_size_bytes = os.path.getsize(input_path)
    duration_seconds = duration_ms / 1000.0
    if duration_seconds == 0:
        return "128k"  # fallback
    bitrate_kbps = (file_size_bytes * 8) / 1000 / duration_seconds  # kbps
    # Round to nearest common MP3 bitrate
    common_rates = [64, 96, 128, 160, 192, 224, 256, 320]
    closest = min(common_rates, key=lambda x: abs(x - bitrate_kbps))
    return f"{closest}k"


def human_readable_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def main(input_path):
    tmp_path = "tmp_for_vad.wav"
    output_path = os.path.splitext(input_path)[0] + "_music_only.mp3"

    original_ext = os.path.splitext(input_path)[1].lower().lstrip(".")
    original_audio = AudioSegment.from_file(input_path, format=original_ext)
    duration_ms = len(original_audio)

    # Estimate original bitrate
    estimated_bitrate = estimate_bitrate(input_path, duration_ms)

    # Load Silero VAD model and utilities
    model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

    # Prepare audio for VAD
    audio_for_vad = original_audio.set_channels(1).set_frame_rate(16000)
    audio_for_vad.export(tmp_path, format="wav")
    wav = read_audio(tmp_path, sampling_rate=16000)
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000, return_seconds=True)

    # Extract non-speech segments
    non_speech_segments = []
    speech_duration_ms = 0
    last_end = 0

    for seg in speech_timestamps:
        start_ms = int(seg['start'] * 1000)
        end_ms = int(seg['end'] * 1000)
        speech_duration_ms += end_ms - start_ms
        if last_end < start_ms:
            non_speech_segments.append(original_audio[last_end:start_ms])
        last_end = end_ms

    if last_end < duration_ms:
        non_speech_segments.append(original_audio[last_end:duration_ms])

    if non_speech_segments:
        non_speech = sum(non_speech_segments)
        non_speech.export(output_path, format="mp3", bitrate=estimated_bitrate)
        print(f"Exported: {output_path} with estimated bitrate {estimated_bitrate}")

        # Calculate stats
        minutes_removed = speech_duration_ms / 1000.0 / 60
        input_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        size_diff = input_size - output_size
        size_diff = max(size_diff, 0)  # Avoid negative "savings"

        print(f"\nSpeech removed: {minutes_removed:.2f} minutes")
        print(f"Space saved: {human_readable_size(size_diff)}")
    else:
        print("No non-speech (music) detected.")

    if os.path.exists(tmp_path):
        os.remove(tmp_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove speech from an audio file using Silero VAD.")
    parser.add_argument("input_file", help="Path to the input audio file.")
    args = parser.parse_args()

    main(args.input_file)
