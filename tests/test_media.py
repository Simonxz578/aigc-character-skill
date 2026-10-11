import unittest,sys,tempfile,json,subprocess,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from aigc_character_media.finishing import validate,finish,probe,encoded_peak
from aigc_character_media.local_video import LocalVideoProvider
from aigc_character_media.local_voice import voice_preset,synthesize
from unittest.mock import patch

class ContractTests(unittest.TestCase):
 def test_remote_cloud_redirect_credentials_and_api_nodes_rejected(self):
  for u in ['https://comfy.cloud','http://192.168.1.2:8188','http://secret@localhost:8188','http://127.0.0.1.evil.test:8188']:
   with self.assertRaises(ValueError):LocalVideoProvider(u)
  with self.assertRaises(ValueError):LocalVideoProvider.validate({'1':{'class_type':'PaidVideoAPI','inputs':{}}})
 def test_voice_slot_and_output_validation_happen_before_native_load(self):
  with patch('aigc_character_media.local_voice.health') as h:
   for a in [{'text':'','speaker':'male'},{'text':'a','speaker':'other'},{'text':'a','speaker':'male','max_duration_sec':0},{'text':'a','speaker':'male','output_dir':'/tmp/escape'}]:
    with self.assertRaises(ValueError):synthesize(**a)
   h.assert_not_called()
  p=voice_preset('male');p['pitch']=12;self.assertEqual(voice_preset('male')['pitch'],0)

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
class RenderTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
  subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','color=c=red:s=160x288:r=24','-f','lavfi','-i','sine=frequency=800:sample_rate=48000','-t','1','-c:v','libx264','-c:a','aac',str(self.p/'shot.mp4')],check=True)
  subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=400:sample_rate=48000:duration=2','-af','volume=24','-c:a','pcm_f32le',str(self.p/'song.wav')],check=True)
  self.c={'spec':{'width':160,'height':288,'fps':30,'duration':2},'shots':[{'file':'shot.mp4','duration':1},{'file':'shot.mp4','duration':1}],'audio':{'file':'song.wav','mode':'mix_generated','master_gain_db':0,'generated_gain_db':-18,'max_decoded_peak_dbfs':-3},'output_dir':'result'}
 def tearDown(self):self.tmp.cleanup()
 def test_frames_audio_mix_peak_budget_decode_and_no_overwrite(self):
  self.assertGreater(encoded_peak(self.p/'song.wav'),1)
  f=self.p/'production.json';f.write_text(json.dumps(self.c));r=finish(f);q=r['qa'];v=probe(self.p/'result/final.mp4')['streams'][0]
  self.assertEqual((v['r_frame_rate'],v['nb_frames']),('30/1','60'));self.assertLessEqual(q['decoded_sample_peak'],10**(-3/20));self.assertLess(q['mix_total_gain'],1);self.assertFalse(q['measured_true_peak']);self.assertEqual(q['review']['listening'],'not_verified')
  with self.assertRaises(ValueError):finish(f)
 def test_invalid_timeline_caption_audio_mode_and_short_source(self):
  for key,value in [('mode','cloud'),('max_decoded_peak_dbfs',float('nan'))]:
   c=json.loads(json.dumps(self.c));c['audio'][key]=value
   with self.assertRaises(ValueError):validate(c,self.p)
  c=json.loads(json.dumps(self.c));c['shots'][0]['duration']=.5
  with self.assertRaises(ValueError):validate(c,self.p)
  c=json.loads(json.dumps(self.c));c['captions']=[{'start':0,'end':1.2,'zh':'A'},{'start':1,'end':2,'zh':'B'}]
  with self.assertRaises(ValueError):validate(c,self.p)
  c=json.loads(json.dumps(self.c));c['shots']=[{'file':'shot.mp4','duration':2}];f=self.p/'bad.json';f.write_text(json.dumps(c))
  with self.assertRaisesRegex(ValueError,'shorter'):finish(f,dry_run=True)
 def test_bilingual_overlay_and_editable_subtitles(self):
  c=json.loads(json.dumps(self.c));c['output_dir']='caption_result';c['title']={'start':0,'end':.7,'lines':['人物MV','Character film']};c['captions']=[{'start':0,'end':1,'zh':'初见','en':'First meeting'},{'start':1,'end':2,'zh':'再见','en':'Until we meet again'}]
  c['caption_backend']='pillow';c['fonts']={'cjk':'/System/Library/Fonts/Hiragino Sans GB.ttc','latin':'/System/Library/Fonts/Supplemental/Times New Roman.ttf'}
  if not all(Path(v).is_file() for v in c['fonts'].values()):self.skipTest('CJK/Latin test fonts unavailable')
  f=self.p/'captions.json';f.write_text(json.dumps(c));r=finish(f)
  self.assertEqual(r['qa']['caption_backend'],'pillow');self.assertTrue((self.p/'caption_result/subtitles/bilingual.ass').is_file());self.assertEqual(probe(self.p/'caption_result/final.mp4')['streams'][0]['nb_frames'],'60')

if __name__=='__main__':unittest.main()
