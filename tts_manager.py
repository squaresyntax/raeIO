import os

try:
    from TTS.api import TTS
except ImportError:  # pragma: no cover - optional dependency
    TTS = None


class TTSManager:
    def __init__(self, voice="tts_models/en/vctk/vits", cache_dir="tts_cache", logger=None, fuckery_mode=False):
        self.voice = voice
        self.logger = logger
        self.cache_dir = cache_dir
        self.fuckery_mode = fuckery_mode
        os.makedirs(cache_dir, exist_ok=True)
        if TTS:
            self.tts = TTS(voice)
        else:
            self.tts = None

    def synthesize(self, text, voice=None, speaker_wav=None, emotion=None):
        voice = voice or self.voice
        fname = f"{hash((text, voice, emotion, speaker_wav))}.wav"
        if self.fuckery_mode:
            fpath = os.path.join(self.cache_dir, fname + ".enc")
            with open(fpath, "wb") as f:
                f.write(b"ENCRYPTED")
            return fpath
        if not self.tts:
            fpath = os.path.join(self.cache_dir, fname)
            with open(fpath, "wb") as f:
                f.write(b"FAKEAUDIO")
            return fpath
        kwargs = {}
        if speaker_wav:
            kwargs['speaker_wav'] = speaker_wav
        if emotion:
            kwargs['emotion'] = emotion
        wav = self.tts.tts(text=text, speaker_wav=speaker_wav, emotion=emotion)
        self.tts.save_wav(wav, fpath)
        return fpath

    def list_voices(self):
        if self.tts:
            return self.tts.list_voices()
        return []

    def set_voice(self, voice):
        self.voice = voice
        if TTS:
            self.tts = TTS(voice)
