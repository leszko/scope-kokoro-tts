from typing import Literal

from pydantic import Field

from scope.core.pipelines.base_schema import BasePipelineConfig, ModeDefaults, ui_field_config

Language = Literal[
    "American English",
    "British English",
    "Spanish",
    "French",
    "Hindi",
    "Italian",
    "Japanese",
    "Portuguese",
    "Mandarin Chinese",
]

LANG_TO_CODE: dict[str, str] = {
    "American English": "a",
    "British English": "b",
    "Spanish": "e",
    "French": "f",
    "Hindi": "h",
    "Italian": "i",
    "Japanese": "j",
    "Portuguese": "p",
    "Mandarin Chinese": "z",
}

# Voice enum: "Display Label" -> kokoro voice id
# Format: "{Name} ({region} {gender})"
Voice = Literal[
    # American English
    "Alloy (US Female)",
    "Aoede (US Female)",
    "Bella (US Female)",
    "Heart (US Female)",
    "Jessica (US Female)",
    "Kore (US Female)",
    "Nicole (US Female)",
    "Nova (US Female)",
    "River (US Female)",
    "Sarah (US Female)",
    "Sky (US Female)",
    "Adam (US Male)",
    "Echo (US Male)",
    "Eric (US Male)",
    "Fenrir (US Male)",
    "Liam (US Male)",
    "Michael (US Male)",
    "Onyx (US Male)",
    "Puck (US Male)",
    "Santa (US Male)",
    # British English
    "Alice (UK Female)",
    "Emma (UK Female)",
    "Isabella (UK Female)",
    "Lily (UK Female)",
    "Daniel (UK Male)",
    "Fable (UK Male)",
    "George (UK Male)",
    "Lewis (UK Male)",
    # Spanish
    "Dora (ES Female)",
    "Alex (ES Male)",
    "Santa (ES Male)",
    # French
    "Siwis (FR Female)",
    # Hindi
    "Alpha (HI Female)",
    "Beta (HI Female)",
    "Omega (HI Male)",
    "Psi (HI Male)",
    # Italian
    "Sara (IT Female)",
    "Nicola (IT Male)",
    # Japanese
    "Alpha (JA Female)",
    "Gongitsune (JA Female)",
    "Nezumi (JA Female)",
    "Tebukuro (JA Female)",
    "Kumo (JA Male)",
    # Portuguese
    "Dora (PT Female)",
    "Alex (PT Male)",
    "Santa (PT Male)",
    # Mandarin Chinese
    "Xiaobei (ZH Female)",
    "Xiaoni (ZH Female)",
    "Xiaoxiao (ZH Female)",
    "Xiaoyi (ZH Female)",
    "Yunjian (ZH Male)",
    "Yunxi (ZH Male)",
    "Yunxia (ZH Male)",
    "Yunyang (ZH Male)",
]

VOICE_TO_ID: dict[str, str] = {
    # American English
    "Alloy (US Female)": "af_alloy",
    "Aoede (US Female)": "af_aoede",
    "Bella (US Female)": "af_bella",
    "Heart (US Female)": "af_heart",
    "Jessica (US Female)": "af_jessica",
    "Kore (US Female)": "af_kore",
    "Nicole (US Female)": "af_nicole",
    "Nova (US Female)": "af_nova",
    "River (US Female)": "af_river",
    "Sarah (US Female)": "af_sarah",
    "Sky (US Female)": "af_sky",
    "Adam (US Male)": "am_adam",
    "Echo (US Male)": "am_echo",
    "Eric (US Male)": "am_eric",
    "Fenrir (US Male)": "am_fenrir",
    "Liam (US Male)": "am_liam",
    "Michael (US Male)": "am_michael",
    "Onyx (US Male)": "am_onyx",
    "Puck (US Male)": "am_puck",
    "Santa (US Male)": "am_santa",
    # British English
    "Alice (UK Female)": "bf_alice",
    "Emma (UK Female)": "bf_emma",
    "Isabella (UK Female)": "bf_isabella",
    "Lily (UK Female)": "bf_lily",
    "Daniel (UK Male)": "bm_daniel",
    "Fable (UK Male)": "bm_fable",
    "George (UK Male)": "bm_george",
    "Lewis (UK Male)": "bm_lewis",
    # Spanish
    "Dora (ES Female)": "ef_dora",
    "Alex (ES Male)": "em_alex",
    "Santa (ES Male)": "em_santa",
    # French
    "Siwis (FR Female)": "ff_siwis",
    # Hindi
    "Alpha (HI Female)": "hf_alpha",
    "Beta (HI Female)": "hf_beta",
    "Omega (HI Male)": "hm_omega",
    "Psi (HI Male)": "hm_psi",
    # Italian
    "Sara (IT Female)": "if_sara",
    "Nicola (IT Male)": "im_nicola",
    # Japanese
    "Alpha (JA Female)": "jf_alpha",
    "Gongitsune (JA Female)": "jf_gongitsune",
    "Nezumi (JA Female)": "jf_nezumi",
    "Tebukuro (JA Female)": "jf_tebukuro",
    "Kumo (JA Male)": "jm_kumo",
    # Portuguese
    "Dora (PT Female)": "pf_dora",
    "Alex (PT Male)": "pm_alex",
    "Santa (PT Male)": "pm_santa",
    # Mandarin Chinese
    "Xiaobei (ZH Female)": "zf_xiaobei",
    "Xiaoni (ZH Female)": "zf_xiaoni",
    "Xiaoxiao (ZH Female)": "zf_xiaoxiao",
    "Xiaoyi (ZH Female)": "zf_xiaoyi",
    "Yunjian (ZH Male)": "zm_yunjian",
    "Yunxi (ZH Male)": "zm_yunxi",
    "Yunxia (ZH Male)": "zm_yunxia",
    "Yunyang (ZH Male)": "zm_yunyang",
}


class KokoroTTSConfig(BasePipelineConfig):
    """Configuration for Kokoro text-to-speech pipeline.

    Generates speech audio from text prompts using the Kokoro TTS model (82M params).
    Audio is streamed via WebRTC at 24kHz.
    """

    pipeline_id = "kokoro-tts"
    pipeline_name = "Kokoro TTS"
    pipeline_description = (
        "Text-to-speech pipeline using Kokoro (82M params). "
        "Type text in the prompt box and hear it spoken. "
        "Supports multiple voices and adjustable speed."
    )
    pipeline_version = "1.0.0"

    produces_video = False
    produces_audio = True
    supports_prompts = True
    supports_cache_management = False

    modes = {"text": ModeDefaults(default=True)}

    voice: Voice = Field(
        default="Heart (US Female)",
        description="Voice preset for speech synthesis",
        json_schema_extra=ui_field_config(order=1, label="Voice"),
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed multiplier (0.5 = slow, 2.0 = fast)",
        json_schema_extra=ui_field_config(
            order=2,
            label="Speed",
            modulatable=True,
            modulatable_min=0.5,
            modulatable_max=2.0,
        ),
    )
    lang_code: Language = Field(
        default="American English",
        description="Language for text processing and phonemization",
        json_schema_extra=ui_field_config(
            order=3, is_load_param=True, label="Language"
        ),
    )
