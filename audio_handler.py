import os
import uuid
from config import UPLOAD_FOLDER

def save_audio_file(audio_file):
    """
    Saves uploaded audio file to uploads folder.
    Returns saved file path.
    """

    unique_name = f"{uuid.uuid4()}.webm"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)

    audio_file.save(save_path)

    return save_path