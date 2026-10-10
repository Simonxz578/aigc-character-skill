# AIGC character skill

A Chinese-first character acting director skill: turn a short story request into a copy-ready video prompt with motivation, gaze, breath, gestures, prop ownership, dialogue and a continuous timeline.

This is a text-authoring skill, **not a video generation model**. It needs no GPU, API key or paid service. Platform labels such as Seedance 2.5/2.0, Kling, Veo and Sora describe prompt targets, not verified current capabilities.

## Install in Codex

With an absent destination directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Simonxz578/aigc-character-skill.git ~/.codex/skills/aigc-character-skill
```

Start a new Codex session. Use `$aigc-character-skill` followed by a natural-language scene. It also supports implicit discovery. For a custom CODEX_HOME, install under its `skills/` directory. Review local modifications before updating with `git pull --ff-only`.

Examples: a restrained 15-second emotional performance; a two-person notebook handoff; revise only one character's vocal delivery while preserving everything else.

## Contents

Skill entry point, UI metadata, nine focused references, ten original examples (twelve copy-ready prompts), a standard-library validator and regression tests. Default output is natural Chinese prose. Concise, standard, cinematic and custom length modes support seven output styles.

```bash
python3 scripts/validate_prompt.py prompt.txt --duration 15 --max-chars 5000 --json
python3 -m unittest discover -s tests -v
```

Python 3.9+; no dependencies. Counts Unicode code points including spaces and newlines. Semantic warnings exit0; input/argument failures exit2. Heuristics do not prove acting quality or model compliance. See [Chinese documentation](README.md) and [forward-test records](tests/forward-results.md).

v1.0.0 local verification: 44 automated tests passed, skill frontmatter validated, and 12 independent natural-language calls across 10 groups completed. Missing-reference cases test text handling only; the overlong recital case tests conflict handling rather than fulfilling an impossible 15-second constraint.

MIT applies to original repository text and code. No private references, transcripts, portraits, voiceprints or third-party media are distributed. Layout informed by [Agent Skills](https://agentskills.io/specification) and [OpenAI's skills documentation](https://developers.openai.com/plugins/build/skills).
