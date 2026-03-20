"""Kokoro TTS pipeline for real-time text-to-speech.

Uses the Kokoro model (82M params) to generate speech audio from text prompts.
Audio is output at 24kHz and streamed via WebRTC in sentence-sized chunks to
avoid overflowing the WebRTC audio buffer.
"""

import logging
import time
from collections import deque
from typing import TYPE_CHECKING

import numpy as np
import torch

from scope.core.pipelines.interface import Pipeline

if TYPE_CHECKING:
    from scope.core.pipelines.schema import BasePipelineConfig

logger = logging.getLogger(__name__)

# Maximum chunk duration in seconds. Chunks longer than this are split
# to keep the WebRTC audio buffer from overflowing (3s cap).
MAX_CHUNK_SECONDS = 2.0
SAMPLE_RATE = 24000
MAX_CHUNK_SAMPLES = int(MAX_CHUNK_SECONDS * SAMPLE_RATE)


class KokoroTTSPipeline(Pipeline):
    """Text-to-speech pipeline using Kokoro."""

    @classmethod
    def get_config_class(cls) -> type["BasePipelineConfig"]:
        from .schema import KokoroTTSConfig

        return KokoroTTSConfig

    def __init__(self, device: torch.device | None = None, **kwargs):
        self.device = (
            device
            if device is not None
            else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        )
        self._pipeline = None
        self._last_prompt = None
        self._lang_code = self._resolve_lang_code(kwargs.get("lang_code", "a"))
        # Queue of audio chunks waiting to be delivered
        self._audio_queue: deque[torch.Tensor] = deque()

    def _ensure_initialized(self):
        """Lazy-load the Kokoro pipeline on first use."""
        if self._pipeline is not None:
            return

        logger.info("Loading Kokoro TTS model (lang_code=%s)...", self._lang_code)
        from kokoro import KPipeline

        self._pipeline = KPipeline(lang_code=self._lang_code)
        logger.info("Kokoro TTS model loaded successfully")

    def prepare(self, **kwargs):
        """No video input required for TTS."""
        return None

    def __call__(self, **kwargs) -> dict | None:
        """Generate or deliver speech audio from text prompts.

        When a new prompt arrives, generates all audio and queues it in
        sentence-sized chunks. Each subsequent call delivers one chunk
        until the queue is drained, then waits for a new prompt.
        """
        # If we have queued audio chunks, deliver the next one
        if self._audio_queue:
            chunk = self._audio_queue.popleft()
            return {
                "audio": chunk,
                "audio_sample_rate": SAMPLE_RATE,
            }

        prompts = kwargs.get("prompts")
        if not prompts:
            time.sleep(0.05)
            return None

        # Extract text from the prompts structure
        text = self._extract_text(prompts)
        if not text:
            time.sleep(0.05)
            return None

        # Only generate when the prompt changes
        if text == self._last_prompt:
            time.sleep(0.05)
            return None

        self._ensure_initialized()
        self._last_prompt = text

        voice = self._resolve_voice(kwargs.get("voice", "af_heart"))
        speed = kwargs.get("speed", 1.0)

        logger.info(
            "Generating speech: voice=%s, speed=%.1f, text=%r",
            voice,
            speed,
            text[:80],
        )

        try:
            for _graphemes, _phonemes, audio in self._pipeline(
                text, voice=voice, speed=speed
            ):
                if audio is None:
                    continue
                # Split large chunks to stay within WebRTC buffer limits
                self._enqueue_audio(audio)

            if not self._audio_queue:
                logger.warning("Kokoro produced no audio for text: %r", text[:80])
                return None

            total_samples = sum(c.shape[1] for c in self._audio_queue)
            logger.info(
                "Generated %.2fs of audio in %d chunks",
                total_samples / SAMPLE_RATE,
                len(self._audio_queue),
            )

            # Deliver the first chunk immediately
            chunk = self._audio_queue.popleft()
            return {
                "audio": chunk,
                "audio_sample_rate": SAMPLE_RATE,
            }

        except Exception:
            logger.exception("Error generating speech")
            return None

    def _enqueue_audio(self, audio):
        """Split audio into chunks and add to the delivery queue.

        Args:
            audio: Audio data as torch.Tensor or numpy array.
        """
        if isinstance(audio, torch.Tensor):
            audio_t = audio.detach().clone()
        else:
            audio_t = torch.from_numpy(np.array(audio, dtype=np.float32))

        if audio_t.ndim == 1:
            # Split 1D audio into max-sized chunks
            total = audio_t.shape[0]
            offset = 0
            while offset < total:
                end = min(offset + MAX_CHUNK_SAMPLES, total)
                chunk = audio_t[offset:end].unsqueeze(0)  # (1, samples)
                self._audio_queue.append(chunk)
                offset = end
        else:
            self._audio_queue.append(audio_t)

    @staticmethod
    def _resolve_voice(voice: str) -> str:
        """Resolve display label to Kokoro voice ID, or pass through if already an ID."""
        from .schema import VOICE_TO_ID

        return VOICE_TO_ID.get(voice, voice)

    @staticmethod
    def _resolve_lang_code(lang: str) -> str:
        """Resolve display label to Kokoro lang code, or pass through if already a code."""
        from .schema import LANG_TO_CODE

        return LANG_TO_CODE.get(lang, lang)

    @staticmethod
    def _extract_text(prompts) -> str:
        """Extract text from the prompts data structure.

        Prompts can be:
        - A list of dicts with "text" key: [{"text": "hello", ...}]
        - A list of strings: ["hello"]
        - A string: "hello"
        """
        if isinstance(prompts, str):
            return prompts.strip()

        if isinstance(prompts, list) and len(prompts) > 0:
            first = prompts[0]
            if isinstance(first, dict):
                return first.get("text", "").strip()
            if isinstance(first, str):
                return first.strip()

        return ""
