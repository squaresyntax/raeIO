import os

try:
    from TTS.api import TTS
except ImportError:
    TTS = None

class TTSManager:
    def __init__(self, voice="tts_models/en/vctk/vits", cache_dir="tts_cache", logger=None):
        self.voice = voice
        self.logger = logger
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        if TTS:
            self.tts = TTS(voice)
        else:
            self.tts = None
        self.flags = None

    def update_mode_flags(self, flags) -> None:
        self.flags = flags

    def synthesize(self, text, voice=None, speaker_wav=None, emotion=None):
        if self.flags and self.flags.stealth_mode:
            raise RuntimeError("TTS disabled in stealth mode")
        if not self.tts:
            raise RuntimeError("Coqui TTS not installed. Run: pip install TTS")
        voice = voice or self.voice
        fname = f"{hash((text, voice, emotion, speaker_wav))}.wav"
        fpath = os.path.join(self.cache_dir, fname)
        if os.path.exists(fpath):
            return fpath
        kwargs = {}
        if speaker_wav:
            kwargs['speaker_wav'] = speaker_wav
        if emotion:
            kwargs['emotion'] = emotion
        wav = self.tts.tts(text=text, speaker_wav=speaker_wav, emotion=emotion)
        self.tts.save_wav(wav, fpath)
        if self.flags and self.flags.fuckery_mode:
            with open(fpath, "rb") as f:
                data = f.read()
            encrypted = self.flags.encrypt(data)
            with open(fpath, "wb") as f:
                f.write(encrypted)
        return fpath

    def list_voices(self):
        if self.tts:
            return self.tts.list_voices()
        return []

    def set_voice(self, voice):
        self.voice = voice
        if TTS:
            self.tts = TTS(voice)