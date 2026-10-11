# AIGC character skill 2.0

Chinese character acting direction plus an optional end-to-end character-video production workflow. Quick prompt requests stay text-only; explicit production or finishing requests continue to reviewable local media.

## Included

- [Character-video product PRD](docs/PRD-character-video-production.md) and [The Drunken Beauty case study](docs/PRD-guifei-mv.md).
- Six integrated skill families: HyperFrames, video-use, Remotion Skills, Generative Media Skills, VideoCut/chengfeng-videocut-skills and a dedicated Seedance 2.5 skill. [196 pinned public module entries](config/upstream-skills.lock.json); fetch locally on demand.
- Working optional VOICEVOX and loopback-only ComfyUI CLI/MCP adapters migrated from anime-video-skill.
- Configurable FFmpeg finishing: exact-duration concatenation, CFR, master audio or quiet generated-audio mixing, titles, bilingual ASS/SRT, deterministic captions, decoded AAC peak correction and technical QA.
- All original acting references, ten scenarios/twelve prompts and prompt validation retained.

The skill is not a standalone generation model. Provider accounts, models and runtimes are separate. Prompt/source installation is not runtime validation or perceptual acceptance.

## Install

```bash
git clone https://github.com/Simonxz578/aigc-character-skill.git ~/.codex/skills/aigc-character-skill
```

Preserve local changes before updating. Start a new session and use `$aigc-character-skill`. Prompt checks require Python3.9+; optional media tools require Python3.10+, FFmpeg/ffprobe and their stated dependencies.

```bash
python -m pip install -e '.[render]'
python scripts/integrations.py sync --family all
python scripts/integrations.py resolve --module seedance-2-5
aigc-character-finish project/production.json --dry-run
aigc-character-finish project/production.json
# Optional official SDK wrapper:
python -m pip install -e '.[mcp,render]'
aigc-character-mcp
```

The source-cache installer pins SHAs, preserves relative references, never overwrites unknown caches, executes no upstream installers and enables no paid provider. External sources are not redistributed as MIT.

Relative media paths resolve from the configuration file. [Example configuration](examples/guifei/production.json) deliberately excludes song lyrics and media; supply your own files, fonts and checked caption text. ASS is burned directly when libass is present; auto mode explicitly records deterministic Pillow-plate fallback. New outputs refuse to overwrite an existing final by default.

## Verification and limitations

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

[Release validation](docs/release-validation-v2.md) distinguishes actual local render/voice/source checks from untested external runtimes. The historical Guifei output passed technical checks; sung words and the subjective music mix remain not listening-verified. Wan5B has not passed character-motion acceptance, and Wan14B/LTX2.5 remain untested.

See the [Chinese documentation](README.md), [migration record](docs/migration-from-anime.md) and [third-party notices](THIRD_PARTY_NOTICES.md). Original code/docs are MIT; songs, photos, generated clips, weights and voiceprints are excluded. Native model and runtime licenses remain independent.
