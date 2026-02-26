import asyncio
import edge_tts

# Free Microsoft Edge TTS voices - no API key needed
VOICE = "en-US-AriaNeural"  # Natural female voice
RATE = "+0%"
VOLUME = "+0%"

async def generate_voice(text: str, output_path: str) -> str:
    """Generate speech using Microsoft Edge TTS - completely free."""
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, volume=VOLUME)
    await communicate.save(output_path)
    return output_path

async def get_available_voices() -> list:
    """Get list of available voices."""
    voices = await edge_tts.list_voices()
    english_voices = [v for v in voices if v["Locale"].startswith("en-")]
    return english_voices
