import tempfile
import wave
from collections import deque

import numpy as np
import sounddevice as sd

from faster_whisper import WhisperModel
from openwakeword.model import Model


# -----------------------------
# CONFIG
# -----------------------------

WAKE_THRESHOLD = 0.5

SAMPLE_RATE = 16000
CHANNELS = 1

SPEECH_THRESHOLD = 1100

WHISPER_MODEL = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

# Warm up Whisper
try:
    WHISPER_MODEL.transcribe(
        np.zeros(16000, dtype=np.int16)
    )
except Exception:
    pass


wake_model = Model()

print("Wake models:", wake_model.models.keys())

#
# Beep
#

def beep():
    frequency = 880  # Hz
    duration = 0.15  # seconds

    samples = np.linspace(
        0,
        duration,
        int(SAMPLE_RATE * duration),
        False
    )

    tone = (
        0.3 *
        np.sin(
            2 * np.pi * frequency * samples
        )
    )

    sd.play(tone, SAMPLE_RATE)
    sd.wait()

# -----------------------------
# Wake Word
# -----------------------------


def wait_for_wakeword():
    global wake_model
    print("Listening for wake word...")

    block = 640  # 20ms chunks

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=np.int16,
        blocksize=block,
    ) as stream:

        while True:

            audio, _ = stream.read(block)

            prediction = wake_model.predict(
                audio.flatten()
            )

            for score in prediction.values():

                if score > WAKE_THRESHOLD:
                    print("Wake word detected!")
                    wake_model = Model()
                    return



# -----------------------------
# Record Speech
# -----------------------------


def record_until_silence():

    print("Listening...")
    beep()
    SILENCE_DURATION = 1.2
    START_TIMEOUT = 5

    frames = []

    silence_time = 0
    speech_started = False
    wait_time = 0

    block_size = 1024

    # Keep previous audio to avoid losing first words
    pre_roll = deque(maxlen=5)


    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=np.int16,
        blocksize=block_size,
    ) as stream:


        while True:

            audio, _ = stream.read(block_size)

            audio = audio.copy()

            volume = np.sqrt(
                np.mean(audio.astype(float) ** 2)
            )

            print(
                f"Volume: {int(volume)}"
            )


            pre_roll.append(audio)


            # Wait for speech
            if not speech_started:

                if volume > SPEECH_THRESHOLD:

                    speech_started = True

                    print(
                        "Speech detected..."
                    )

                    frames.extend(
                        list(pre_roll)
                    )

                else:

                    wait_time += (
                        block_size / SAMPLE_RATE
                    )

                    if wait_time > START_TIMEOUT:

                        print(
                            "No speech detected."
                        )

                        return None

                    continue


            else:

                frames.append(audio)


            # Detect silence

            if volume < SPEECH_THRESHOLD:

                silence_time += (
                    block_size / SAMPLE_RATE
                )

            else:

                silence_time = 0


            if silence_time >= SILENCE_DURATION:

                print(
                    "Finished speaking."
                )

                break



    audio = np.concatenate(frames)


    tmp = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )


    with wave.open(tmp.name, "wb") as wf:

        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)

        wf.writeframes(
            audio.tobytes()
        )


    return tmp.name



# -----------------------------
# Whisper
# -----------------------------


def transcribe(filename):

    segments, _ = WHISPER_MODEL.transcribe(
        filename
    )

    return "".join(
        segment.text
        for segment in segments
    ).strip()



# -----------------------------
# Main Loop
# -----------------------------


while True:

    wait_for_wakeword()

    filename = record_until_silence()

    if filename is None:
        continue


    text = transcribe(
        filename
    )


    print(
        f"You said: {text}"
    )