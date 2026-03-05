import os
import subprocess
import webrtcvad
import wave
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def convert_audio(input_path):
    """
    Convert WebM → 16kHz mono WAV
    """

    output_path = input_path.replace(".webm", "_clean.wav")

    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-loglevel", "quiet",
        output_path
    ]

    subprocess.run(command)

    return output_path


def remove_silence(wav_path):
    """
    Remove silence using VAD
    """

    vad = webrtcvad.Vad(2)

    with wave.open(wav_path, 'rb') as wf:

        sample_rate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    frame_duration = 30  # ms
    frame_size = int(sample_rate * frame_duration / 1000) * 2

    voiced_frames = []

    for i in range(0, len(frames), frame_size):

        frame = frames[i:i + frame_size]

        if len(frame) < frame_size:
            continue

        if vad.is_speech(frame, sample_rate):
            voiced_frames.append(frame)

    output_path = wav_path.replace("_clean.wav", "_vad.wav")

    with wave.open(output_path, 'wb') as wf:

        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(voiced_frames))

    return output_path


def transcribe_audio(file_path):

    clean_audio = convert_audio(file_path)

    speech_audio = remove_silence(clean_audio)

    with open(speech_audio, "rb") as audio_file:

        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            temperature=0
        )

    transcript = response.text.strip()

    try:
        os.remove(clean_audio)
        os.remove(speech_audio)
    except:
        pass

    return transcript