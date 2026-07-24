import asyncio
import edge_tts
import vlc
import time

async def generateSpeech(text):
    communicate = edge_tts.Communicate(
        text,
        "en-US-GuyNeural"
    )
    await communicate.save("speech.mp3")

def speak(text):
    asyncio.run(generateSpeech(text))

    player = vlc.MediaPlayer("speech.mp3")

    result = player.play()

    while player.get_state() not in (
        vlc.State.Ended,
        vlc.State.Error,
    ):
        time.sleep(0.1)