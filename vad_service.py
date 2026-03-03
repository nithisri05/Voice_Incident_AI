import torch
import torchaudio
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
import os

# Load model once (global)
model = load_silero_vad()


def apply_vad(input_wav_path):
    """
    Applies Silero VAD to remove non-speech parts.
    Returns path to speech-only WAV file.
    """

    wav = read_audio(input_wav_path, sampling_rate=16000)

    speech_timestamps = get_speech_timestamps(
        wav,
        model,
        sampling_rate=16000,
        threshold=0.5
    )

    if not speech_timestamps:
        return input_wav_path  # No speech detected

    speech_audio = []

    for segment in speech_timestamps:
        start = segment['start']
        end = segment['end']
        speech_audio.append(wav[start:end])

    speech_only = torch.cat(speech_audio)

    output_path = input_wav_path.replace(".wav", "_vad.wav")

    torchaudio.save(
        output_path,
        speech_only.unsqueeze(0),
        16000
    )

    return output_path