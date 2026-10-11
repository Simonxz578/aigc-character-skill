#!/usr/bin/env python3
"""Resolve and optionally cache pinned external skills; never execute their installers."""
from pathlib import Path
import argparse,json,os,re,subprocess,tempfile,shutil
ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/'config/upstream-skills.lock.json'
def records():return json.loads(LOCK.read_text())['repositories']
def source_dir(cache,r):return cache/(r['repository'].replace('/','--')+'--'+r['commit'][:12])
def sync(r,cache):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',r['repository']) or not re.fullmatch(r'[0-9a-f]{40}',r['commit']):raise ValueError('Invalid repository or pinned SHA')
 dest=source_dir(cache,r);marker=dest/'.aigc-source.json'
 if dest.exists():
  if marker.is_file() and json.loads(marker.read_text()).get('commit')==r['commit']:return dest
  raise ValueError(f'Existing directory has no matching receipt; preserve it: {dest}')
 cache.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.fetch-',dir=cache) as td:
  work=Path(td)/'source';work.mkdir()
  def git(*args):subprocess.run(['git','-c','core.hooksPath=/dev/null',*args],cwd=work,check=True,stdout=subprocess.DEVNULL)
  git('init','-q');git('remote','add','origin',f"https://github.com/{r['repository']}.git")
  git('fetch','-q','--depth=1','--filter=blob:none','origin',r['commit'])
  dirs={m['path'] for m in r['modules']}
  if '.' not in dirs:
   git('sparse-checkout','init','--no-cone')
   patterns=['/*','!/*/']+['/'+d.strip('/')+'/' for d in sorted(dirs)]
   (work/'.git/info/sparse-checkout').write_text('\n'.join(patterns)+'\n')
  git('checkout','-q','--detach','FETCH_HEAD')
  sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip()
  if sha!=r['commit']:raise RuntimeError('Fetched SHA does not match lock')
  for m in r['modules']:
   if not (work/m['entrypoint']).is_file():raise RuntimeError(f"Missing pinned module: {m['entrypoint']}")
  (work/'.aigc-source.json').write_text(json.dumps({'repository':r['repository'],'commit':sha,'runtime_installed':False},indent=2))
  work.rename(dest)
 return dest

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['list','resolve','sync']);ap.add_argument('--family',default='all');ap.add_argument('--module');ap.add_argument('--cache',type=Path,default=ROOT/'.integrations/sources');args=ap.parse_args()
 repos=[r for r in records() if args.family=='all' or r['family']==args.family]
 if not repos:ap.error('Unknown family')
 if args.action=='resolve' and not args.module:ap.error('resolve requires --module')
 found=False
 for r in repos:
  dest=sync(r,args.cache) if args.action=='sync' else source_dir(args.cache,r)
  for m in r['modules']:
   if args.module and m['name']!=args.module:continue
   found=True;entry=dest/m['entrypoint']
   print(json.dumps({'family':r['family'],'module':m['name'],'entrypoint':str(entry),'available':entry.is_file(),'source':f"https://github.com/{r['repository']}/blob/{r['commit']}/{m['entrypoint']}",'license':r['license_spdx'],'runtime_state':'not_verified'},ensure_ascii=False))
 if not found:ap.error('Unknown module; use list')
if __name__=='__main__':main()
