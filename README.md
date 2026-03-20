# Kokoro TTS

A [Daydream Scope](https://daydream.live) plugin that adds real-time text-to-speech using the [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) model (82M params). Type text in the prompt box and hear it spoken aloud via WebRTC audio streaming.

## Features

- **50+ voices** across 9 languages (American English, British English, Spanish, French, Hindi, Italian, Japanese, Portuguese, Mandarin Chinese)
- **Adjustable speed** from 0.5x to 2.0x
- **Sentence-level chunking** for smooth, low-latency audio delivery over WebRTC

## Installation

Install directly from GitHub in the Scope UI or CLI:

```
https://github.com/leszko/scope-kokoro-tts
```

Or via the CLI:

```bash
uv run daydream-scope install https://github.com/leszko/scope-kokoro-tts
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Voice | select | Heart (US Female) | Voice preset for speech synthesis |
| Speed | slider (0.5–2.0) | 1.0 | Speech speed multiplier |
| Language | select (load-time) | American English | Language for text processing and phonemization |

## Usage

1. Install the plugin and restart Scope.
2. Select **Kokoro TTS** from the pipeline list.
3. Choose a language and click **Start**.
4. Type text in the prompt box — audio plays back through WebRTC.

## Development

Clone and install locally for development:

```bash
git clone https://github.com/leszko/scope-kokoro-tts
uv run daydream-scope install -e ./scope-kokoro-tts
```

After making changes, use the **Reload** button in the Plugins settings tab.

## License

See [LICENSE](LICENSE) for details.
