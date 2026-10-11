# Sources and third-party notices

## Original / migrated MIT code

The original character directing material and new orchestration/finishing code are MIT under LICENSE. local_voice.py, local_video.py and io.py are migrated from Simonxz578/anime-video-skill at 788d014 (MIT). Source paths, scope and exclusions are recorded in config/migration-provenance.json. The owner and existing copyright notice are preserved.

## External skills (not redistributed)

The six families below are integrated using pinned repository URLs, module paths and an optional local source cache. Their documents/code are NOT included in the public release ZIP or re-licensed under this repository's MIT license. The source-cache tool preserves the original repository tree and available notices.

| Repository | Reported source license at checked SHA | Note |
|---|---|---|
| heygen-com/hyperframes | Apache-2.0 | CLI/runtime/license and notices remain upstream |
| browser-use/video-use | MIT | Cloud transcription examples are optional |
| remotion-dev/skills | No root SPDX/license identified | No copying into this public repository; check current upstream terms before reuse |
| calesthio/generative-media-skills | MIT | Provider service/model terms independent |
| Agentchengfeng/chengfeng-videocut-skills | Apache-2.0 | Original NOTICE.md remains in cached source; Runtime separate |
| Standed/Seedance2.5 | MIT | Independent community skill, not ByteDance's official software |

Exact SHAs and source entries are in config/upstream-skills.lock.json. The historical dexhunter/seedance2-skill (MIT) is recorded only in the inherited anime lockfile; it is not relabeled as2.5. sjinn-ai/seedance2.5-skills was reviewed as an alternative; no root license was identified and it is not vendored.

## Media / runtimes

VOICEVOX Core and each voice model/character have their own terms. The example presets require VOICEVOX:雨晴はう / VOICEVOX:玄野武宏 credits. No living performer voiceprint is copied or claimed. ComfyUI, Wan/LTX weights, FFmpeg builds, fonts, HyperFrames, Remotion, transcription engines and cloud providers retain their own licensing and availability conditions. No native binaries or model weights are redistributed.

The Guifei PRD documents processing of user-provided media. It distributes no commercial song file/complete lyrics, dance reference, portrait, video, browser screenshot, private project id, login details or personal filesystem paths. Historical QA JSON is a sanitized numerical summary. Publication of source docs does not publish the user's original media.
