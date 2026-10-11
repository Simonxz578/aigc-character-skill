#!/usr/bin/env python3
"""Report capability availability without credentials, model installation or network."""
import json,shutil,subprocess,importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]
r={'executables':{k:bool(shutil.which(k)) for k in ['ffmpeg','ffprobe','git','node']},'python_modules':{k:importlib.util.find_spec(k) is not None for k in ['PIL','numpy','voicevox_core','mcp']},'external_skills_cached':0,'runtime_validation':'not_performed','paid_fallback':False}
if r['executables']['ffmpeg']:
 f=subprocess.check_output(['ffmpeg','-hide_banner','-filters'],text=True,stderr=subprocess.DEVNULL);r['libass_subtitles_filter']=' subtitles ' in f
if (p/'.integrations/sources').exists():r['external_skills_cached']=sum(1 for q in (p/'.integrations/sources').rglob('SKILL.md'))
print(json.dumps(r,indent=2))
