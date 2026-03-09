import io

def save_audio_file(audio_file):
    """
    Convert uploaded audio to memory stream.
    Ignore extremely small recordings (noise).
    """

    audio_bytes = audio_file.read()

    # ignore very tiny audio (noise clicks)
    if len(audio_bytes) < 2000:
        return None

    audio_stream = io.BytesIO(audio_bytes)

    # whisper needs filename
    audio_stream.name = "speech.webm"

    return audio_stream