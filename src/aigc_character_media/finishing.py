"""Configurable fixed-duration FFmpeg finishing, captions and measured media QA."""
from __future__ import annotations
import argparse,array,hashlib,json,math,os,re,subprocess
from pathlib import Path

FF=os.environ.get('FFMPEG_BIN','ffmpeg')
FP=os.environ.get('FFPROBE_BIN','ffprobe')

def probe(path):
    return json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(path)]))

def number(v,name,lo,hi):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not lo<=v<=hi:
        raise ValueError(f'{name} must be finite in [{lo}, {hi}]')
    return v

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def validate(config,base):
    c=json.loads(json.dumps(config));spec=c['spec']
    if c.get('schema_version',1)!=1:raise ValueError('Unsupported production schema version')
    for k in ['width','height','fps']:
        number(spec[k],k,1,8192 if k!='fps' else 120)
        if int(spec[k])!=spec[k]:raise ValueError(f'{k} must be an integer')
        spec[k]=int(spec[k])
    if spec['width']%2 or spec['height']%2:raise ValueError('H.264 dimensions must be even')
    duration=number(spec['duration'],'duration',.1,3600)
    if abs(duration*spec['fps']-round(duration*spec['fps']))>1e-6:raise ValueError('duration must be frame-aligned')
    shots=c.get('shots')
    if not isinstance(shots,list) or not shots:raise ValueError('shots must be a nonempty list')
    def resolve(v):return str((base/str(v)).resolve())
    for s in shots:
        s['duration']=number(s['duration'],'shot duration',.01,3600)
        s['trim_start']=number(s.get('trim_start',0),'trim_start',0,3600)
        if abs(s['duration']*spec['fps']-round(s['duration']*spec['fps']))>1e-6:raise ValueError('shot durations must be frame-aligned')
        s['file']=resolve(s['file'])
        if not Path(s['file']).is_file():raise ValueError(f"Missing shot: {s['file']}")
    if abs(sum(s['duration'] for s in shots)-duration)>1e-6:raise ValueError('Shot durations do not equal target duration')
    a=c.get('audio')
    if not isinstance(a,dict) or a.get('mode','replace') not in ['replace','mix_generated']:raise ValueError('audio.mode must be replace or mix_generated')
    a['mode']=a.get('mode','replace');a['file']=resolve(a['file'])
    if not Path(a['file']).is_file():raise ValueError('Missing master audio')
    for k,default,lo,hi in [('master_gain_db',0,-80,6),('generated_gain_db',-24,-80,0),('boundary_fade_sec',.2,0,2),('max_decoded_peak_dbfs',-1.5,-30,0)]:a[k]=number(a.get(k,default),k,lo,hi)
    last=0
    for s in c.get('captions',[]):
        number(s['start'],'caption start',0,duration);number(s['end'],'caption end',0,duration)
        if s['end']<=s['start'] or s['start']<last:raise ValueError('Captions overlap or have invalid intervals')
        last=s['end']
        if not any(isinstance(s.get(k),str) and s[k].strip() for k in ['zh','en']):raise ValueError('Empty caption')
    t=c.get('title')
    if t:
        number(t['start'],'title start',0,duration);number(t['end'],'title end',0,duration)
        if t['end']<=t['start'] or not t.get('lines') or len(t['lines'])>6:raise ValueError('Invalid title interval/lines')
        if not all(isinstance(s,str) and s.strip() for s in t['lines']):raise ValueError('Invalid title text')
    if t or c.get('captions'):
        for k in ['cjk','latin']:
            c.setdefault('fonts',{})[k]=resolve(c.get('fonts',{}).get(k,''))
            if not Path(c['fonts'][k]).is_file():raise ValueError(f'Missing {k} font path')
    if c.get('caption_backend','auto') not in ['auto','ass','pillow']:raise ValueError('Unknown caption backend')
    c['output_dir']=resolve(c.get('output_dir','outputs/finish'))
    return c

def subtitle_time(t,ass=False):
    n=round(t*(100 if ass else 1000));unit=100 if ass else 1000
    return f'{n//(unit*3600):01}:{n//(unit*60)%60:02}:{n//unit%60:02}.{n%unit:02}' if ass else f'{n//(unit*3600):02}:{n//(unit*60)%60:02}:{n//unit%60:02},{n%unit:03}'

def captions(c,out):
    from PIL import Image,ImageDraw,ImageFont
    W,H=c['spec']['width'],c['spec']['height'];folder=out/'subtitles';folder.mkdir(exist_ok=True)
    cf=ImageFont.truetype(c['fonts']['cjk'],max(10,round(W*38/720)))
    ef=ImageFont.truetype(c['fonts']['latin'],max(8,round(W*27/720)))
    ass=['[Script Info]','ScriptType: v4.00+','WrapStyle: 0',f'PlayResX: {W}',f'PlayResY: {H}','', '[V4+ Styles]', 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',f'Style: Chinese,{cf.getname()[0]},{cf.size},&H00F7F8FF,&H000000FF,&H00150F0A,&HAA000000,0,0,0,0,100,100,0,0,1,2,0,2,{round(W*.08)},{round(W*.08)},{round(H*.125)},1',f'Style: English,{ef.getname()[0]},{ef.size},&H00DFEBF3,&H000000FF,&H00150F0A,&HAA000000,0,0,0,0,100,100,0,0,1,1,0,2,{round(W*.08)},{round(W*.08)},{round(H*.18)},1','', '[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    files={'zh-CN':[],'en':[],'bilingual':[]};plates=[]
    for i,s in enumerate(c.get('captions',[])):
        z,e=s.get('zh',''),s.get('en','');start,end=subtitle_time(s['start']),subtitle_time(s['end'])
        for key,text in [('zh-CN',z),('en',e),('bilingual','\n'.join(x for x in [e,z] if x))]:
            if text:files[key].append(f'{len(files[key])+1}\n{start} --> {end}\n{text}\n')
        im=Image.new('RGBA',(W,round(H*.2)));d=ImageDraw.Draw(im)
        def wrap(text,font):
            parts=text.split() if ' ' in text else list(text);lines=[''];sep=' ' if ' ' in text else ''
            for word in parts:
                trial=(lines[-1]+sep+word).strip()
                if d.textlength(trial,font=font)>W*.84 and lines[-1]:lines.append(word)
                else:lines[-1]=trial
            return lines
        zh_count=len(wrap(z,cf)) if z else 0
        for key,text,font in [('Chinese',z,cf),('English',e,ef)]:
            if text:
                safe=text.replace('{','｛').replace('}','｝').replace('\n','\\N')
                margin=round(H*.078) if key=='Chinese' and zh_count==2 else (round(H*.17) if key=='English' and len(wrap(e,ef))==2 else 0)
                ass.append(f"Dialogue: 0,{subtitle_time(s['start'],True)},{subtitle_time(s['end'],True)},{key},,0,0,{margin},,{safe}")
        for text,font,y,step in [(e,ef,H*.06,H*.0265),(z,cf,H*(.14 if zh_count==2 else .112),H*.035)]:
            if not text:continue
            lines=wrap(text,font)
            if len(lines)>2:raise ValueError('Caption too long; split into shorter screens')
            for j,line in enumerate(lines):
                if d.textlength(line,font=font)>W*.9:raise ValueError('Caption token wider than safe area')
                d.text((W/2,y-(len(lines)-1)*step/2+j*step),line,font=font,anchor='mm',fill=(255,247,231,255),stroke_width=max(1,round(W/360)),stroke_fill=(12,13,18,235))
        f=folder/f'caption_{i:03}.png';im.save(f);plates.append(f)
    for k,v in files.items():(folder/(k+'.srt')).write_text('\n'.join(v),encoding='utf-8')
    (folder/'bilingual.ass').write_text('\n'.join(ass)+'\n',encoding='utf-8')
    title=None
    if c.get('title'):
        t=c['title'];n=len(t['lines']);im=Image.new('RGBA',(W,round(H*.36)));d=ImageDraw.Draw(im)
        for i,line in enumerate(t['lines']):
            font=ImageFont.truetype(c['fonts']['cjk'] if i==0 or i>1 else c['fonts']['latin'],max(10,round(W*([60,27,23,20,20,20][i])/720)))
            if d.textlength(line,font=font)>W*.9:raise ValueError('Title wider than safe area')
            y=H*.05 if i==0 else H*(.12+(i-1)*.045)
            d.text((W/2,y),line,font=font,anchor='mm',fill=(251,225,174,255),stroke_width=max(1,round(W/720)),stroke_fill=(26,12,5,210))
        title=folder/'title.png';im.save(title)
    return plates,title

def encoded_peak(file):
    peak=0
    # Check both stereo channels; a mono downmix could hide an overload.
    proc=subprocess.Popen([FF,'-v','error','-i',str(file),'-vn','-ac','2','-ar','48000','-f','f32le','-'],stdout=subprocess.PIPE)
    while True:
        b=proc.stdout.read(262144)
        if not b:break
        a=array.array('f');a.frombytes(b);peak=max(peak,max((abs(v) for v in a),default=0))
    if proc.wait():raise RuntimeError('Audio decode failed')
    return peak

def finish(config_path,overwrite=False,dry_run=False):
    path=Path(config_path).resolve();c=validate(json.loads(path.read_text()),path.parent)
    probes=[]
    for s in c['shots']:
        r=probe(s['file']);v=next((v for v in r['streams'] if v['codec_type']=='video'),None)
        if not v:raise ValueError('Shot has no video')
        available=float(v.get('duration',r['format'].get('duration',0)))
        if available+.002<s['trim_start']+s['duration']:raise ValueError('Source shot shorter than its slot; no freeze or time stretch applied')
        probes.append(r)
    master=probe(c['audio']['file'])
    if not any(s['codec_type']=='audio' for s in master['streams']):raise ValueError('Master file has no audio')
    master_audio=next(s for s in master['streams'] if s['codec_type']=='audio')
    if float(master_audio.get('duration',master['format']['duration']))+.03<c['spec']['duration']:raise ValueError('Master audio shorter than video; no loop applied')
    if dry_run:return {'status':'validated_inputs','config':c,'source_probes':probes,'runtime_executed':False}
    out=Path(c['output_dir']);final=out/'final.mp4'
    if final.exists() and not overwrite:raise ValueError('Final already exists; use a new directory or explicit --overwrite')
    for d in ['','qa','subtitles']:(out/d).mkdir(parents=True,exist_ok=True)
    manifest={'config':c,'inputs':[{'path':f,'sha256':sha(Path(f))} for f in [s['file'] for s in c['shots']]+[c['audio']['file']]],'commands':[]}
    def run(cmd):
        cmd=list(map(str,cmd));manifest['commands'].append(cmd)
        with (out/'qa/commands.log').open('a') as l:subprocess.run(cmd,cwd=out,stdout=l,stderr=l,check=True)
    W,H,fps,duration=[c['spec'][k] for k in ['width','height','fps','duration']];n=len(c['shots'])
    audio=c['audio'];cmd=[FF,'-hide_banner','-y','-filter_complex_threads','2']
    for s in c['shots']:cmd+=['-i',s['file']]
    cmd+=['-i',audio['file']];f=[]
    for i,s in enumerate(c['shots']):
        f.append(f"[{i}:v]trim=start={s['trim_start']}:duration={s['duration']},setpts=PTS-STARTPTS,fps={fps},scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v{i}]")
    f.append(''.join(f'[v{i}]' for i in range(n))+f'concat=n={n}:v=1:a=0[picture]')
    picture=out/'picture.mp4'
    run(cmd+['-filter_complex',';'.join(f),'-map','[picture]','-an','-c:v','libx264','-crf','18','-preset','fast','-threads','4','-frames:v',str(round(duration*fps)),'-t',str(duration),picture])
    # Separate PCM mix prevents repeated picture encoding after an AAC headroom repair.
    f=[]
    for i,s in enumerate(c['shots']):
        fade=min(audio['boundary_fade_sec'],s['duration']/2)
        if audio['mode']=='mix_generated' and any(v['codec_type']=='audio' for v in probes[i]['streams']):
            f.append(f"[{i}:a]atrim=start={s['trim_start']}:duration={s['duration']},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={s['duration']},atrim=duration={s['duration']},volume={audio['generated_gain_db']}dB,afade=t=in:d={fade},afade=t=out:st={s['duration']-fade}:d={fade}[a{i}]")
        else:f.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={s['duration']}[a{i}]")
    f.append(''.join(f'[a{i}]' for i in range(n))+f'concat=n={n}:v=0:a=1[generated]')
    f.append(f"[{n}:a]atrim=duration={duration},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume={audio['master_gain_db']}dB[song]")
    f.append('[song][generated]amix=inputs=2:duration=first:normalize=0[mix]')
    pcm=out/'mix.wav'
    run(cmd+['-filter_complex',';'.join(f),'-map','[mix]','-c:a','pcm_f32le','-t',str(duration),pcm])
    styled=picture;backend='none'
    if c.get('title') or c.get('captions'):
        plates,title=captions(c,out)
        available=subprocess.check_output([FF,'-hide_banner','-filters'],text=True,stderr=subprocess.DEVNULL)
        has_ass=bool(re.search(r'\bsubtitles\s+V',available));requested=c.get('caption_backend','auto')
        if requested=='ass' and not has_ass:raise RuntimeError('Strict ASS burn-in requested but this FFmpeg has no subtitles/libass filter')
        backend='ass' if requested!='pillow' and has_ass else 'pillow'
        scmd=[FF,'-hide_banner','-y','-filter_complex_threads','2','-i',picture];f=[];last='0:v';nextinput=1
        if title:
            scmd+=['-loop','1','-framerate',str(fps),'-t',str(duration),'-i',title];t=c['title'];fade=min(.2,(t['end']-t['start'])/3)
            f.append(f"[1:v]format=rgba,fade=t=in:st={t['start']}:d={fade}:alpha=1,fade=t=out:st={t['end']-fade}:d={fade}:alpha=1[title]")
            f.append(f"[{last}][title]overlay=0:{round(H*.03)}:enable='gte(t,{t['start']})*lt(t,{t['end']})':eof_action=pass[vt]");last='vt';nextinput+=1
        if c.get('captions') and backend=='ass':
            f.append(f"[{last}]subtitles=filename=subtitles/bilingual.ass[capass]");last='capass'
        elif c.get('captions'):
            for i,(s,plate) in enumerate(zip(c['captions'],plates)):
                scmd+=['-i',plate];tag=f'cap{i}'
                f.append(f"[{last}][{nextinput}:v]overlay=0:{round(H*.75)}:enable='gte(t,{s['start']})*lt(t,{s['end']})':eof_action=repeat[{tag}]");last=tag;nextinput+=1
        styled=out/'styled_picture.mp4'
        run(scmd+['-filter_complex',';'.join(f),'-map',f'[{last}]','-an','-c:v','libx264','-crf','18','-preset','fast','-threads','4','-pix_fmt','yuv420p','-frames:v',str(round(duration*fps)),'-t',str(duration),styled])
    gain=1.;limit=10**(audio['max_decoded_peak_dbfs']/20)
    for attempt in range(3):
        run([FF,'-hide_banner','-y','-i',styled,'-i',pcm,'-map','0:v:0','-map','1:a:0','-c:v','copy','-af',f'volume={gain:.10f}','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',str(duration),'-movflags','+faststart',final])
        peak=encoded_peak(final)
        if peak<=limit:break
        gain*=limit/max(peak,1e-10)*.97
    else:raise RuntimeError('Could not satisfy encoded audio peak budget')
    r=probe(final);v=next(s for s in r['streams'] if s['codec_type']=='video');a=next(s for s in r['streams'] if s['codec_type']=='audio')
    assert (int(v['width']),int(v['height']),v['r_frame_rate'],int(v['nb_frames']))==(W,H,f'{fps}/1',round(fps*duration))
    assert abs(float(r['format']['duration'])-duration)<=1/fps and abs(float(a['duration'])-duration)<.03
    run([FF,'-v','error','-i',final,'-f','null','-'])
    (out/'qa/probe.json').write_text(json.dumps(r,indent=2))
    qa={'technical_pass':True,'duration_sec':duration,'frames':int(v['nb_frames']),'decoded_sample_peak':peak,'sample_peak_budget_dbfs':audio['max_decoded_peak_dbfs'],'measured_true_peak':False,'mix_total_gain':gain,'caption_backend':backend,'caption_backend_degraded':backend=='pillow' and c.get('caption_backend','auto')=='auto','review':c.get('review',{'identity':'not_verified','lyrics':'not_verified','listening':'not_verified'}),'sha256':sha(final)}
    manifest['qa']=qa;(out/'render_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    try:
        from PIL import Image,ImageDraw
        thumbs=[]
        for i in range(min(len(c['shots']),10)):
            t=sum(s['duration'] for s in c['shots'][:i])+c['shots'][i]['duration']/2;f=out/'qa'/f'frame_{i:02}.jpg'
            run([FF,'-v','error','-y','-ss',str(t),'-i',final,'-frames:v','1','-q:v','2',f]);im=Image.open(f).convert('RGB');im.thumbnail((240,round(240*H/W)));thumbs.append(im)
        th=round(240*H/W);sheet=Image.new('RGB',(240*min(5,len(thumbs)),(th+24)*math.ceil(len(thumbs)/5)),(22,20,23));d=ImageDraw.Draw(sheet)
        for i,im in enumerate(thumbs):x=i%5*240;y=i//5*(th+24);sheet.paste(im,(x,y));d.text((x+8,y+th+3),f'Shot {i+1:02}',fill='white')
        sheet.save(out/'qa/contact_sheet.jpg',quality=92)
    except ImportError:qa['contact_sheet']='Pillow unavailable; encoded-frame evidence omitted'
    manifest['qa']=qa;(out/'render_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(out/'qa/validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
    return {'status':'rendered_technical_pass','video':str(final),'qa':qa}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('config',type=Path);ap.add_argument('--overwrite',action='store_true');ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
    try:print(json.dumps(finish(a.config,a.overwrite,a.dry_run),ensure_ascii=False,indent=2))
    except (ValueError,KeyError,subprocess.CalledProcessError,RuntimeError) as e:ap.exit(2,f'{e}\n')
if __name__=='__main__':main()
