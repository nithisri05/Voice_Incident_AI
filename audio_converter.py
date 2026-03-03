import ffmpeg

def convert_webm_to_wav(input_path):
    """
    Simple and safe conversion.
    No aggressive silence trimming.
    Just resample + mono conversion.
    """

    output_path = input_path.replace(".webm", "_cleaned.wav")

    (
        ffmpeg
        .input(input_path)
        .output(
            output_path,
            format="wav",
            acodec="pcm_s16le",
            ar="16000",
            ac=1
        )
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path